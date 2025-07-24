"""Config flow for BlowControl integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

class BlowControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BlowControl."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                host = user_input[CONF_HOST]
                name = user_input.get(CONF_NAME, DEFAULT_NAME)
                
                # Validate host format
                if not self._is_valid_host(host):
                    errors["base"] = "invalid_host"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema(
                            {
                                vol.Required(CONF_HOST, default=host): str,
                                vol.Optional(CONF_NAME, default=name): str,
                            }
                        ),
                        errors=errors,
                    )
                
                # Test connection (optional - can be removed if not needed)
                # await self._test_connection(host)
                
                # Create unique ID based on host
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

    def _is_valid_host(self, host: str) -> bool:
        """Validate host format."""
        import re
        # Basic IP address validation
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return bool(re.match(ip_pattern, host) or re.match(hostname_pattern, host)) 