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
        if user_input is not None:
            # Check if user wants to use OpenDyson or manual entry
            if user_input.get("use_opendyson", True):
                return await self.async_step_opendyson_setup()
            else:
                return await self.async_step_manual_credentials()

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
        if user_input is not None:
            # Check if OpenDyson is installed
            if not await self._check_opendyson_installed():
                return await self.async_step_opendyson_install()
            
            return await self.async_step_opendyson_login()

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
        if user_input is not None:
            # Try to install OpenDyson
            if await self._install_opendyson():
                return await self.async_step_opendyson_login()
            else:
                return await self.async_step_manual_credentials()

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
        if user_input is not None:
            email = user_input.get("email")
            password = user_input.get("password")
            
            # Try to login with OpenDyson
            credentials = await self._opendyson_login(email, password)
            if credentials:
                self.opendyson_credentials = credentials
                return await self.async_step_device_selection()
            else:
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
        if user_input is not None:
            selected_device = user_input.get("device")
            if selected_device:
                # Parse device info and store it
                device_info = self._parse_device_info(selected_device)
                self.device_data.update(device_info)
                return await self.async_step_final_config()
            else:
                return await self.async_step_manual_credentials()

        # Get list of devices from OpenDyson
        devices = await self._get_opendyson_devices()
        if not devices:
            return await self.async_step_manual_credentials()

        device_options = {device["serial"]: f"{device['name']} ({device['serial']})" for device in devices}

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
        if user_input is not None:
            # Validate manual credentials
            if self._validate_manual_credentials(user_input):
                self.device_data.update(user_input)
                return await self.async_step_final_config()
            else:
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
        if user_input is not None:
            name = user_input.get("name", DEFAULT_NAME)
            
            # Create unique ID based on serial number
            await self.async_set_unique_id(self.device_data["serial_number"])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=name,
                data={
                    "name": name,
                    **self.device_data,
                },
            )

        return self.async_show_form(
            step_id="final_config",
            data_schema=vol.Schema(
                {
                    vol.Optional("name", default=DEFAULT_NAME): str,
                }
            ),
            description_placeholders={
                "final_info": f"Device: {self.device_data.get('name', 'Unknown')} ({self.device_data.get('serial_number', 'Unknown')})"
            }
        )

    async def _check_opendyson_installed(self) -> bool:
        """Check if OpenDyson is installed."""
        try:
            result = await self.hass.async_add_executor_job(
                subprocess.run, ["opendyson", "--version"], 
                {"capture_output": True, "text": True}
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def _install_opendyson(self) -> bool:
        """Try to install OpenDyson."""
        try:
            # Try to install via go install
            result = await self.hass.async_add_executor_job(
                subprocess.run, ["go", "install", "github.com/libdyson-wg/opendyson@latest"],
                {"capture_output": True, "text": True}
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def _opendyson_login(self, email: str, password: str) -> dict | None:
        """Login to OpenDyson and get credentials."""
        try:
            # Run opendyson login
            result = await self.hass.async_add_executor_job(
                subprocess.run, 
                ["opendyson", "login", "--email", email, "--password", password],
                {"capture_output": True, "text": True}
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    async def _get_opendyson_devices(self) -> list:
        """Get list of devices from OpenDyson."""
        try:
            result = await self.hass.async_add_executor_job(
                subprocess.run, ["opendyson", "devices", "--json"],
                {"capture_output": True, "text": True}
            )
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            return []
        except (subprocess.SubprocessError, FileNotFoundError, ValueError):
            return []

    def _parse_device_info(self, device_serial: str) -> dict:
        """Parse device information from OpenDyson output."""
        # This would parse the actual device info from OpenDyson
        # For now, return basic structure
        return {
            "serial_number": device_serial,
            "device_ip": "192.168.1.100",  # Would be extracted from device info
            "mqtt_password": self.opendyson_credentials.get("mqtt_password", ""),
            "mqtt_port": 1883,
            "root_topic": "438M",
        }

    def _validate_manual_credentials(self, credentials: dict) -> bool:
        """Validate manually entered credentials."""
        required_fields = ["device_ip", "mqtt_password", "serial_number"]
        return all(credentials.get(field) for field in required_fields)

    def _is_valid_host(self, host: str) -> bool:
        """Validate host format."""
        if not host:
            return False
        
        # Basic IP address validation
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return bool(re.match(ip_pattern, host) or re.match(hostname_pattern, host)) 