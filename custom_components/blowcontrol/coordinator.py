"""Coordinator for BlowControl integration."""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import shutil
from datetime import timedelta
from typing import Any
from functools import partial

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, BLOWCONTROL_SPEED_MAPPING

_LOGGER = logging.getLogger(__name__)

class BlowControlCoordinator(DataUpdateCoordinator):
    """Class to manage fetching BlowControl data."""

    def __init__(self, hass: HomeAssistant, device_config: dict[str, Any]) -> None:
        """Initialize."""
        self.hass = hass
        self.device_config = device_config
        self.device_ip = device_config.get("device_ip", "192.168.1.100")
        self.mqtt_password = device_config.get("mqtt_password", "")
        self.serial_number = device_config.get("serial_number", "")
        self.mqtt_port = device_config.get("mqtt_port", 1883)
        self.root_topic = device_config.get("root_topic", "438M")
        self._cli_available = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"BlowControl {self.serial_number}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _check_cli_available(self) -> bool:
        """Check if blowcontrol CLI is available."""
        if self._cli_available is not None:
            return self._cli_available
            
        try:
            # Check if blowcontrol command exists
            result = await self.hass.async_add_executor_job(
                partial(shutil.which, "blowcontrol")
            )
            self._cli_available = result is not None
            if not self._cli_available:
                _LOGGER.info("BlowControl CLI not found in PATH. Using mock data for testing. Install BlowControl CLI for full device control.")
            return self._cli_available
        except Exception as e:
            _LOGGER.error("Error checking for BlowControl CLI: %s", e)
            self._cli_available = False
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via BlowControl CLI."""
        _LOGGER.info("=== COORDINATOR: Updating data via BlowControl CLI ===")
        
        # Check if CLI is available
        if not await self._check_cli_available():
            _LOGGER.info("Using mock data (CLI not available)")
            return await self._fetch_mock_data()
            
        try:
            # Set environment variables for BlowControl CLI
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            _LOGGER.info("Environment variables: %s", {k: "***" if k == "MQTT_PASSWORD" else v for k, v in env.items()})
            
            # Get device state via BlowControl CLI: blowcontrol state --json
            command = ["blowcontrol", "state", "--json"]
            _LOGGER.info("Running command: %s", " ".join(command))
            
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            _LOGGER.info("BlowControl CLI return code: %s", result.returncode)
            _LOGGER.info("BlowControl CLI stdout: %s", result.stdout)
            _LOGGER.info("BlowControl CLI stderr: %s", result.stderr)
            
            if result.returncode == 0:
                try:
                    state_data = json.loads(result.stdout)
                    _LOGGER.info("Parsed state data: %s", state_data)
                    return self._parse_blowcontrol_state(state_data)
                except json.JSONDecodeError as e:
                    _LOGGER.warning("Failed to parse BlowControl state JSON: %s", e)
                    _LOGGER.info("Falling back to mock data")
                    return await self._fetch_mock_data()
            else:
                _LOGGER.warning("BlowControl CLI failed: %s", result.stderr)
                _LOGGER.info("Falling back to mock data")
                return await self._fetch_mock_data()
                
        except (subprocess.SubprocessError, FileNotFoundError) as err:
            _LOGGER.info("BlowControl CLI not available: %s", err)
            _LOGGER.info("Falling back to mock data")
            return await self._fetch_mock_data()
        except Exception as err:
            _LOGGER.error("Error updating BlowControl data: %s", err)
            raise UpdateFailed(f"Error communicating with BlowControl device: {err}")

    def _parse_blowcontrol_state(self, state_data: dict[str, Any]) -> dict[str, Any]:
        """Parse BlowControl CLI state output."""
        # Parse the actual BlowControl CLI state structure
        # The state command returns: {"state": {...}, "environmental": {...}}
        
        device_state = state_data.get("state", {})
        environmental = state_data.get("environmental", {})
        
        # Extract fan state from device state
        fan_state = device_state.get("product-state", {})
        
        # Map BlowControl speed (0-10) back to our speed (0-4)
        blowcontrol_speed = int(fan_state.get("fnsp", ["0"])[1])
        mapped_speed = 0
        # Create reverse mapping from BlowControl speed to our speed
        reverse_mapping = {bc_speed: our_speed for our_speed, bc_speed in BLOWCONTROL_SPEED_MAPPING.items()}
        mapped_speed = reverse_mapping.get(blowcontrol_speed, 0)
        
        # Parse oscillation state
        oscillation_on = fan_state.get("oson", ["OFF"])[1] == "ON"
        oscillation_angles = {
            "lower": int(fan_state.get("osal", ["0000"])[1]),
            "upper": int(fan_state.get("osau", ["0000"])[1])
        }
        
        # Determine oscillation width from angles
        oscillation_width = 0
        if oscillation_on and oscillation_angles["upper"] > oscillation_angles["lower"]:
            oscillation_width = oscillation_angles["upper"] - oscillation_angles["lower"]
        
        return {
            "fan": {
                "power": fan_state.get("fpwr", ["OFF"])[1],
                "speed": mapped_speed,
                "oscillating": oscillation_width > 0,
                "direction": "forward",  # Default, could be enhanced with actual direction
                "rpm": mapped_speed * 300,  # Estimate RPM based on speed
            },
            "environment": {
                "temperature": environmental.get("tact", 22.5),
                "humidity": environmental.get("hact", 45.2),
                "air_quality": environmental.get("pm25", 12.3),
            },
            "connection": {
                "connected": True,  # If we got state, we're connected
                "last_seen": "2024-01-01T12:00:00Z",  # Could be enhanced with actual timestamp
            }
        }

    async def _fetch_mock_data(self) -> dict[str, Any]:
        """Fetch mock data for testing."""
        return {
            "fan": {
                "power": "ON",
                "speed": 2,
                "oscillating": False,
                "direction": "forward",
                "rpm": 1200,
            },
            "environment": {
                "temperature": 22.5,
                "humidity": 45.2,
                "air_quality": 12.3,
            },
            "connection": {
                "connected": True,
                "last_seen": "2024-01-01T12:00:00Z",
            }
        }

    async def async_set_fan_power(self, power: bool) -> None:
        """Set fan power state via BlowControl CLI."""
        if not await self._check_cli_available():
            _LOGGER.info("Fan power control: Using mock mode (BlowControl CLI not installed)")
            return
            
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Use actual BlowControl CLI command: blowcontrol power on/off
            command = ["blowcontrol", "power", "on" if power else "off"]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan power: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except FileNotFoundError:
            _LOGGER.info("BlowControl CLI not found. Using mock mode for testing. Install BlowControl CLI for full device control.")
            return
        except Exception as err:
            _LOGGER.error("Error setting fan power: %s", err)
            return

    async def async_set_fan_speed(self, speed: int) -> None:
        """Set fan speed via BlowControl CLI."""
        if not await self._check_cli_available():
            _LOGGER.info("Fan speed control: Using mock mode (BlowControl CLI not installed)")
            return
            
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Use actual BlowControl CLI command: blowcontrol speed <0-10>
            # Note: BlowControl uses 0-10 range, we map our 0-4 to 0-10
            mapped_speed = BLOWCONTROL_SPEED_MAPPING.get(speed, 0)
            command = ["blowcontrol", "speed", str(mapped_speed)]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan speed: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except FileNotFoundError:
            _LOGGER.info("BlowControl CLI not found. Using mock mode for testing. Install BlowControl CLI for full device control.")
            return
        except Exception as err:
            _LOGGER.error("Error setting fan speed: %s", err)
            return

    async def async_set_fan_oscillation(self, oscillating: bool) -> None:
        """Set fan oscillation via BlowControl CLI."""
        if not await self._check_cli_available():
            _LOGGER.info("Fan oscillation control: Using mock mode (BlowControl CLI not installed)")
            return
            
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Use actual BlowControl CLI command: blowcontrol width <width>
            # 0 = no oscillation, 90 = medium, 180 = wide
            width = "180" if oscillating else "0"
            command = ["blowcontrol", "width", width]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan oscillation: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except FileNotFoundError:
            _LOGGER.info("BlowControl CLI not found. Using mock mode for testing. Install BlowControl CLI for full device control.")
            return
        except Exception as err:
            _LOGGER.error("Error setting fan oscillation: %s", err)
            return

    async def async_set_fan_direction(self, direction: str) -> None:
        """Set fan direction via BlowControl CLI."""
        if not await self._check_cli_available():
            _LOGGER.info("Fan direction control: Using mock mode (BlowControl CLI not installed)")
            return
            
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Use actual BlowControl CLI command: blowcontrol direction <degrees>
            # Map "forward" to 180°, "reverse" to 0°
            degrees = "180" if direction == "forward" else "0"
            command = ["blowcontrol", "direction", degrees]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan direction: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except FileNotFoundError:
            _LOGGER.info("BlowControl CLI not found. Using mock mode for testing. Install BlowControl CLI for full device control.")
            return
        except Exception as err:
            _LOGGER.error("Error setting fan direction: %s", err)
            return

    async def async_close(self) -> None:
        """Close the coordinator."""
        # No session to close since we're using subprocess
        pass 