"""Pytest configuration and fixtures for BlowControl tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock Home Assistant modules
class MockHomeAssistant:
    """Mock Home Assistant module."""
    
    class config_entries:
        class ConfigEntry:
            def __init__(self, entry_id="test", data=None):
                self.entry_id = entry_id
                self.data = data or {}
        
        class ConfigEntryNotReady(Exception):
            pass
    
    class const:
        CONF_HOST = "host"
        CONF_NAME = "name"
        CONF_DEVICE_ID = "device_id"
        Platform = "platform"
    
    class core:
        class HomeAssistant:
            def __init__(self):
                self.data = {}
    
    class data_entry_flow:
        class FlowResultType:
            CREATE_ENTRY = "create_entry"
            FORM = "form"
            ABORT = "abort"
    
    class helpers:
        class entity_platform:
            class AddEntitiesCallback:
                pass
        
        class update_coordinator:
            class DataUpdateCoordinator:
                def __init__(self, hass, logger, name, update_interval):
                    self.hass = hass
                    self.logger = logger
                    self.name = name
                    self.update_interval = update_interval
                    self.data = {}
                    self.last_update_success = True
            
            class UpdateFailed(Exception):
                pass
    
    class util:
        class percentage:
            @staticmethod
            def percentage_to_ranged_value(range_tuple, percentage):
                return int(percentage / 100 * (range_tuple[1] - range_tuple[0]) + range_tuple[0])
            
            @staticmethod
            def ranged_value_to_percentage(range_tuple, value):
                return int((value - range_tuple[0]) / (range_tuple[1] - range_tuple[0]) * 100)
    
    class components:
        class fan:
            class FanEntity:
                pass
            
            class FanEntityFeature:
                SET_SPEED = 1
                OSCILLATE = 2
                DIRECTION = 4
        
        class binary_sensor:
            class BinarySensorEntity:
                pass
            
            class BinarySensorDeviceClass:
                POWER = "power"
                CONNECTIVITY = "connectivity"
        
        class sensor:
            class SensorEntity:
                pass
            
            class SensorDeviceClass:
                TEMPERATURE = "temperature"
                HUMIDITY = "humidity"
                PM25 = "pm25"
            
            class SensorStateClass:
                MEASUREMENT = "measurement"

# Create mock modules
sys.modules['homeassistant'] = MockHomeAssistant()
sys.modules['homeassistant.config_entries'] = MockHomeAssistant.config_entries
sys.modules['homeassistant.const'] = MockHomeAssistant.const
sys.modules['homeassistant.core'] = MockHomeAssistant.core
sys.modules['homeassistant.data_entry_flow'] = MockHomeAssistant.data_entry_flow
sys.modules['homeassistant.helpers'] = MockHomeAssistant.helpers
sys.modules['homeassistant.helpers.entity_platform'] = MockHomeAssistant.helpers.entity_platform
sys.modules['homeassistant.helpers.update_coordinator'] = MockHomeAssistant.helpers.update_coordinator
sys.modules['homeassistant.util'] = MockHomeAssistant.util
sys.modules['homeassistant.util.percentage'] = MockHomeAssistant.util.percentage
sys.modules['homeassistant.components'] = MockHomeAssistant.components
sys.modules['homeassistant.components.fan'] = MockHomeAssistant.components.fan
sys.modules['homeassistant.components.binary_sensor'] = MockHomeAssistant.components.binary_sensor
sys.modules['homeassistant.components.sensor'] = MockHomeAssistant.components.sensor
sys.modules['homeassistant.exceptions'] = MagicMock()

# Mock other dependencies
sys.modules['aiohttp'] = MagicMock()
sys.modules['async_timeout'] = MagicMock()
sys.modules['voluptuous'] = MagicMock()
sys.modules['voluptuous.validators'] = MagicMock()


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = AsyncMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "host": "192.168.1.100",
        "name": "Test Fan",
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


# Configure pytest
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "coordinator: mark test for coordinator functionality"
    )
    config.addinivalue_line(
        "markers", "fan: mark test for fan entity"
    )
    config.addinivalue_line(
        "markers", "binary_sensor: mark test for binary sensors"
    )
    config.addinivalue_line(
        "markers", "sensor: mark test for sensors"
    )
    config.addinivalue_line(
        "markers", "config_flow: mark test for configuration flow"
    )
    config.addinivalue_line(
        "markers", "init: mark test for initialization"
    ) 