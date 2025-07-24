"""Integration tests for the BlowControl integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.blowcontrol import async_setup, async_setup_entry, async_unload_entry
from custom_components.blowcontrol.config_flow import BlowControlConfigFlow
from custom_components.blowcontrol.coordinator import BlowControlCoordinator
from custom_components.blowcontrol.fan import BlowControlFan
from custom_components.blowcontrol.binary_sensor import BlowControlPowerSensor, BlowControlConnectionSensor
from custom_components.blowcontrol.sensor import (
    BlowControlTemperatureSensor,
    BlowControlHumiditySensor,
    BlowControlAirQualitySensor,
    BlowControlFanSpeedSensor,
)
from custom_components.blowcontrol.const import DOMAIN, DEFAULT_NAME


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = AsyncMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }
    return entry


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator with realistic data."""
    coordinator = AsyncMock()
    coordinator.data = {
        "fan": {
            "power": "ON",
            "speed": 2,
            "oscillating": False,
            "direction": "forward",
            "rpm": 1200,
        },
        "environment": {
            "temperature": 22.5,
            "humidity": 45.2,
            "air_quality": 12.3,
        },
        "connection": {
            "connected": True,
            "last_seen": "2024-01-01T12:00:00Z",
        }
    }
    coordinator.last_update_success = True
    return coordinator


@pytest.mark.asyncio
async def test_full_integration_setup_and_teardown(mock_hass, mock_config_entry):
    """Test complete integration setup and teardown."""
    # Setup integration
    with patch('custom_components.blowcontrol.async_forward_entry_setups') as mock_forward:
        mock_forward.return_value = None
        
        setup_result = await async_setup_entry(mock_hass, mock_config_entry)
    
    assert setup_result is True
    assert DOMAIN in mock_hass.data
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
    
    # Teardown integration
    with patch('custom_components.blowcontrol.async_unload_platforms') as mock_unload:
        mock_unload.return_value = True
        
        unload_result = await async_unload_entry(mock_hass, mock_config_entry)
    
    assert unload_result is True
    assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_coordinator_with_entities(mock_hass, mock_coordinator):
    """Test coordinator working with all entity types."""
    # Create entities
    fan = BlowControlFan(mock_coordinator, "Test Fan", "test_entry_id")
    power_sensor = BlowControlPowerSensor(mock_coordinator, "Test Fan", "test_entry_id")
    connection_sensor = BlowControlConnectionSensor(mock_coordinator, "Test Fan", "test_entry_id")
    temp_sensor = BlowControlTemperatureSensor(mock_coordinator, "Test Fan", "test_entry_id")
    humidity_sensor = BlowControlHumiditySensor(mock_coordinator, "Test Fan", "test_entry_id")
    air_quality_sensor = BlowControlAirQualitySensor(mock_coordinator, "Test Fan", "test_entry_id")
    fan_speed_sensor = BlowControlFanSpeedSensor(mock_coordinator, "Test Fan", "test_entry_id")
    
    # Test initial states
    assert fan.is_on
    assert power_sensor.is_on
    assert connection_sensor.is_on
    assert temp_sensor.state == 22.5
    assert humidity_sensor.state == 45.2
    assert air_quality_sensor.state == 12.3
    assert fan_speed_sensor.state == 1200
    
    # Update coordinator data
    new_data = {
        "fan": {
            "power": "OFF",
            "speed": 0,
            "oscillating": True,
            "direction": "reverse",
            "rpm": 0,
        },
        "environment": {
            "temperature": 25.0,
            "humidity": 60.0,
            "air_quality": 15.0,
        },
        "connection": {
            "connected": False,
            "last_seen": "2024-01-01T12:30:00Z",
        }
    }
    
    # Update entities
    fan.update_from_coordinator(new_data)
    power_sensor.update_from_coordinator(new_data)
    connection_sensor.update_from_coordinator(new_data)
    temp_sensor.update_from_coordinator(new_data)
    humidity_sensor.update_from_coordinator(new_data)
    air_quality_sensor.update_from_coordinator(new_data)
    fan_speed_sensor.update_from_coordinator(new_data)
    
    # Verify updated states
    assert not fan.is_on
    assert not power_sensor.is_on
    assert not connection_sensor.is_on
    assert temp_sensor.state == 25.0
    assert humidity_sensor.state == 60.0
    assert air_quality_sensor.state == 15.0
    assert fan_speed_sensor.state == 0


@pytest.mark.asyncio
async def test_config_flow_integration():
    """Test config flow integration."""
    config_flow = BlowControlConfigFlow()
    
    # Test successful configuration
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Integration Test Fan",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id'):
            with patch.object(config_flow, '_abort_if_unique_id_configured'):
                result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Integration Test Fan"
    assert result["data"][CONF_HOST] == "192.168.1.100"
    assert result["data"][CONF_NAME] == "Integration Test Fan"


@pytest.mark.asyncio
async def test_entity_coordination(mock_coordinator):
    """Test that entities properly coordinate with the coordinator."""
    # Create entities
    fan = BlowControlFan(mock_coordinator, "Test Fan", "test_entry_id")
    power_sensor = BlowControlPowerSensor(mock_coordinator, "Test Fan", "test_entry_id")
    
    # Test that entities don't poll (they rely on coordinator)
    assert not fan.should_poll
    assert not power_sensor.should_poll
    
    # Test availability based on coordinator
    assert fan.available
    assert power_sensor.available
    
    # Simulate coordinator failure
    mock_coordinator.last_update_success = False
    assert not fan.available
    assert not power_sensor.available


@pytest.mark.asyncio
async def test_fan_control_integration(mock_coordinator):
    """Test fan control integration with coordinator."""
    fan = BlowControlFan(mock_coordinator, "Test Fan", "test_entry_id")
    
    # Test fan control methods
    with patch.object(mock_coordinator, 'async_set_fan_power') as mock_power:
        await fan.async_turn_on()
        mock_power.assert_called_once_with(True)
    
    with patch.object(mock_coordinator, 'async_set_fan_power') as mock_power:
        await fan.async_turn_off()
        mock_power.assert_called_once_with(False)
    
    with patch.object(mock_coordinator, 'async_set_fan_speed') as mock_speed:
        await fan.async_set_percentage(75)
        mock_speed.assert_called_once()
    
    with patch.object(mock_coordinator, 'async_set_fan_oscillation') as mock_osc:
        await fan.async_set_oscillating(True)
        mock_osc.assert_called_once_with(True)
    
    with patch.object(mock_coordinator, 'async_set_fan_direction') as mock_dir:
        await fan.async_set_direction("reverse")
        mock_dir.assert_called_once_with("reverse")


@pytest.mark.asyncio
async def test_data_consistency_across_entities(mock_coordinator):
    """Test that all entities show consistent data from coordinator."""
    # Create all entities
    entities = [
        BlowControlFan(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlPowerSensor(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlConnectionSensor(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlTemperatureSensor(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlHumiditySensor(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlAirQualitySensor(mock_coordinator, "Test Fan", "test_entry_id"),
        BlowControlFanSpeedSensor(mock_coordinator, "Test Fan", "test_entry_id"),
    ]
    
    # Test initial consistency
    assert all(entity.available for entity in entities)
    
    # Update coordinator data
    new_data = {
        "fan": {"power": "OFF", "speed": 0, "rpm": 0},
        "environment": {"temperature": 30.0, "humidity": 80.0, "air_quality": 25.0},
        "connection": {"connected": False}
    }
    
    # Update all entities
    for entity in entities:
        entity.update_from_coordinator(new_data)
    
    # Test consistency after update
    fan, power, connection, temp, humidity, air_quality, fan_speed = entities
    
    assert not fan.is_on
    assert not power.is_on
    assert not connection.is_on
    assert temp.state == 30.0
    assert humidity.state == 80.0
    assert air_quality.state == 25.0
    assert fan_speed.state == 0


@pytest.mark.asyncio
async def test_error_handling_integration(mock_hass, mock_config_entry):
    """Test error handling across the integration."""
    # Test setup with error
    with patch('custom_components.blowcontrol.async_forward_entry_setups', side_effect=Exception("Setup error")):
        with pytest.raises(Exception) as exc_info:
            await async_setup_entry(mock_hass, mock_config_entry)
        assert "Setup error" in str(exc_info.value)
    
    # Test teardown with error
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
        "coordinator": AsyncMock(),
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms', side_effect=Exception("Teardown error")):
        with pytest.raises(Exception) as exc_info:
            await async_unload_entry(mock_hass, mock_config_entry)
        assert "Teardown error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_multiple_config_entries(mock_hass):
    """Test handling multiple config entries."""
    entry1 = MagicMock(spec=ConfigEntry)
    entry1.entry_id = "entry1"
    entry1.data = {CONF_HOST: "192.168.1.100", CONF_NAME: "Fan 1"}
    
    entry2 = MagicMock(spec=ConfigEntry)
    entry2.entry_id = "entry2"
    entry2.data = {CONF_HOST: "192.168.1.101", CONF_NAME: "Fan 2"}
    
    # Setup both entries
    with patch('custom_components.blowcontrol.async_forward_entry_setups'):
        await async_setup_entry(mock_hass, entry1)
        await async_setup_entry(mock_hass, entry2)
    
    # Verify both are stored
    assert "entry1" in mock_hass.data[DOMAIN]
    assert "entry2" in mock_hass.data[DOMAIN]
    
    # Teardown one entry
    with patch('custom_components.blowcontrol.async_unload_platforms', return_value=True):
        await async_unload_entry(mock_hass, entry1)
    
    # Verify only one remains
    assert "entry1" not in mock_hass.data[DOMAIN]
    assert "entry2" in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_coordinator_lifecycle(mock_hass):
    """Test coordinator lifecycle management."""
    coordinator = BlowControlCoordinator(mock_hass, "192.168.1.100")
    
    # Test initialization
    assert coordinator.host == "192.168.1.100"
    assert coordinator.name == "BlowControl 192.168.1.100"
    
    # Test data fetching
    data = await coordinator._async_update_data()
    assert "fan" in data
    assert "environment" in data
    assert "connection" in data
    
    # Test cleanup
    await coordinator.async_close()
    coordinator.session.close.assert_called_once() 