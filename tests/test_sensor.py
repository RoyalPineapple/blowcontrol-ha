"""Test the BlowControl sensor platform."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.blowcontrol.sensor import (
    BlowControlTemperatureSensor,
    BlowControlHumiditySensor,
    BlowControlAirQualitySensor,
    BlowControlFanSpeedSensor,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = AsyncMock()
    coordinator.data = {
        "environment": {
            "temperature": 22.5,
            "humidity": 45.2,
            "air_quality": 12.3,
        },
        "fan": {
            "rpm": 1200,
        }
    }
    coordinator.last_update_success = True
    return coordinator


@pytest.fixture
def temperature_sensor(mock_coordinator):
    """Create a temperature sensor for testing."""
    return BlowControlTemperatureSensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.fixture
def humidity_sensor(mock_coordinator):
    """Create a humidity sensor for testing."""
    return BlowControlHumiditySensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.fixture
def air_quality_sensor(mock_coordinator):
    """Create an air quality sensor for testing."""
    return BlowControlAirQualitySensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.fixture
def fan_speed_sensor(mock_coordinator):
    """Create a fan speed sensor for testing."""
    return BlowControlFanSpeedSensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.mark.asyncio
async def test_temperature_sensor_initialization(temperature_sensor):
    """Test temperature sensor initialization."""
    assert temperature_sensor.name == "Test Fan Temperature"
    assert temperature_sensor.unique_id == "test_entry_id_temperature"
    assert temperature_sensor.state == 22.5
    assert temperature_sensor.unit_of_measurement == "°C"
    assert temperature_sensor.device_class.value == "temperature"
    assert temperature_sensor.state_class.value == "measurement"


@pytest.mark.asyncio
async def test_humidity_sensor_initialization(humidity_sensor):
    """Test humidity sensor initialization."""
    assert humidity_sensor.name == "Test Fan Humidity"
    assert humidity_sensor.unique_id == "test_entry_id_humidity"
    assert humidity_sensor.state == 45.2
    assert humidity_sensor.unit_of_measurement == "%"
    assert humidity_sensor.device_class.value == "humidity"
    assert humidity_sensor.state_class.value == "measurement"


@pytest.mark.asyncio
async def test_air_quality_sensor_initialization(air_quality_sensor):
    """Test air quality sensor initialization."""
    assert air_quality_sensor.name == "Test Fan Air Quality"
    assert air_quality_sensor.unique_id == "test_entry_id_air_quality"
    assert air_quality_sensor.state == 12.3
    assert air_quality_sensor.unit_of_measurement == "µg/m³"
    assert air_quality_sensor.device_class.value == "pm25"
    assert air_quality_sensor.state_class.value == "measurement"


@pytest.mark.asyncio
async def test_fan_speed_sensor_initialization(fan_speed_sensor):
    """Test fan speed sensor initialization."""
    assert fan_speed_sensor.name == "Test Fan Fan Speed"
    assert fan_speed_sensor.unique_id == "test_entry_id_fan_speed"
    assert fan_speed_sensor.state == 1200
    assert fan_speed_sensor.unit_of_measurement == "RPM"
    assert fan_speed_sensor.state_class.value == "measurement"


@pytest.mark.asyncio
async def test_temperature_sensor_update_from_coordinator(temperature_sensor):
    """Test temperature sensor update from coordinator."""
    test_data = {
        "environment": {
            "temperature": 25.0,
        }
    }
    
    temperature_sensor.update_from_coordinator(test_data)
    
    assert temperature_sensor.state == 25.0


@pytest.mark.asyncio
async def test_humidity_sensor_update_from_coordinator(humidity_sensor):
    """Test humidity sensor update from coordinator."""
    test_data = {
        "environment": {
            "humidity": 60.0,
        }
    }
    
    humidity_sensor.update_from_coordinator(test_data)
    
    assert humidity_sensor.state == 60.0


@pytest.mark.asyncio
async def test_air_quality_sensor_update_from_coordinator(air_quality_sensor):
    """Test air quality sensor update from coordinator."""
    test_data = {
        "environment": {
            "air_quality": 15.0,
        }
    }
    
    air_quality_sensor.update_from_coordinator(test_data)
    
    assert air_quality_sensor.state == 15.0


@pytest.mark.asyncio
async def test_fan_speed_sensor_update_from_coordinator(fan_speed_sensor):
    """Test fan speed sensor update from coordinator."""
    test_data = {
        "fan": {
            "rpm": 1500,
        }
    }
    
    fan_speed_sensor.update_from_coordinator(test_data)
    
    assert fan_speed_sensor.state == 1500


@pytest.mark.asyncio
async def test_sensor_update_from_coordinator_missing_data(temperature_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor):
    """Test sensor updates with missing data."""
    test_data = {}
    
    # Store original values
    original_temp = temperature_sensor.state
    original_humidity = humidity_sensor.state
    original_air_quality = air_quality_sensor.state
    original_fan_speed = fan_speed_sensor.state
    
    # Update with empty data
    temperature_sensor.update_from_coordinator(test_data)
    humidity_sensor.update_from_coordinator(test_data)
    air_quality_sensor.update_from_coordinator(test_data)
    fan_speed_sensor.update_from_coordinator(test_data)
    
    # Should remain unchanged
    assert temperature_sensor.state == original_temp
    assert humidity_sensor.state == original_humidity
    assert air_quality_sensor.state == original_air_quality
    assert fan_speed_sensor.state == original_fan_speed


@pytest.mark.asyncio
async def test_sensor_update_from_coordinator_none_data(temperature_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor):
    """Test sensor updates with None data."""
    # Store original values
    original_temp = temperature_sensor.state
    original_humidity = humidity_sensor.state
    original_air_quality = air_quality_sensor.state
    original_fan_speed = fan_speed_sensor.state
    
    # Update with None data
    temperature_sensor.update_from_coordinator(None)
    humidity_sensor.update_from_coordinator(None)
    air_quality_sensor.update_from_coordinator(None)
    fan_speed_sensor.update_from_coordinator(None)
    
    # Should remain unchanged
    assert temperature_sensor.state == original_temp
    assert humidity_sensor.state == original_humidity
    assert air_quality_sensor.state == original_air_quality
    assert fan_speed_sensor.state == original_fan_speed


@pytest.mark.asyncio
async def test_sensor_manual_update_state(temperature_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor):
    """Test manual state updates."""
    # Temperature sensor
    temperature_sensor.update_state(30.0)
    assert temperature_sensor.state == 30.0
    
    # Humidity sensor
    humidity_sensor.update_state(70.0)
    assert humidity_sensor.state == 70.0
    
    # Air quality sensor
    air_quality_sensor.update_state(20.0)
    assert air_quality_sensor.state == 20.0
    
    # Fan speed sensor
    fan_speed_sensor.update_state(1800)
    assert fan_speed_sensor.state == 1800


@pytest.mark.asyncio
async def test_sensor_edge_cases(temperature_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor):
    """Test sensor edge cases."""
    # Test with zero values
    temperature_sensor.update_state(0.0)
    humidity_sensor.update_state(0.0)
    air_quality_sensor.update_state(0.0)
    fan_speed_sensor.update_state(0)
    
    assert temperature_sensor.state == 0.0
    assert humidity_sensor.state == 0.0
    assert air_quality_sensor.state == 0.0
    assert fan_speed_sensor.state == 0
    
    # Test with negative values (should be allowed)
    temperature_sensor.update_state(-5.0)
    humidity_sensor.update_state(-10.0)
    air_quality_sensor.update_state(-1.0)
    fan_speed_sensor.update_state(-100)
    
    assert temperature_sensor.state == -5.0
    assert humidity_sensor.state == -10.0
    assert air_quality_sensor.state == -1.0
    assert fan_speed_sensor.state == -100


@pytest.mark.asyncio
async def test_sensor_properties(temperature_sensor, humidity_sensor, air_quality_sensor, fan_speed_sensor):
    """Test sensor properties."""
    # Temperature sensor properties
    assert temperature_sensor.name == "Test Fan Temperature"
    assert temperature_sensor.unique_id == "test_entry_id_temperature"
    assert temperature_sensor.unit_of_measurement == "°C"
    assert temperature_sensor.device_class.value == "temperature"
    assert temperature_sensor.state_class.value == "measurement"
    
    # Humidity sensor properties
    assert humidity_sensor.name == "Test Fan Humidity"
    assert humidity_sensor.unique_id == "test_entry_id_humidity"
    assert humidity_sensor.unit_of_measurement == "%"
    assert humidity_sensor.device_class.value == "humidity"
    assert humidity_sensor.state_class.value == "measurement"
    
    # Air quality sensor properties
    assert air_quality_sensor.name == "Test Fan Air Quality"
    assert air_quality_sensor.unique_id == "test_entry_id_air_quality"
    assert air_quality_sensor.unit_of_measurement == "µg/m³"
    assert air_quality_sensor.device_class.value == "pm25"
    assert air_quality_sensor.state_class.value == "measurement"
    
    # Fan speed sensor properties
    assert fan_speed_sensor.name == "Test Fan Fan Speed"
    assert fan_speed_sensor.unique_id == "test_entry_id_fan_speed"
    assert fan_speed_sensor.unit_of_measurement == "RPM"
    assert fan_speed_sensor.state_class.value == "measurement" 