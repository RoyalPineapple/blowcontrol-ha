"""Config flow for BlowControl integration."""
from __future__ import annotations

import logging
import re
import subprocess
import sys
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BlowControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BlowControl."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.device_data = {}
        self.opendyson_credentials = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle the initial step."""
        _LOGGER.info("=== CONFIG FLOW: Starting user step ===")
        
        if user_input is not None:
            _LOGGER.info("User input received: %s", user_input)
            use_opendyson = user_input.get("use_opendyson", True)
            _LOGGER.info("User chose OpenDyson: %s", use_opendyson)
            
            # Check if user wants to use OpenDyson or manual entry
            if use_opendyson:
                _LOGGER.info("Proceeding to OpenDyson setup step")
                return await self.async_step_opendyson_setup()
            else:
                _LOGGER.info("Proceeding to manual credentials step")
                return await self.async_step_manual_credentials()

        _LOGGER.info("Showing initial user form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("use_opendyson", default=True): bool,
                }
            ),
            description_placeholders={
                "opendyson_info": "OpenDyson will help you automatically get your device credentials from Dyson's servers.",
                "manual_info": "You can manually enter credentials if you already have them from OpenDyson or other tools."
            }
        )

    async def async_step_opendyson_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle OpenDyson setup step."""
        _LOGGER.info("=== CONFIG FLOW: Starting OpenDyson setup step ===")
        
        if user_input is not None:
            _LOGGER.info("OpenDyson setup user input received: %s", user_input)
            
            # Check if OpenDyson is installed
            _LOGGER.info("Checking if OpenDyson is installed...")
            is_installed = await self._check_opendyson_installed()
            _LOGGER.info("OpenDyson installed: %s", is_installed)
            
            if not is_installed:
                _LOGGER.info("OpenDyson not installed, proceeding to install step")
                return await self.async_step_opendyson_install()
            
            _LOGGER.info("OpenDyson is installed, proceeding to login step")
            return await self.async_step_opendyson_login()

        _LOGGER.info("Showing OpenDyson setup form")
        return self.async_show_form(
            step_id="opendyson_setup",
            data_schema=vol.Schema({}),
            description_placeholders={
                "setup_info": "We'll help you install and configure OpenDyson to get your device credentials automatically."
            }
        )

    async def async_step_opendyson_install(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle OpenDyson installation step."""
        _LOGGER.info("=== CONFIG FLOW: Starting OpenDyson install step ===")
        
        if user_input is not None:
            _LOGGER.info("OpenDyson install user input received: %s", user_input)
            
            # Try to install OpenDyson
            _LOGGER.info("Attempting to install OpenDyson...")
            install_success = await self._install_opendyson()
            _LOGGER.info("OpenDyson installation result: %s", install_success)
            
            if install_success:
                _LOGGER.info("OpenDyson installed successfully, proceeding to login step")
                return await self.async_step_opendyson_login()
            else:
                _LOGGER.info("OpenDyson installation failed, proceeding to manual credentials")
                return await self.async_step_manual_credentials()

        _LOGGER.info("Showing OpenDyson install form")
        return self.async_show_form(
            step_id="opendyson_install",
            data_schema=vol.Schema({}),
            description_placeholders={
                "install_info": "OpenDyson needs to be installed to get your device credentials. We'll try to install it automatically, or you can install it manually and try again."
            }
        )

    async def async_step_opendyson_login(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle OpenDyson login step."""
        _LOGGER.info("=== CONFIG FLOW: Starting OpenDyson login step ===")
        
        if user_input is not None:
            _LOGGER.info("OpenDyson login user input received")
            email = user_input.get("email")
            password = user_input.get("password")
            _LOGGER.info("Email provided: %s", email)
            _LOGGER.info("Password provided: %s", "***" if password else "None")
            
            # Try to login with OpenDyson
            _LOGGER.info("Attempting OpenDyson login...")
            credentials = await self._opendyson_login(email, password)
            _LOGGER.info("OpenDyson login result: %s", "Success" if credentials else "Failed")
            
            if credentials:
                _LOGGER.info("Login successful, storing credentials")
                self.opendyson_credentials = credentials
                _LOGGER.info("Proceeding to device selection step")
                return await self.async_step_device_selection()
            else:
                _LOGGER.info("Login failed, showing error form")
                return self.async_show_form(
                    step_id="opendyson_login",
                    data_schema=vol.Schema(
                        {
                            vol.Required("email"): str,
                            vol.Required("password"): str,
                        }
                    ),
                    errors={"base": "login_failed"}
                )

        _LOGGER.info("Showing OpenDyson login form")
        return self.async_show_form(
            step_id="opendyson_login",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                }
            ),
            description_placeholders={
                "login_info": "Enter your Dyson account credentials to get your device information."
            }
        )

    async def async_step_device_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle device selection step."""
        _LOGGER.info("=== CONFIG FLOW: Starting device selection step ===")
        
        if user_input is not None:
            _LOGGER.info("Device selection user input received: %s", user_input)
            selected_device = user_input.get("device")
            _LOGGER.info("Selected device: %s", selected_device)
            
            if selected_device:
                _LOGGER.info("Device selected, parsing device info...")
                # Parse device info and store it
                device_info = self._parse_device_info(selected_device)
                _LOGGER.info("Parsed device info: %s", device_info)
                self.device_data.update(device_info)
                _LOGGER.info("Updated device data: %s", self.device_data)
                _LOGGER.info("Proceeding to final config step")
                return await self.async_step_final_config()
            else:
                _LOGGER.info("No device selected, proceeding to manual credentials")
                return await self.async_step_manual_credentials()

        # Get list of devices from OpenDyson
        _LOGGER.info("Fetching devices from OpenDyson...")
        devices = await self._get_opendyson_devices()
        _LOGGER.info("Found %d devices: %s", len(devices), devices)
        
        if not devices:
            _LOGGER.info("No devices found, proceeding to manual credentials")
            return await self.async_step_manual_credentials()

        device_options = {device["serial"]: f"{device['name']} ({device['serial']})" for device in devices}
        _LOGGER.info("Device options: %s", device_options)

        _LOGGER.info("Showing device selection form")
        return self.async_show_form(
            step_id="device_selection",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(device_options),
                }
            ),
            description_placeholders={
                "device_info": f"Found {len(devices)} device(s). Select the one you want to control:"
            }
        )

    async def async_step_manual_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle manual credential entry."""
        _LOGGER.info("=== CONFIG FLOW: Starting manual credentials step ===")
        
        if user_input is not None:
            _LOGGER.info("Manual credentials user input received")
            _LOGGER.info("Device IP: %s", user_input.get("device_ip"))
            _LOGGER.info("Serial Number: %s", user_input.get("serial_number"))
            _LOGGER.info("MQTT Password: %s", "***" if user_input.get("mqtt_password") else "None")
            _LOGGER.info("MQTT Port: %s", user_input.get("mqtt_port"))
            _LOGGER.info("Root Topic: %s", user_input.get("root_topic"))
            
            # Validate manual credentials
            _LOGGER.info("Validating manual credentials...")
            is_valid = self._validate_manual_credentials(user_input)
            _LOGGER.info("Credentials validation result: %s", is_valid)
            
            if is_valid:
                _LOGGER.info("Credentials valid, updating device data")
                self.device_data.update(user_input)
                _LOGGER.info("Updated device data: %s", self.device_data)
                _LOGGER.info("Proceeding to final config step")
                return await self.async_step_final_config()
            else:
                _LOGGER.info("Credentials invalid, showing error form")
                return self.async_show_form(
                    step_id="manual_credentials",
                    data_schema=vol.Schema(
                        {
                            vol.Required("device_ip"): str,
                            vol.Required("mqtt_password"): str,
                            vol.Required("serial_number"): str,
                            vol.Optional("mqtt_port", default=1883): int,
                            vol.Optional("root_topic", default="438M"): str,
                        }
                    ),
                    errors={"base": "invalid_credentials"}
                )

        _LOGGER.info("Showing manual credentials form")
        return self.async_show_form(
            step_id="manual_credentials",
            data_schema=vol.Schema(
                {
                    vol.Required("device_ip"): str,
                    vol.Required("mqtt_password"): str,
                    vol.Required("serial_number"): str,
                    vol.Optional("mqtt_port", default=1883): int,
                    vol.Optional("root_topic", default="438M"): str,
                }
            ),
            description_placeholders={
                "manual_info": "Enter your device credentials manually. You can get these from OpenDyson or other Dyson credential extraction tools."
            }
        )

    async def async_step_final_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResultType:
        """Handle final configuration step."""
        _LOGGER.info("=== CONFIG FLOW: Starting final config step ===")
        
        if user_input is not None:
            _LOGGER.info("Final config user input received: %s", user_input)
            name = user_input.get("name", DEFAULT_NAME)
            _LOGGER.info("Device name: %s", name)
            
            # Create unique ID based on serial number
            serial_number = self.device_data.get("serial_number", "unknown")
            _LOGGER.info("Setting unique ID to: %s", serial_number)
            await self.async_set_unique_id(serial_number)
            self._abort_if_unique_id_configured()
            
            final_data = {
                "name": name,
                **self.device_data,
            }
            _LOGGER.info("Final config data: %s", final_data)
            _LOGGER.info("=== CONFIG FLOW: Creating entry with title: %s ===", name)
            
            return self.async_create_entry(
                title=name,
                data=final_data,
            )

        device_name = self.device_data.get('name', 'Unknown')
        device_serial = self.device_data.get('serial_number', 'Unknown')
        _LOGGER.info("Showing final config form for device: %s (%s)", device_name, device_serial)
        
        return self.async_show_form(
            step_id="final_config",
            data_schema=vol.Schema(
                {
                    vol.Optional("name", default=DEFAULT_NAME): str,
                }
            ),
            description_placeholders={
                "final_info": f"Device: {device_name} ({device_serial})"
            }
        )

    async def _check_opendyson_installed(self) -> bool:
        """Check if OpenDyson is installed."""
        _LOGGER.info("=== DEBUG: Checking if OpenDyson is installed ===")
        try:
            _LOGGER.info("Running: opendyson --version")
            result = await self.hass.async_add_executor_job(
                subprocess.run, ["opendyson", "--version"], 
                {"capture_output": True, "text": True}
            )
            _LOGGER.info("OpenDyson version check return code: %s", result.returncode)
            _LOGGER.info("OpenDyson version check stdout: %s", result.stdout)
            _LOGGER.info("OpenDyson version check stderr: %s", result.stderr)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            _LOGGER.info("OpenDyson not found or error: %s", e)
            return False

    async def _install_opendyson(self) -> bool:
        """Try to install OpenDyson."""
        _LOGGER.info("=== DEBUG: Attempting to install OpenDyson ===")
        try:
            # Try to install via go install
            command = ["go", "install", "github.com/libdyson-wg/opendyson@latest"]
            _LOGGER.info("Running: %s", " ".join(command))
            result = await self.hass.async_add_executor_job(
                subprocess.run, command,
                {"capture_output": True, "text": True}
            )
            _LOGGER.info("OpenDyson install return code: %s", result.returncode)
            _LOGGER.info("OpenDyson install stdout: %s", result.stdout)
            _LOGGER.info("OpenDyson install stderr: %s", result.stderr)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            _LOGGER.info("OpenDyson install failed: %s", e)
            return False

    async def _opendyson_login(self, email: str, password: str) -> dict | None:
        """Login to OpenDyson and get credentials."""
        _LOGGER.info("=== DEBUG: Attempting OpenDyson login ===")
        try:
            # Run opendyson login
            command = ["opendyson", "login", "--email", email, "--password", password]
            _LOGGER.info("Running: opendyson login --email %s --password ***", email)
            result = await self.hass.async_add_executor_job(
                subprocess.run, command,
                {"capture_output": True, "text": True}
            )
            _LOGGER.info("OpenDyson login return code: %s", result.returncode)
            _LOGGER.info("OpenDyson login stdout: %s", result.stdout)
            _LOGGER.info("OpenDyson login stderr: %s", result.stderr)
            
            if result.returncode == 0:
                _LOGGER.info("OpenDyson login successful")
                # For now, return a mock credentials dict
                # In a real implementation, this would parse the actual credentials
                return {"mqtt_password": "mock_password", "serial_number": "mock_serial"}
            else:
                _LOGGER.info("OpenDyson login failed")
                return None
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            _LOGGER.info("OpenDyson login error: %s", e)
            return None

    async def _get_opendyson_devices(self) -> list:
        """Get list of devices from OpenDyson."""
        _LOGGER.info("=== DEBUG: Getting devices from OpenDyson ===")
        try:
            command = ["opendyson", "devices", "--json"]
            _LOGGER.info("Running: %s", " ".join(command))
            result = await self.hass.async_add_executor_job(
                subprocess.run, command,
                {"capture_output": True, "text": True}
            )
            _LOGGER.info("OpenDyson devices return code: %s", result.returncode)
            _LOGGER.info("OpenDyson devices stdout: %s", result.stdout)
            _LOGGER.info("OpenDyson devices stderr: %s", result.stderr)
            
            if result.returncode == 0:
                import json
                try:
                    devices = json.loads(result.stdout)
                    _LOGGER.info("Parsed devices: %s", devices)
                    return devices
                except json.JSONDecodeError as e:
                    _LOGGER.info("Failed to parse devices JSON: %s", e)
                    return []
            else:
                _LOGGER.info("OpenDyson devices command failed")
                return []
        except (subprocess.SubprocessError, FileNotFoundError, ValueError) as e:
            _LOGGER.info("OpenDyson devices error: %s", e)
            return []

    def _parse_device_info(self, device_serial: str) -> dict:
        """Parse device information from OpenDyson output."""
        _LOGGER.info("=== DEBUG: Parsing device info for serial: %s ===", device_serial)
        _LOGGER.info("OpenDyson credentials: %s", self.opendyson_credentials)
        
        # This would parse the actual device info from OpenDyson
        # For now, return basic structure
        device_info = {
            "serial_number": device_serial,
            "device_ip": "192.168.1.100",  # Would be extracted from device info
            "mqtt_password": self.opendyson_credentials.get("mqtt_password", ""),
            "mqtt_port": 1883,
            "root_topic": "438M",
        }
        _LOGGER.info("Parsed device info: %s", device_info)
        return device_info

    def _validate_manual_credentials(self, credentials: dict) -> bool:
        """Validate manually entered credentials."""
        _LOGGER.info("=== DEBUG: Validating manual credentials ===")
        _LOGGER.info("Credentials to validate: %s", {k: "***" if k == "mqtt_password" else v for k, v in credentials.items()})
        
        required_fields = ["device_ip", "mqtt_password", "serial_number"]
        _LOGGER.info("Required fields: %s", required_fields)
        
        for field in required_fields:
            value = credentials.get(field)
            _LOGGER.info("Field '%s': %s", field, "***" if field == "mqtt_password" else value)
            if not value:
                _LOGGER.info("Missing required field: %s", field)
                return False
        
        _LOGGER.info("All required fields present")
        return True

    def _is_valid_host(self, host: str) -> bool:
        """Validate host format."""
        if not host:
            return False
        
        # Basic IP address validation
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return bool(re.match(ip_pattern, host) or re.match(hostname_pattern, host)) 