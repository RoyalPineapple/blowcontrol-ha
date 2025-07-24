"""Test the BlowControl config flow."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResultType

from custom_components.blowcontrol.config_flow import BlowControlConfigFlow
from custom_components.blowcontrol.const import DEFAULT_NAME, DOMAIN


@pytest.fixture
def config_flow():
    """Create a config flow instance for testing."""
    return BlowControlConfigFlow()


@pytest.mark.asyncio
async def test_config_flow_initialization(config_flow):
    """Test config flow initialization."""
    assert config_flow.VERSION == 1


@pytest.mark.asyncio
async def test_config_flow_user_step_success(config_flow):
    """Test successful user step."""
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id'):
            with patch.object(config_flow, '_abort_if_unique_id_configured'):
                result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Fan"
    assert result["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }


@pytest.mark.asyncio
async def test_config_flow_user_step_default_name(config_flow):
    """Test user step with default name."""
    user_input = {
        CONF_HOST: "192.168.1.100",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id'):
            with patch.object(config_flow, '_abort_if_unique_id_configured'):
                result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME
    assert result["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: DEFAULT_NAME,
    }


@pytest.mark.asyncio
async def test_config_flow_user_step_invalid_host(config_flow):
    """Test user step with invalid host."""
    user_input = {
        CONF_HOST: "invalid-host",
        CONF_NAME: "Test Fan",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=False):
        result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"]["base"] == "invalid_host"


@pytest.mark.asyncio
async def test_config_flow_user_step_exception(config_flow):
    """Test user step with exception."""
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }
    
    with patch.object(config_flow, '_is_valid_host', side_effect=Exception("Test error")):
        result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"]["base"] == "unknown"


@pytest.mark.asyncio
async def test_config_flow_user_step_no_input(config_flow):
    """Test user step with no input."""
    result = await config_flow.async_step_user(user_input=None)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert "errors" not in result


@pytest.mark.asyncio
async def test_config_flow_host_validation_valid_ip(config_flow):
    """Test host validation with valid IP address."""
    valid_hosts = [
        "192.168.1.100",
        "10.0.0.1",
        "172.16.0.1",
        "127.0.0.1",
        "0.0.0.0",
        "255.255.255.255",
    ]
    
    for host in valid_hosts:
        assert config_flow._is_valid_host(host) is True


@pytest.mark.asyncio
async def test_config_flow_host_validation_valid_hostname(config_flow):
    """Test host validation with valid hostname."""
    valid_hostnames = [
        "localhost",
        "blowcontrol.local",
        "fan.example.com",
        "test-host",
        "device123",
    ]
    
    for hostname in valid_hostnames:
        assert config_flow._is_valid_host(hostname) is True


@pytest.mark.asyncio
async def test_config_flow_host_validation_invalid(config_flow):
    """Test host validation with invalid hosts."""
    invalid_hosts = [
        "invalid-host-",
        "-invalid-host",
        "host.with.invalid.chars!",
        "host with spaces",
        "host.with..double.dots",
        "host.with.trailing.dot.",
        ".host.with.leading.dot",
        "",
        "   ",
        "host.with.very.long.domain.name.that.exceeds.maximum.length.allowed.by.the.validation.regex.pattern",
    ]
    
    for host in invalid_hosts:
        assert config_flow._is_valid_host(host) is False


@pytest.mark.asyncio
async def test_config_flow_host_validation_edge_cases(config_flow):
    """Test host validation edge cases."""
    # Test with None
    assert config_flow._is_valid_host(None) is False
    
    # Test with non-string
    assert config_flow._is_valid_host(123) is False
    assert config_flow._is_valid_host([]) is False
    assert config_flow._is_valid_host({}) is False


@pytest.mark.asyncio
async def test_config_flow_schema_validation(config_flow):
    """Test config flow schema validation."""
    result = await config_flow.async_step_user(user_input=None)
    
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    
    # Check that the schema is properly defined
    schema = result["data_schema"]
    assert CONF_HOST in schema.schema
    assert CONF_NAME in schema.schema


@pytest.mark.asyncio
async def test_config_flow_unique_id_handling(config_flow):
    """Test unique ID handling in config flow."""
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id') as mock_set_id:
            with patch.object(config_flow, '_abort_if_unique_id_configured') as mock_abort:
                await config_flow.async_step_user(user_input=user_input)
    
    mock_set_id.assert_called_once_with("192.168.1.100")
    mock_abort.assert_called_once()


@pytest.mark.asyncio
async def test_config_flow_error_handling(config_flow):
    """Test error handling in config flow."""
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Test Fan",
    }
    
    # Test with validation error
    with patch.object(config_flow, '_is_valid_host', return_value=False):
        result = await config_flow.async_step_user(user_input=user_input)
        assert result["errors"]["base"] == "invalid_host"
    
    # Test with unique ID conflict
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id'):
            with patch.object(config_flow, '_abort_if_unique_id_configured', side_effect=config_entries.ConfigEntryNotReady):
                result = await config_flow.async_step_user(user_input=user_input)
                assert result["type"] == FlowResultType.ABORT
                assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_config_flow_data_persistence(config_flow):
    """Test that config data is properly persisted."""
    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_NAME: "Custom Fan Name",
    }
    
    with patch.object(config_flow, '_is_valid_host', return_value=True):
        with patch.object(config_flow, 'async_set_unique_id'):
            with patch.object(config_flow, '_abort_if_unique_id_configured'):
                result = await config_flow.async_step_user(user_input=user_input)
    
    assert result["data"][CONF_HOST] == "192.168.1.100"
    assert result["data"][CONF_NAME] == "Custom Fan Name"
    assert len(result["data"]) == 2  # Only host and name should be stored 