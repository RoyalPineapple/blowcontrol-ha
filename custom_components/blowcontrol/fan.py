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
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    DEFAULT_NAME,
    DOMAIN,
    FAN_SPEED_NAMES,
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
    
    name = config.get("name", DEFAULT_NAME)
    
    # Get or create coordinator
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        coordinator = BlowControlCoordinator(hass, config)
        hass.data[DOMAIN]["coordinator"] = coordinator
    
    # Create fan entity
    fan = BlowControlFan(coordinator, name, config_entry.entry_id)
    
    # Add coordinator listener
    coordinator.async_add_listener(fan.update_from_coordinator)
    
    async_add_entities([fan])

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
        self._direction = "forward"
        
        # Update state from coordinator data
        if self.coordinator.data:
            self.update_from_coordinator()

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
    def current_direction(self) -> str | None:
        """Return the current direction of the fan."""
        return self._direction

    @property
    def supported_features(self) -> FanEntityFeature:
        """Flag supported features."""
        return (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.DIRECTION
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        try:
            if percentage is not None:
                await self.async_set_percentage(percentage)
            else:
                # Turn on at last known speed or low speed
                speed = self._speed if self._speed > FAN_SPEED_OFF else FAN_SPEED_LOW
                await self._async_set_speed(speed)
            
            await self.coordinator.async_set_fan_power(True)
            self._state = STATE_ON
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to turn on fan: %s", e)
            # Still update state even if CLI fails
            self._state = STATE_ON
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        try:
            await self.coordinator.async_set_fan_power(False)
            await self._async_set_speed(FAN_SPEED_OFF)
        except Exception as e:
            _LOGGER.error("Failed to turn off fan: %s", e)
        
        self._state = STATE_OFF
        self._percentage = 0
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return

        try:
            speed = percentage_to_ranged_value(SPEED_RANGE, percentage)
            await self._async_set_speed(speed)
            self._percentage = percentage
            self._state = STATE_ON
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set fan percentage: %s", e)
            # Still update state even if CLI fails
            self._percentage = percentage
            self._state = STATE_ON
            self.async_write_ha_state()

    async def async_set_oscillating(self, oscillating: bool) -> None:
        """Set oscillation."""
        try:
            await self.coordinator.async_set_fan_oscillation(oscillating)
        except Exception as e:
            _LOGGER.error("Failed to set fan oscillation: %s", e)
        
        self._oscillating = oscillating
        self.async_write_ha_state()

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        try:
            await self.coordinator.async_set_fan_direction(direction)
        except Exception as e:
            _LOGGER.error("Failed to set fan direction: %s", e)
        
        self._direction = direction
        self.async_write_ha_state()

    async def _async_set_speed(self, speed: int) -> None:
        """Set the speed of the fan."""
        try:
            await self.coordinator.async_set_fan_speed(speed)
            self._speed = speed
            self._percentage = ranged_value_to_percentage(SPEED_RANGE, speed)
            _LOGGER.info("Setting fan speed to %s (%s)", speed, FAN_SPEED_NAMES.get(speed, "Unknown"))
        except Exception as e:
            _LOGGER.error("Failed to set fan speed: %s", e)
            # Still update state even if CLI fails
            self._speed = speed
            self._percentage = ranged_value_to_percentage(SPEED_RANGE, speed)

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_fan"

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    def update_from_coordinator(self) -> None:
        """Update the fan state from coordinator data."""
        data = self.coordinator.data
        if data and "fan" in data:
            fan_data = data["fan"]
            self._state = STATE_ON if fan_data.get("power") == "ON" else STATE_OFF
            self._speed = fan_data.get("speed", FAN_SPEED_OFF)
            self._oscillating = fan_data.get("oscillating", False)
            self._direction = fan_data.get("direction", "forward")
            self._percentage = ranged_value_to_percentage(SPEED_RANGE, self._speed)
            self.async_write_ha_state()
