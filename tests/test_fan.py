"""Test the BlowControl fan platform."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.blowcontrol.fan import BlowControlFan
from custom_components.blowcontrol.const import (
    FAN_SPEED_OFF,
    FAN_SPEED_LOW,
    STATE_OFF,
    STATE_ON,
)


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = AsyncMock()
    coordinator.data = {
        "fan": {
            "power": "OFF",
            "speed": FAN_SPEED_OFF,
            "oscillating": False,
            "direction": "forward",
            "rpm": 0,
        }
    }
    coordinator.last_update_success = True
    return coordinator


@pytest.fixture
def fan_entity(mock_coordinator):
    """Create a fan entity for testing."""
    return BlowControlFan(mock_coordinator, "Test Fan", "test_entry_id")


@pytest.mark.asyncio
async def test_fan_initialization(fan_entity):
    """Test fan entity initialization."""
    assert fan_entity.name == "Test Fan"
    assert fan_entity.unique_id == "test_entry_id_fan"
    assert not fan_entity.is_on
    assert fan_entity.percentage == 0
    assert fan_entity.speed_count == 5
    assert not fan_entity.oscillating
    assert fan_entity.available


@pytest.mark.asyncio
async def test_fan_turn_on(fan_entity):
    """Test turning on the fan."""
    await fan_entity.async_turn_on()
    
    assert fan_entity.is_on
    fan_entity.coordinator.async_set_fan_power.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_fan_turn_off(fan_entity):
    """Test turning off the fan."""
    # First turn on
    await fan_entity.async_turn_on()
    
    # Then turn off
    await fan_entity.async_turn_off()
    
    assert not fan_entity.is_on
    assert fan_entity.percentage == 0
    fan_entity.coordinator.async_set_fan_power.assert_called_with(False)


@pytest.mark.asyncio
async def test_fan_set_percentage(fan_entity):
    """Test setting fan percentage."""
    await fan_entity.async_set_percentage(50)
    
    assert fan_entity.is_on
    assert fan_entity.percentage == 50
    fan_entity.coordinator.async_set_fan_speed.assert_called_once()


@pytest.mark.asyncio
async def test_fan_set_oscillating(fan_entity):
    """Test setting fan oscillation."""
    await fan_entity.async_set_oscillating(True)
    
    assert fan_entity.oscillating
    fan_entity.coordinator.async_set_fan_oscillation.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_fan_update_from_coordinator(fan_entity):
    """Test updating fan from coordinator data."""
    test_data = {
        "fan": {
            "power": "ON",
            "speed": FAN_SPEED_LOW,
            "oscillating": True,
            "direction": "forward",
            "rpm": 600,
        }
    }
    
    fan_entity.update_from_coordinator(test_data)
    
    assert fan_entity.is_on
    assert fan_entity.percentage == 25  # FAN_SPEED_LOW = 25%
    assert fan_entity.oscillating


@pytest.mark.asyncio
async def test_fan_should_not_poll(fan_entity):
    """Test that fan should not poll."""
    assert not fan_entity.should_poll


@pytest.mark.asyncio
async def test_fan_available_when_coordinator_successful(fan_entity):
    """Test fan availability based on coordinator."""
    fan_entity.coordinator.last_update_success = True
    assert fan_entity.available
    
    fan_entity.coordinator.last_update_success = False
    assert not fan_entity.available 