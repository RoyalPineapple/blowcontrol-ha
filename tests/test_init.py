"""Test the BlowControl integration initialization."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.blowcontrol import async_setup, async_setup_entry, async_unload_entry
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


@pytest.mark.asyncio
async def test_async_setup(mock_hass):
    """Test async_setup function."""
    config = {DOMAIN: {CONF_HOST: "192.168.1.100"}}
    
    result = await async_setup(mock_hass, config)
    
    assert result is True
    assert DOMAIN in mock_hass.data


@pytest.mark.asyncio
async def test_async_setup_entry_success(mock_hass, mock_config_entry):
    """Test successful async_setup_entry."""
    with patch('custom_components.blowcontrol.async_forward_entry_setups') as mock_forward:
        mock_forward.return_value = None
        
        result = await async_setup_entry(mock_hass, mock_config_entry)
    
    assert result is True
    assert DOMAIN in mock_hass.data
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
    assert mock_hass.data[DOMAIN][mock_config_entry.entry_id] == mock_config_entry.data
    mock_forward.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_existing_data(mock_hass, mock_config_entry):
    """Test async_setup_entry with existing data."""
    # Pre-populate data
    mock_hass.data[DOMAIN] = {"existing_entry": {"host": "existing"}}
    
    with patch('custom_components.blowcontrol.async_forward_entry_setups') as mock_forward:
        mock_forward.return_value = None
        
        result = await async_setup_entry(mock_hass, mock_config_entry)
    
    assert result is True
    assert "existing_entry" in mock_hass.data[DOMAIN]
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_success(mock_hass, mock_config_entry):
    """Test successful async_unload_entry."""
    # Setup data first
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
        "coordinator": AsyncMock(),
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms') as mock_unload:
        mock_unload.return_value = True
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
    
    assert result is True
    assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]
    assert "coordinator" not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_failure(mock_hass, mock_config_entry):
    """Test async_unload_entry when unload fails."""
    # Setup data first
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
        "coordinator": AsyncMock(),
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms') as mock_unload:
        mock_unload.return_value = False
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
    
    assert result is False
    # Data should remain unchanged
    assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]
    assert "coordinator" in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_no_coordinator(mock_hass, mock_config_entry):
    """Test async_unload_entry when no coordinator exists."""
    # Setup data without coordinator
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms') as mock_unload:
        mock_unload.return_value = True
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
    
    assert result is True
    assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_coordinator_cleanup(mock_hass, mock_config_entry):
    """Test that coordinator is properly cleaned up."""
    # Setup data with coordinator
    mock_coordinator = AsyncMock()
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
        "coordinator": mock_coordinator,
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms') as mock_unload:
        mock_unload.return_value = True
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
    
    assert result is True
    mock_coordinator.async_close.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_platform_setup(mock_hass, mock_config_entry):
    """Test that platforms are properly set up."""
    with patch('custom_components.blowcontrol.async_forward_entry_setups') as mock_forward:
        mock_forward.return_value = None
        
        await async_setup_entry(mock_hass, mock_config_entry)
    
    # Check that async_forward_entry_setups was called with correct platforms
    mock_forward.assert_called_once()
    call_args = mock_forward.call_args
    assert call_args[0][0] == mock_config_entry  # First argument should be config_entry


@pytest.mark.asyncio
async def test_async_setup_entry_data_storage(mock_hass, mock_config_entry):
    """Test that config data is properly stored."""
    with patch('custom_components.blowcontrol.async_forward_entry_setups'):
        await async_setup_entry(mock_hass, mock_config_entry)
    
    stored_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
    assert stored_data[CONF_HOST] == "192.168.1.100"
    assert stored_data[CONF_NAME] == "Test Fan"


@pytest.mark.asyncio
async def test_async_setup_entry_default_name(mock_hass, mock_config_entry):
    """Test that default name is used when not provided."""
    # Remove name from config entry
    mock_config_entry.data = {CONF_HOST: "192.168.1.100"}
    
    with patch('custom_components.blowcontrol.async_forward_entry_setups'):
        await async_setup_entry(mock_hass, mock_config_entry)
    
    stored_data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
    assert stored_data[CONF_HOST] == "192.168.1.100"
    # Name should be added with default value
    assert CONF_NAME in stored_data


@pytest.mark.asyncio
async def test_async_setup_entry_multiple_entries(mock_hass):
    """Test handling multiple config entries."""
    entry1 = MagicMock(spec=ConfigEntry)
    entry1.entry_id = "entry1"
    entry1.data = {CONF_HOST: "192.168.1.100", CONF_NAME: "Fan 1"}
    
    entry2 = MagicMock(spec=ConfigEntry)
    entry2.entry_id = "entry2"
    entry2.data = {CONF_HOST: "192.168.1.101", CONF_NAME: "Fan 2"}
    
    with patch('custom_components.blowcontrol.async_forward_entry_setups'):
        await async_setup_entry(mock_hass, entry1)
        await async_setup_entry(mock_hass, entry2)
    
    assert "entry1" in mock_hass.data[DOMAIN]
    assert "entry2" in mock_hass.data[DOMAIN]
    assert mock_hass.data[DOMAIN]["entry1"] == entry1.data
    assert mock_hass.data[DOMAIN]["entry2"] == entry2.data


@pytest.mark.asyncio
async def test_async_setup_entry_error_handling(mock_hass, mock_config_entry):
    """Test error handling in async_setup_entry."""
    with patch('custom_components.blowcontrol.async_forward_entry_setups', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await async_setup_entry(mock_hass, mock_config_entry)
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_unload_entry_error_handling(mock_hass, mock_config_entry):
    """Test error handling in async_unload_entry."""
    mock_hass.data[DOMAIN] = {
        mock_config_entry.entry_id: mock_config_entry.data,
        "coordinator": AsyncMock(),
    }
    
    with patch('custom_components.blowcontrol.async_unload_platforms', side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await async_unload_entry(mock_hass, mock_config_entry)
        assert "Test error" in str(exc_info.value) 