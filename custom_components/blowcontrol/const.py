"""Constants for the BlowControl integration."""

DOMAIN = "blowcontrol"

# Configuration keys
CONF_HOST = "host"
CONF_NAME = "name"
CONF_DEVICE_ID = "device_id"

# Default values
DEFAULT_NAME = "BlowControl Fan"
DEFAULT_SCAN_INTERVAL = 30

# Device states
STATE_ON = "on"
STATE_OFF = "off"

# Fan speeds
FAN_SPEED_OFF = 0
FAN_SPEED_LOW = 1
FAN_SPEED_MEDIUM = 2
FAN_SPEED_HIGH = 3
FAN_SPEED_MAX = 4

# Fan speed names
FAN_SPEED_NAMES = {
    FAN_SPEED_OFF: "Off",
    FAN_SPEED_LOW: "Low",
    FAN_SPEED_MEDIUM: "Medium", 
    FAN_SPEED_HIGH: "High",
    FAN_SPEED_MAX: "Max"
}

# Fan speed percentages
FAN_SPEED_PERCENTAGES = {
    FAN_SPEED_OFF: 0,
    FAN_SPEED_LOW: 25,
    FAN_SPEED_MEDIUM: 50,
    FAN_SPEED_HIGH: 75,
    FAN_SPEED_MAX: 100
}
