"""The BlowControl integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_DEVICE_ID,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Platform to be used for this integration
PLATFORMS: list[Platform] = [Platform.FAN, Platform.BINARY_SENSOR, Platform.SENSOR]

# Configuration schema for the integration
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_DEVICE_ID): cv.string,
            }
        )
    }
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BlowControl from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Clean up coordinator if it exists
        if "coordinator" in hass.data[DOMAIN]:
            await hass.data[DOMAIN]["coordinator"].async_close()
            hass.data[DOMAIN].pop("coordinator")
        
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the BlowControl component."""
    hass.data.setdefault(DOMAIN, {})
    
    return True
