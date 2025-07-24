"""Platform for BlowControl fan integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    CONF_HOST,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    FAN_SPEED_NAMES,
    FAN_SPEED_PERCENTAGES,
    FAN_SPEED_OFF,
    FAN_SPEED_LOW,
    FAN_SPEED_MEDIUM,
    FAN_SPEED_HIGH,
    FAN_SPEED_MAX,
    STATE_OFF,
    STATE_ON,
)
from .coordinator import BlowControlCoordinator

_LOGGER = logging.getLogger(__name__)

# Speed range for the fan
SPEED_RANGE = (FAN_SPEED_OFF, FAN_SPEED_MAX)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BlowControl fan platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    host = config[CONF_HOST]
    name = config.get(CONF_NAME, DEFAULT_NAME)
    
    # Get or create coordinator
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        coordinator = BlowControlCoordinator(hass, host)
        hass.data[DOMAIN]["coordinator"] = coordinator
    
    async_add_entities([BlowControlFan(coordinator, name, config_entry.entry_id)])

class BlowControlFan(FanEntity):
    """Representation of a BlowControl fan."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the fan."""
        self.coordinator = coordinator
        self._name = name
        self._entry_id = entry_id
        self._state = STATE_OFF
        self._speed = FAN_SPEED_OFF
        self._oscillating = False
        self._percentage = 0

    @property
    def name(self) -> str:
        """Return the name of the fan."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if the entity is on."""
        return self._state == STATE_ON

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self._percentage

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(FAN_SPEED_NAMES)

    @property
    def oscillating(self) -> bool | None:
        """Return whether the fan is oscillating."""
        return self._oscillating

    @property
    def supported_features(self) -> FanEntityFeature:
        """Flag supported features."""
        return (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.DIRECTION
        )

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            # Turn on at last known speed or low speed
            speed = self._speed if self._speed > FAN_SPEED_OFF else FAN_SPEED_LOW
            await self._async_set_speed(speed)
        
        await self.coordinator.async_set_fan_power(True)
        self._state = STATE_ON
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.coordinator.async_set_fan_power(False)
        await self._async_set_speed(FAN_SPEED_OFF)
        self._state = STATE_OFF
        self._percentage = 0
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return

        speed = percentage_to_ranged_value(SPEED_RANGE, percentage)
        await self._async_set_speed(speed)
        self._percentage = percentage
        self._state = STATE_ON
        self.async_write_ha_state()

    async def async_set_oscillating(self, oscillating: bool) -> None:
        """Set oscillation."""
        await self.coordinator.async_set_fan_oscillation(oscillating)
        self._oscillating = oscillating
        self.async_write_ha_state()

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        await self.coordinator.async_set_fan_direction(direction)
        self.async_write_ha_state()

    async def _async_set_speed(self, speed: int) -> None:
        """Set the speed of the fan."""
        await self.coordinator.async_set_fan_speed(speed)
        self._speed = speed
        self._percentage = ranged_value_to_percentage(SPEED_RANGE, speed)
        _LOGGER.info("Setting fan speed to %s (%s)", speed, FAN_SPEED_NAMES.get(speed, "Unknown"))

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_fan"

    def update_from_coordinator(self, data: dict[str, Any]) -> None:
        """Update the fan state from coordinator data."""
        if data and "fan" in data:
            fan_data = data["fan"]
            self._state = STATE_ON if fan_data.get("power") == "ON" else STATE_OFF
            self._speed = fan_data.get("speed", FAN_SPEED_OFF)
            self._oscillating = fan_data.get("oscillating", False)
            self._percentage = ranged_value_to_percentage(SPEED_RANGE, self._speed)
