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
                # Validate the connection here
                # For now, we'll just accept the input
                host = user_input[CONF_HOST]
                name = user_input.get(CONF_NAME, DEFAULT_NAME)
                
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