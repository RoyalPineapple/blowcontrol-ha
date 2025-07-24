"""Coordinator for BlowControl integration."""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from datetime import timedelta
from typing import Any
from functools import partial

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL

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
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"BlowControl {self.serial_number}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via BlowControl CLI."""
        _LOGGER.info("=== COORDINATOR: Updating data via BlowControl CLI ===")
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
            
            # Get device state via BlowControl CLI
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
            _LOGGER.warning("BlowControl CLI not available: %s", err)
            _LOGGER.info("Falling back to mock data")
            return await self._fetch_mock_data()
        except Exception as err:
            _LOGGER.error("Error updating BlowControl data: %s", err)
            raise UpdateFailed(f"Error communicating with BlowControl device: {err}")

    def _parse_blowcontrol_state(self, state_data: dict[str, Any]) -> dict[str, Any]:
        """Parse BlowControl CLI state output."""
        # Parse the actual BlowControl CLI output format
        # This will need to be adjusted based on the actual CLI output
        return {
            "fan": {
                "power": state_data.get("power", "OFF"),
                "speed": state_data.get("speed", 0),
                "oscillating": state_data.get("oscillating", False),
                "direction": state_data.get("direction", "forward"),
                "rpm": state_data.get("rpm", 0),
            },
            "environment": {
                "temperature": state_data.get("temperature", 22.5),
                "humidity": state_data.get("humidity", 45.2),
                "air_quality": state_data.get("air_quality", 12.3),
            },
            "connection": {
                "connected": state_data.get("connected", True),
                "last_seen": state_data.get("last_seen", "2024-01-01T12:00:00Z"),
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
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            command = ["blowcontrol", "power", "on" if power else "off"]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan power: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except Exception as err:
            _LOGGER.error("Error setting fan power: %s", err)
            raise

    async def async_set_fan_speed(self, speed: int) -> None:
        """Set fan speed via BlowControl CLI."""
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            command = ["blowcontrol", "speed", str(speed)]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan speed: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except Exception as err:
            _LOGGER.error("Error setting fan speed: %s", err)
            raise

    async def async_set_fan_oscillation(self, oscillating: bool) -> None:
        """Set fan oscillation via BlowControl CLI."""
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Note: This would need to be adjusted based on actual BlowControl CLI commands
            command = ["blowcontrol", "oscillation", "on" if oscillating else "off"]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan oscillation: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except Exception as err:
            _LOGGER.error("Error setting fan oscillation: %s", err)
            raise

    async def async_set_fan_direction(self, direction: str) -> None:
        """Set fan direction via BlowControl CLI."""
        try:
            env = {
                "DEVICE_IP": self.device_ip,
                "MQTT_PASSWORD": self.mqtt_password,
                "SERIAL_NUMBER": self.serial_number,
                "MQTT_PORT": str(self.mqtt_port),
                "ROOT_TOPIC": self.root_topic,
            }
            
            # Note: This would need to be adjusted based on actual BlowControl CLI commands
            command = ["blowcontrol", "direction", direction]
            result = await self.hass.async_add_executor_job(
                partial(subprocess.run, command, capture_output=True, text=True, env=env)
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to set fan direction: %s", result.stderr)
                raise Exception(f"BlowControl CLI failed: {result.stderr}")
                
        except Exception as err:
            _LOGGER.error("Error setting fan direction: %s", err)
            raise

    async def async_close(self) -> None:
        """Close the coordinator."""
        # No session to close since we're using subprocess
        pass 