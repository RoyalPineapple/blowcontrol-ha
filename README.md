# BlowControl Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40RoyalPineapple-blue.svg)](https://github.com/RoyalPineapple)
[![license](https://img.shields.io/badge/license-Seems%20to%20Work-orange.svg)](LICENSE)

A comprehensive Home Assistant integration for controlling Dyson fans through the BlowControl system. This integration provides full fan control, environmental monitoring, and status tracking for your BlowControl-enabled Dyson devices.

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Entities](#-entities)
- [Usage Examples](#-usage-examples)
- [Automations](#-automations)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Changelog](#-changelog)
- [License](#-license)

## ✨ Features

### 🌀 Fan Control
- **Power Management**: Turn fan on/off with full state tracking
- **Speed Control**: Precise speed adjustment from 0-100% with 5 discrete levels
- **Oscillation Control**: Enable/disable fan oscillation
- **Direction Control**: Forward/reverse fan direction
- **Speed Presets**: Low, Medium, High, Max speed settings

### 📊 Environmental Monitoring
- **Temperature Sensor**: Real-time temperature readings in Celsius
- **Humidity Sensor**: Relative humidity percentage monitoring
- **Air Quality Sensor**: PM2.5 air quality measurements (µg/m³)
- **Fan Speed Sensor**: Current fan RPM monitoring

### 🔍 Status Monitoring
- **Power Status**: Binary sensor for fan power state
- **Connection Status**: Real-time connection monitoring to BlowControl device
- **Error Detection**: Automatic error detection and reporting

### 🎛️ User Experience
- **Configuration Flow**: User-friendly setup wizard
- **Translations**: Multi-language support (English included)
- **Error Handling**: Comprehensive error handling and user feedback
- **Data Coordination**: Efficient data management with automatic updates

## 📋 Requirements

### Hardware Requirements
- **BlowControl Device**: Compatible BlowControl hardware for Dyson fans
- **Network Access**: Device must be accessible on your local network
- **Dyson Fan**: Compatible Dyson fan model

### Software Requirements
- **Home Assistant**: Version 2023.8.0 or higher
- **Python**: 3.10 or higher (included with Home Assistant)
- **Network**: Stable network connection between Home Assistant and BlowControl device
- **BlowControl CLI**: The `blowcontrol` command-line tool must be installed and available in the system PATH

### Optional Requirements
- **HACS**: For easy installation and updates
- **Git**: For development and manual installation

## 🚀 Installation

### Method 1: HACS Installation (Recommended)

1. **Install HACS** (if not already installed):
   ```bash
   # Follow the official HACS installation guide
   # https://hacs.xyz/docs/installation/manual
   ```

2. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Go to **Settings** → **Repositories**
   - Click **Add Repository**
   - Repository: `RoyalPineapple/blowcontrol-ha`
   - Category: **Integration**

3. **Install Integration**:
   - Go to **HACS** → **Integrations**
   - Search for "BlowControl"
   - Click **Download**
   - Restart Home Assistant

### Method 2: Manual Installation

#### Option A: Using the Installation Helper (Recommended)
```bash
# Download and run the installation helper
curl -O https://raw.githubusercontent.com/RoyalPineapple/blowcontrol-ha/main/scripts/install_blowcontrol.py
python3 install_blowcontrol.py
```

#### Option B: Manual Installation
```bash
# Install Python dependencies
pip install paho-mqtt python-dotenv

# Clone and install BlowControl
git clone https://github.com/RoyalPineapple/blowcontrol.git
cd blowcontrol
pip install -e .
```

2. **Clone Repository**:
   ```bash
   git clone https://github.com/RoyalPineapple/blowcontrol-ha.git
   cd blowcontrol-ha
   ```

3. **Copy Integration**:
   ```bash
   # Copy to your Home Assistant config directory
   cp -r custom_components/blowcontrol /path/to/homeassistant/config/custom_components/
   ```

3. **Restart Home Assistant**:
   - Go to **Settings** → **System** → **Restart**
   - Or restart your Home Assistant server/container

### Method 3: Docker Installation

If running Home Assistant in Docker:

```bash
# Mount the integration directory
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -v /PATH_TO_YOUR_CONFIG:/config \
  -v /etc/localtime:/etc/localtime:ro \
  -p 8123:8123 \
  homeassistant/home-assistant:stable

# Copy integration files to mounted config directory
cp -r custom_components/blowcontrol /PATH_TO_YOUR_CONFIG/custom_components/
```

## ⚙️ Configuration

### Prerequisites

Before configuring the integration, ensure you have:

1. **BlowControl CLI Installed**: The `blowcontrol` command must be available in your system PATH
2. **Device Credentials**: You'll need the following information:
   - Device IP address
   - MQTT password
   - Device serial number
   - MQTT port (usually 1883)
   - Root topic (usually 438M)

### Initial Setup

1. **Access Home Assistant**:
   - Open your Home Assistant instance
   - Navigate to **Settings** → **Devices & Services**

2. **Add Integration**:
   - Click **Add Integration** (bottom right)
   - Search for **"BlowControl"**
   - Click on the integration

3. **Configure Device**:
   - **Device IP**: IP address of your BlowControl device
   - **MQTT Password**: Password for MQTT communication
   - **Serial Number**: Device serial number
   - **MQTT Port**: MQTT port (default: 1883)
   - **Root Topic**: MQTT root topic (default: 438M)
   - **Name**: Friendly name for the integration

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `host` | string | Yes | - | IP address of BlowControl device |
| `name` | string | No | "BlowControl Fan" | Custom name for the device |
| `device_id` | string | No | - | Unique device identifier |

### Advanced Configuration

For advanced users, you can configure the integration via `configuration.yaml`:

```yaml
# Example configuration.yaml entry
blowcontrol:
  host: 192.168.1.100
  name: "Living Room Fan"
  device_id: "dyson_fan_001"
```

## 📱 Entities

The integration creates the following entities automatically:

### Fan Entity
**Entity ID**: `fan.blowcontrol_fan`

**Features**:
- Power control (on/off)
- Speed control (0-100%)
- Oscillation control
- Direction control
- Speed presets

**Attributes**:
```yaml
percentage: 75
oscillating: true
direction: forward
speed_count: 5
supported_features: 7
```

### Binary Sensors

#### Power Status
**Entity ID**: `binary_sensor.blowcontrol_power`

**States**:
- `on`: Fan is powered on
- `off`: Fan is powered off

#### Connection Status
**Entity ID**: `binary_sensor.blowcontrol_connected`

**States**:
- `on`: Connected to BlowControl device
- `off`: Disconnected from BlowControl device

### Sensors

#### Temperature
**Entity ID**: `sensor.blowcontrol_temperature`

**Unit**: °C (Celsius)
**Device Class**: `temperature`
**State Class**: `measurement`

#### Humidity
**Entity ID**: `sensor.blowcontrol_humidity`

**Unit**: % (Percentage)
**Device Class**: `humidity`
**State Class**: `measurement`

#### Air Quality
**Entity ID**: `sensor.blowcontrol_air_quality`

**Unit**: µg/m³
**Device Class**: `pm25`
**State Class**: `measurement`

#### Fan Speed
**Entity ID**: `sensor.blowcontrol_fan_speed`

**Unit**: RPM
**State Class**: `measurement`

## 💡 Usage Examples

### Basic Fan Control

```yaml
# Turn fan on at 50% speed
service: fan.turn_on
target:
  entity_id: fan.blowcontrol_fan
data:
  percentage: 50

# Turn fan off
service: fan.turn_off
target:
  entity_id: fan.blowcontrol_fan

# Set oscillation
service: fan.set_oscillating
target:
  entity_id: fan.blowcontrol_fan
data:
  oscillating: true
```

### Speed Control

```yaml
# Set specific percentage
service: fan.set_percentage
target:
  entity_id: fan.blowcontrol_fan
data:
  percentage: 75

# Set direction
service: fan.set_direction
target:
  entity_id: fan.blowcontrol_fan
data:
  direction: reverse
```

## 🤖 Automations

### Temperature-Based Fan Control

```yaml
automation:
  - alias: "Turn on fan when hot"
    description: "Automatically turn on fan when temperature exceeds 25°C"
    trigger:
      platform: numeric_state
      entity_id: sensor.blowcontrol_temperature
      above: 25
    condition:
      - condition: state
        entity_id: fan.blowcontrol_fan
        state: "off"
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 75
      - service: fan.set_oscillating
        target:
          entity_id: fan.blowcontrol_fan
        data:
          oscillating: true
```

### Air Quality Monitoring

```yaml
automation:
  - alias: "High air quality alert"
    description: "Turn on fan when air quality is poor"
    trigger:
      platform: numeric_state
      entity_id: sensor.blowcontrol_air_quality
      above: 35
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 100
      - service: notify.mobile_app
        data:
          title: "Air Quality Alert"
          message: "Poor air quality detected. Fan turned on at maximum speed."
```

### Night Mode

```yaml
automation:
  - alias: "Night mode fan"
    description: "Set fan to quiet night mode"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 25
      - service: fan.set_oscillating
        target:
          entity_id: fan.blowcontrol_fan
        data:
          oscillating: true
```

### Connection Monitoring

```yaml
automation:
  - alias: "BlowControl connection lost"
    description: "Alert when connection to BlowControl device is lost"
    trigger:
      platform: state
      entity_id: binary_sensor.blowcontrol_connected
      to: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "BlowControl Connection Lost"
          message: "Connection to BlowControl device has been lost. Check network connection."
```

## 📊 Scripts

### Comfort Mode

```yaml
script:
  comfort_mode:
    alias: "Comfort Mode"
    description: "Set fan to comfortable settings"
    sequence:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 60
      - service: fan.set_oscillating
        target:
          entity_id: fan.blowcontrol_fan
        data:
          oscillating: true
      - service: fan.set_direction
        target:
          entity_id: fan.blowcontrol_fan
        data:
          direction: forward
```

### Sleep Mode

```yaml
script:
  sleep_mode:
    alias: "Sleep Mode"
    description: "Set fan to sleep-friendly settings"
    sequence:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 20
      - service: fan.set_oscillating
        target:
          entity_id: fan.blowcontrol_fan
        data:
          oscillating: false
```

### Turbo Mode

```yaml
script:
  turbo_mode:
    alias: "Turbo Mode"
    description: "Set fan to maximum performance"
    sequence:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 100
      - service: fan.set_oscillating
        target:
          entity_id: fan.blowcontrol_fan
        data:
          oscillating: true
```

## 🔧 Troubleshooting

### Common Issues

#### Integration Not Appearing
**Problem**: BlowControl integration doesn't appear in the integrations list.

**Solutions**:
1. **Restart Home Assistant** after installation
2. **Check file permissions** on the integration directory
3. **Verify installation path**: Ensure files are in `config/custom_components/blowcontrol/`
4. **Check Home Assistant logs** for errors

#### Connection Issues
**Problem**: Cannot connect to BlowControl device.

**Solutions**:
1. **Verify IP address** is correct and device is on same network
2. **Check network connectivity**:
   ```bash
   ping <blowcontrol_ip_address>
   ```
3. **Verify BlowControl service** is running on the device
4. **Check firewall settings** on both Home Assistant and BlowControl device

#### BlowControl CLI Not Found
**Problem**: Error "No such file or directory: 'blowcontrol'" in logs.

**Solutions**:
1. **Install BlowControl CLI**:
   ```bash
   # Follow the official BlowControl installation guide
   # https://github.com/yourusername/blowcontrol
   ```
2. **Verify CLI installation**:
   ```bash
   blowcontrol --help
   ```
3. **Check PATH**: Ensure `blowcontrol` is in your system PATH
4. **Restart Home Assistant** after installing the CLI
5. **Check permissions**: Ensure the CLI is executable

#### Entities Not Updating
**Problem**: Sensor values are not updating or showing stale data.

**Solutions**:
1. **Check coordinator status** in Home Assistant logs
2. **Verify network connectivity** to BlowControl device
3. **Restart the integration**:
   - Go to **Settings** → **Devices & Services**
   - Find BlowControl integration
   - Click **Configure** → **Reload**
4. **Check for error messages** in logs

#### Fan Not Responding
**Problem**: Fan controls don't work or fan doesn't respond.

**Solutions**:
1. **Check power status** binary sensor
2. **Verify connection status** binary sensor
3. **Check BlowControl device logs**
4. **Test direct communication** with BlowControl device
5. **Restart BlowControl device** if necessary

### Debug Mode

Enable debug logging for detailed troubleshooting:

```yaml
# Add to configuration.yaml
logger:
  default: info
  logs:
    custom_components.blowcontrol: debug
```

### Log Analysis

Common log entries and their meanings:

```
# Successful connection
INFO (MainThread) [custom_components.blowcontrol.coordinator] Connected to BlowControl device at 192.168.1.100

# Connection timeout
ERROR (MainThread) [custom_components.blowcontrol.coordinator] Timeout communicating with BlowControl device

# API error
ERROR (MainThread) [custom_components.blowcontrol.coordinator] Error communicating with BlowControl device: Connection refused
```

## 🛠️ Development

### Project Structure

```
blowcontrol-ha/
├── custom_components/
│   └── blowcontrol/
│       ├── __init__.py              # Main integration setup
│       ├── manifest.json            # Integration metadata
│       ├── const.py                 # Constants and configuration
│       ├── config_flow.py           # Configuration flow
│       ├── coordinator.py           # Data coordination
│       ├── fan.py                   # Fan entity
│       ├── binary_sensor.py         # Binary sensors
│       ├── sensor.py                # Sensors
│       └── translations/
│           └── en.json              # English translations
├── docs/                            # Documentation
├── tests/                           # Test files
├── README.md                        # This file
└── LICENSE                          # License file
```

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/RoyalPineapple/blowcontrol-ha.git
   cd blowcontrol-ha
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Setup Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

4. **Run Tests**:
   ```bash
   pytest tests/
   ```

### Code Style

This project follows:
- **Black**: Code formatting
- **Flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

### Adding New Features

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement Changes**:
   - Follow Home Assistant integration guidelines
   - Add proper type hints
   - Include docstrings
   - Add tests for new functionality

3. **Test Changes**:
   ```bash
   # Run linting
   flake8 custom_components/blowcontrol/
   
   # Run type checking
   mypy custom_components/blowcontrol/
   
   # Run tests
   pytest tests/
   ```

4. **Submit Pull Request**:
   - Create detailed description
   - Include testing instructions
   - Reference any related issues

## 📚 API Reference

### Coordinator Methods

#### `async_set_fan_power(power: bool)`
Set fan power state.

**Parameters**:
- `power` (bool): True to turn on, False to turn off

**Returns**: None

**Raises**: Exception on communication error

#### `async_set_fan_speed(speed: int)`
Set fan speed level.

**Parameters**:
- `speed` (int): Speed level (0-4)

**Returns**: None

**Raises**: Exception on communication error

#### `async_set_fan_oscillation(oscillating: bool)`
Set fan oscillation state.

**Parameters**:
- `oscillating` (bool): True to enable, False to disable

**Returns**: None

**Raises**: Exception on communication error

#### `async_set_fan_direction(direction: str)`
Set fan direction.

**Parameters**:
- `direction` (str): "forward" or "reverse"

**Returns**: None

**Raises**: Exception on communication error

### Entity Methods

#### Fan Entity
- `async_turn_on()`: Turn fan on
- `async_turn_off()`: Turn fan off
- `async_set_percentage(percentage: int)`: Set speed percentage
- `async_set_oscillating(oscillating: bool)`: Set oscillation
- `async_set_direction(direction: str)`: Set direction

#### Sensor Entities
- `update_from_coordinator(data: dict)`: Update from coordinator data

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Create detailed bug reports with steps to reproduce
2. **Request Features**: Suggest new features or improvements
3. **Submit Code**: Contribute code improvements or new features
4. **Improve Documentation**: Help improve this README or other docs
5. **Test**: Test the integration and report issues

### Development Guidelines

1. **Follow PEP 8**: Use Python style guidelines
2. **Add Tests**: Include tests for new functionality
3. **Update Documentation**: Keep docs up to date with changes
4. **Use Type Hints**: Include proper type annotations
5. **Write Docstrings**: Document all functions and classes

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run tests** and ensure they pass
7. **Submit a pull request** with detailed description

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 📝 Changelog

### Version 1.0.0 (2024-01-01)
**Initial Release**
- ✅ Complete fan control functionality
- ✅ Environmental sensors (temperature, humidity, air quality)
- ✅ Status monitoring (power, connection)
- ✅ Configuration flow for easy setup
- ✅ Data coordination and error handling
- ✅ Comprehensive documentation
- ✅ Translation support (English)
- ✅ Mock data for testing

### Planned Features
- 🔄 Real API integration with BlowControl devices
- 🔄 Multi-device support
- 🔄 Advanced scheduling features
- 🔄 Energy monitoring
- 🔄 Mobile app notifications
- 🔄 Voice assistant integration

## 📄 License

This project is licensed under the "Seems to Work" License (MIT-compatible) - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Home Assistant Community**: For the excellent integration framework
- **Dyson**: For creating amazing fan technology
- **Alex Odawa**: For the original BlowControl project and the "Seems to Work" License
- **Contributors**: Everyone who has contributed to this project

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this README and other docs
2. **Search Issues**: Look for similar issues in the GitHub repository
3. **Create Issue**: If you can't find a solution, create a detailed issue
4. **Community**: Ask for help in the Home Assistant community forums

### Issue Reporting

When reporting issues, please include:

- **Home Assistant Version**: Full version number
- **Integration Version**: Version of this integration
- **Error Messages**: Complete error messages from logs
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **System Information**: OS, Python version, etc.

### Contact

- **GitHub Issues**: [Create an issue](https://github.com/RoyalPineapple/blowcontrol-ha/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RoyalPineapple/blowcontrol-ha/discussions)
- **Email**: [Your email here]

---

**Made with ❤️ by the BlowControl Community**

*This integration is not officially affiliated with Dyson or BlowControl.* 