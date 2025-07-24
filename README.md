# BlowControl Home Assistant Integration

A Home Assistant integration for controlling Dyson fans through the BlowControl system.

## Features

- **Fan Control**: Full fan control including speed adjustment, on/off, oscillation, and direction
- **Environmental Sensors**: Temperature, humidity, and air quality monitoring
- **Status Monitoring**: Power status and connection monitoring
- **Easy Setup**: Simple configuration through Home Assistant UI

## Installation

### Method 1: HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Search for "BlowControl" in the integrations section
4. Click "Download"
5. Restart Home Assistant

### Method 2: Manual Installation

1. Download this repository
2. Copy the `custom_components/blowcontrol` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **BlowControl**
4. Enter your BlowControl device's IP address and optional name
5. Click **Submit**

## Entities

The integration creates the following entities:

### Fan Entity
- **BlowControl Fan**: Main fan control entity
  - Speed control (0-100%)
  - Oscillation control
  - Direction control
  - On/Off control

### Binary Sensors
- **BlowControl Power**: Shows if the fan is powered on
- **BlowControl Connected**: Shows connection status to the device

### Sensors
- **BlowControl Temperature**: Current temperature reading
- **BlowControl Humidity**: Current humidity percentage
- **BlowControl Air Quality**: Air quality measurement (PM2.5)
- **BlowControl Fan Speed**: Current fan speed in RPM

## Usage

### Automations

You can create automations to control your fan based on various conditions:

```yaml
# Turn on fan when temperature is high
automation:
  - alias: "Turn on fan when hot"
    trigger:
      platform: numeric_state
      entity_id: sensor.blowcontrol_temperature
      above: 25
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.blowcontrol_fan
      - service: fan.set_percentage
        target:
          entity_id: fan.blowcontrol_fan
        data:
          percentage: 75
```

### Scripts

Create scripts for common fan operations:

```yaml
# Night mode script
script:
  night_mode:
    sequence:
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

## Troubleshooting

### Connection Issues
- Ensure your BlowControl device is on the same network as Home Assistant
- Verify the IP address is correct
- Check that the BlowControl service is running

### Entity Not Appearing
- Restart Home Assistant after installation
- Check the Home Assistant logs for any error messages
- Verify the integration is properly configured

### Fan Not Responding
- Check the connection status binary sensor
- Verify the fan is powered on
- Check the BlowControl device logs

## Development

This integration is open source. Contributions are welcome!

### Local Development
1. Clone this repository
2. Copy the `custom_components/blowcontrol` folder to your Home Assistant config
3. Make your changes
4. Restart Home Assistant to test

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

## Changelog

### Version 1.0.0
- Initial release
- Basic fan control functionality
- Environmental sensors
- Status monitoring
- Configuration flow 