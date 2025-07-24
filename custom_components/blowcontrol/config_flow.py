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
        """Handle the initial (and only) step: manual credential entry."""
        _LOGGER.info("=== CONFIG FLOW: Starting manual-only user step ===")
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
                _LOGGER.info("Credentials valid, proceeding to create entry")
                name = user_input.get("name", DEFAULT_NAME)
                serial_number = user_input.get("serial_number", "unknown")
                await self.async_set_unique_id(serial_number)
                self._abort_if_unique_id_configured()
                final_data = {
                    "name": name,
                    **user_input,
                }
                _LOGGER.info("Final config data: %s", final_data)
                return self.async_create_entry(
                    title=name,
                    data=final_data,
                )
            else:
                _LOGGER.info("Credentials invalid, showing error form")
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required("device_ip"): str,
                            vol.Required("mqtt_password"): str,
                            vol.Required("serial_number"): str,
                            vol.Optional("mqtt_port", default=1883): int,
                            vol.Optional("root_topic", default="438M"): str,
                            vol.Optional("name", default=DEFAULT_NAME): str,
                        }
                    ),
                    errors={"base": "invalid_credentials"}
                )

        _LOGGER.info("Showing manual credentials form (user step)")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("device_ip"): str,
                    vol.Required("mqtt_password"): str,
                    vol.Required("serial_number"): str,
                    vol.Optional("mqtt_port", default=1883): int,
                    vol.Optional("root_topic", default="438M"): str,
                    vol.Optional("name", default=DEFAULT_NAME): str,
                }
            ),
            description_placeholders={
                "manual_info": "Enter your device credentials manually. You can get these from OpenDyson or other Dyson credential extraction tools."
            }
        )

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