"""Platform for BlowControl binary sensor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_HOST,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    STATE_OFF,
    STATE_ON,
)
from .coordinator import BlowControlCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BlowControl binary sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    host = config[CONF_HOST]
    name = config.get(CONF_NAME, DEFAULT_NAME)
    
    # Get or create coordinator
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        coordinator = BlowControlCoordinator(hass, host)
        hass.data[DOMAIN]["coordinator"] = coordinator
    
    async_add_entities([
        BlowControlPowerSensor(coordinator, name, config_entry.entry_id),
        BlowControlConnectionSensor(coordinator, name, config_entry.entry_id),
    ])

class BlowControlPowerSensor(BinarySensorEntity):
    """Representation of a BlowControl power sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the power sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Power"
        self._entry_id = entry_id
        self._state = False

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if the entity is on."""
        return self._state

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class of the sensor."""
        return BinarySensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_power"

    def update_state(self, is_on: bool) -> None:
        """Update the state of the sensor."""
        self._state = is_on
        self.async_write_ha_state()

    def update_from_coordinator(self, data: dict[str, Any]) -> None:
        """Update the sensor state from coordinator data."""
        if data and "fan" in data:
            fan_data = data["fan"]
            self._state = fan_data.get("power") == "ON"

class BlowControlConnectionSensor(BinarySensorEntity):
    """Representation of a BlowControl connection sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the connection sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Connected"
        self._entry_id = entry_id
        self._state = True  # Assume connected initially

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if the entity is connected."""
        return self._state

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class of the sensor."""
        return BinarySensorDeviceClass.CONNECTIVITY

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_connected"

    def update_state(self, is_connected: bool) -> None:
        """Update the connection state of the sensor."""
        self._state = is_connected
        self.async_write_ha_state()

    def update_from_coordinator(self, data: dict[str, Any]) -> None:
        """Update the sensor state from coordinator data."""
        if data and "connection" in data:
            connection_data = data["connection"]
            self._state = connection_data.get("connected", True)
