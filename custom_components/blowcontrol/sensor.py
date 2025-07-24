"""Platform for BlowControl sensor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_NAME,
    DOMAIN,
)
from .coordinator import BlowControlCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BlowControl sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    # device_ip = config["device_ip"]  # Use device_ip instead of host
    name = config.get("name", DEFAULT_NAME)
    
    # Get or create coordinator
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator is None:
        coordinator = BlowControlCoordinator(hass, config)  # Pass config instead of host
        hass.data[DOMAIN]["coordinator"] = coordinator
    
    # Create entities
    temp_sensor = BlowControlTemperatureSensor(coordinator, name, config_entry.entry_id)
    humidity_sensor = BlowControlHumiditySensor(coordinator, name, config_entry.entry_id)
    air_quality_sensor = BlowControlAirQualitySensor(coordinator, name, config_entry.entry_id)
    fan_speed_sensor = BlowControlFanSpeedSensor(coordinator, name, config_entry.entry_id)
    
    # Add coordinator listeners
    coordinator.async_add_listener(temp_sensor.update_from_coordinator)
    coordinator.async_add_listener(humidity_sensor.update_from_coordinator)
    coordinator.async_add_listener(air_quality_sensor.update_from_coordinator)
    coordinator.async_add_listener(fan_speed_sensor.update_from_coordinator)
    
    async_add_entities([temp_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor])

class BlowControlTemperatureSensor(SensorEntity):
    """Representation of a BlowControl temperature sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the temperature sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Temperature"
        self._entry_id = entry_id
        self._state = None
        self._unit_of_measurement = "°C"  # Use string for Celsius

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_temperature"

    def update_state(self, temperature: float) -> None:
        """Update the temperature state."""
        self._state = temperature
        self.async_write_ha_state()

    def update_from_coordinator(self) -> None:
        """Update the sensor state from coordinator data."""
        data = self.coordinator.data
        if data and "environment" in data:
            env_data = data["environment"]
            self._state = env_data.get("temperature")

class BlowControlHumiditySensor(SensorEntity):
    """Representation of a BlowControl humidity sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the humidity sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Humidity"
        self._entry_id = entry_id
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_humidity"

    def update_state(self, humidity: float) -> None:
        """Update the humidity state."""
        self._state = humidity
        self.async_write_ha_state()

    def update_from_coordinator(self) -> None:
        data = self.coordinator.data
        if data and "environment" in data:
            env_data = data["environment"]
            self._state = env_data.get("humidity")

class BlowControlAirQualitySensor(SensorEntity):
    """Representation of a BlowControl air quality sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the air quality sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Air Quality"
        self._entry_id = entry_id
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "µg/m³"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.PM25

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_air_quality"

    def update_state(self, air_quality: float) -> None:
        """Update the air quality state."""
        self._state = air_quality
        self.async_write_ha_state()

    def update_from_coordinator(self) -> None:
        data = self.coordinator.data
        if data and "environment" in data:
            env_data = data["environment"]
            self._state = env_data.get("air_quality")

class BlowControlFanSpeedSensor(SensorEntity):
    """Representation of a BlowControl fan speed sensor."""

    def __init__(self, coordinator: BlowControlCoordinator, name: str, entry_id: str) -> None:
        """Initialize the fan speed sensor."""
        self.coordinator = coordinator
        self._name = f"{name} Fan Speed"
        self._entry_id = entry_id
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> int | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "RPM"

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID for this device."""
        return f"{self._entry_id}_fan_speed"

    def update_state(self, speed: int) -> None:
        """Update the fan speed state."""
        self._state = speed
        self.async_write_ha_state()

    def update_from_coordinator(self) -> None:
        data = self.coordinator.data
        if data and "fan" in data:
            fan_data = data["fan"]
            self._state = fan_data.get("rpm")
