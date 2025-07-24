"""Test the BlowControl coordinator."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from custom_components.blowcontrol.coordinator import BlowControlCoordinator
from custom_components.blowcontrol.const import DEFAULT_SCAN_INTERVAL


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = AsyncMock()
    hass.data = {}
    return hass


@pytest.fixture
def coordinator(mock_hass):
    """Create a coordinator instance for testing."""
    return BlowControlCoordinator(mock_hass, "192.168.1.100")


@pytest.mark.asyncio
async def test_coordinator_initialization(coordinator):
    """Test coordinator initialization."""
    assert coordinator.host == "192.168.1.100"
    assert coordinator.name == "BlowControl 192.168.1.100"
    assert coordinator.update_interval.total_seconds() == DEFAULT_SCAN_INTERVAL


@pytest.mark.asyncio
async def test_fetch_mock_data(coordinator):
    """Test fetching mock data."""
    data = await coordinator._fetch_mock_data()
    
    assert "fan" in data
    assert "environment" in data
    assert "connection" in data
    
    fan_data = data["fan"]
    assert fan_data["power"] == "ON"
    assert fan_data["speed"] == 2
    assert fan_data["oscillating"] is False
    assert fan_data["direction"] == "forward"
    assert fan_data["rpm"] == 1200
    
    env_data = data["environment"]
    assert env_data["temperature"] == 22.5
    assert env_data["humidity"] == 45.2
    assert env_data["air_quality"] == 12.3
    
    conn_data = data["connection"]
    assert conn_data["connected"] is True
    assert conn_data["last_seen"] == "2024-01-01T12:00:00Z"


@pytest.mark.asyncio
async def test_async_update_data_success(coordinator):
    """Test successful data update."""
    with patch.object(coordinator, '_fetch_mock_data', return_value={"test": "data"}):
        data = await coordinator._async_update_data()
        assert data == {"test": "data"}


@pytest.mark.asyncio
async def test_async_update_data_timeout(coordinator):
    """Test data update with timeout."""
    async def slow_mock_data():
        await asyncio.sleep(15)  # Longer than timeout
        return {"test": "data"}
    
    with patch.object(coordinator, '_fetch_mock_data', side_effect=slow_mock_data):
        with pytest.raises(Exception) as exc_info:
            await coordinator._async_update_data()
        assert "Timeout communicating with BlowControl device" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_update_data_exception(coordinator):
    """Test data update with exception."""
    with patch.object(coordinator, '_fetch_mock_data', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await coordinator._async_update_data()
        assert "Error communicating with BlowControl device: Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_set_fan_power_success(coordinator):
    """Test setting fan power successfully."""
    with patch('asyncio.sleep') as mock_sleep:
        await coordinator.async_set_fan_power(True)
        mock_sleep.assert_called_once_with(0.1)


@pytest.mark.asyncio
async def test_async_set_fan_power_exception(coordinator):
    """Test setting fan power with exception."""
    with patch('asyncio.sleep', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await coordinator.async_set_fan_power(True)
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_set_fan_speed_success(coordinator):
    """Test setting fan speed successfully."""
    with patch('asyncio.sleep') as mock_sleep:
        await coordinator.async_set_fan_speed(3)
        mock_sleep.assert_called_once_with(0.1)


@pytest.mark.asyncio
async def test_async_set_fan_speed_exception(coordinator):
    """Test setting fan speed with exception."""
    with patch('asyncio.sleep', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await coordinator.async_set_fan_speed(3)
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_set_fan_oscillation_success(coordinator):
    """Test setting fan oscillation successfully."""
    with patch('asyncio.sleep') as mock_sleep:
        await coordinator.async_set_fan_oscillation(True)
        mock_sleep.assert_called_once_with(0.1)


@pytest.mark.asyncio
async def test_async_set_fan_oscillation_exception(coordinator):
    """Test setting fan oscillation with exception."""
    with patch('asyncio.sleep', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await coordinator.async_set_fan_oscillation(True)
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_set_fan_direction_success(coordinator):
    """Test setting fan direction successfully."""
    with patch('asyncio.sleep') as mock_sleep:
        await coordinator.async_set_fan_direction("reverse")
        mock_sleep.assert_called_once_with(0.1)


@pytest.mark.asyncio
async def test_async_set_fan_direction_exception(coordinator):
    """Test setting fan direction with exception."""
    with patch('asyncio.sleep', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await coordinator.async_set_fan_direction("reverse")
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_close(coordinator):
    """Test closing the coordinator."""
    await coordinator.async_close()
    coordinator.session.close.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_timeout_handling(coordinator):
    """Test coordinator timeout handling."""
    async def timeout_mock():
        await asyncio.sleep(0.1)
        raise asyncio.TimeoutError()
    
    with patch.object(coordinator, '_fetch_mock_data', side_effect=timeout_mock):
        with pytest.raises(Exception) as exc_info:
            await coordinator._async_update_data()
        assert "Timeout communicating with BlowControl device" in str(exc_info.value) 