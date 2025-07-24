"""Test the BlowControl binary sensor platform."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.blowcontrol.binary_sensor import (
    BlowControlPowerSensor,
    BlowControlConnectionSensor,
)
from custom_components.blowcontrol.coordinator import BlowControlCoordinator


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = AsyncMock()
    coordinator.data = {
        "fan": {
            "power": "OFF",
        },
        "connection": {
            "connected": True,
        }
    }
    coordinator.last_update_success = True
    return coordinator


@pytest.fixture
def power_sensor(mock_coordinator):
    """Create a power sensor for testing."""
    return BlowControlPowerSensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.fixture
def connection_sensor(mock_coordinator):
    """Create a connection sensor for testing."""
    return BlowControlConnectionSensor(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.mark.asyncio
async def test_power_sensor_initialization(power_sensor):
    """Test power sensor initialization."""
    assert power_sensor.name == "Test Fan Power"
    assert power_sensor.unique_id == "test_entry_id_power"
    assert not power_sensor.is_on
    assert power_sensor.device_class.value == "power"


@pytest.mark.asyncio
async def test_connection_sensor_initialization(connection_sensor):
    """Test connection sensor initialization."""
    assert connection_sensor.name == "Test Fan Connected"
    assert connection_sensor.unique_id == "test_entry_id_connected"
    assert connection_sensor.is_on  # Initially True
    assert connection_sensor.device_class.value == "connectivity"


@pytest.mark.asyncio
async def test_power_sensor_update_from_coordinator_on(power_sensor):
    """Test power sensor update when fan is on."""
    test_data = {
        "fan": {
            "power": "ON",
        }
    }
    
    power_sensor.update_from_coordinator(test_data)
    
    assert power_sensor.is_on


@pytest.mark.asyncio
async def test_power_sensor_update_from_coordinator_off(power_sensor):
    """Test power sensor update when fan is off."""
    test_data = {
        "fan": {
            "power": "OFF",
        }
    }
    
    power_sensor.update_from_coordinator(test_data)
    
    assert not power_sensor.is_on


@pytest.mark.asyncio
async def test_power_sensor_update_from_coordinator_missing_data(power_sensor):
    """Test power sensor update with missing data."""
    test_data = {}
    
    power_sensor.update_from_coordinator(test_data)
    
    # Should remain unchanged
    assert not power_sensor.is_on


@pytest.mark.asyncio
async def test_connection_sensor_update_from_coordinator_connected(connection_sensor):
    """Test connection sensor update when connected."""
    test_data = {
        "connection": {
            "connected": True,
        }
    }
    
    connection_sensor.update_from_coordinator(test_data)
    
    assert connection_sensor.is_on


@pytest.mark.asyncio
async def test_connection_sensor_update_from_coordinator_disconnected(connection_sensor):
    """Test connection sensor update when disconnected."""
    test_data = {
        "connection": {
            "connected": False,
        }
    }
    
    connection_sensor.update_from_coordinator(test_data)
    
    assert not connection_sensor.is_on


@pytest.mark.asyncio
async def test_connection_sensor_update_from_coordinator_missing_data(connection_sensor):
    """Test connection sensor update with missing data."""
    test_data = {}
    
    connection_sensor.update_from_coordinator(test_data)
    
    # Should remain unchanged (initially True)
    assert connection_sensor.is_on


@pytest.mark.asyncio
async def test_power_sensor_update_state(power_sensor):
    """Test power sensor manual state update."""
    power_sensor.update_state(True)
    assert power_sensor.is_on
    
    power_sensor.update_state(False)
    assert not power_sensor.is_on


@pytest.mark.asyncio
async def test_connection_sensor_update_state(connection_sensor):
    """Test connection sensor manual state update."""
    connection_sensor.update_state(False)
    assert not connection_sensor.is_on
    
    connection_sensor.update_state(True)
    assert connection_sensor.is_on


@pytest.mark.asyncio
async def test_power_sensor_edge_cases(power_sensor):
    """Test power sensor edge cases."""
    # Test with None data
    power_sensor.update_from_coordinator(None)
    assert not power_sensor.is_on
    
    # Test with malformed data
    test_data = {
        "fan": {
            "power": "UNKNOWN",
        }
    }
    power_sensor.update_from_coordinator(test_data)
    assert not power_sensor.is_on


@pytest.mark.asyncio
async def test_connection_sensor_edge_cases(connection_sensor):
    """Test connection sensor edge cases."""
    # Test with None data
    connection_sensor.update_from_coordinator(None)
    assert connection_sensor.is_on  # Should remain True
    
    # Test with malformed data
    test_data = {
        "connection": {
            "connected": "UNKNOWN",
        }
    }
    connection_sensor.update_from_coordinator(test_data)
    assert connection_sensor.is_on  # Should remain True


@pytest.mark.asyncio
async def test_binary_sensor_properties(power_sensor, connection_sensor):
    """Test binary sensor properties."""
    # Power sensor properties
    assert power_sensor.name == "Test Fan Power"
    assert power_sensor.unique_id == "test_entry_id_power"
    assert power_sensor.device_class.value == "power"
    
    # Connection sensor properties
    assert connection_sensor.name == "Test Fan Connected"
    assert connection_sensor.unique_id == "test_entry_id_connected"
    assert connection_sensor.device_class.value == "connectivity" 