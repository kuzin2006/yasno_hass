from homeassistant.const import Platform


DOMAIN = "yasno_hass"

CONF_CITY = "city"
CONF_GROUPS = "groups"

YASNO_GROUPS = [
    "1.1",
    "1.2",
    "2.1",
    "2.2",
    "3.1",
    "3.2",
    "4.1",
    "4.2",
    "5.1",
    "5.2",
    "6.1",
    "6.2",
]
CITIES = ["kiev", "dnipro"]

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR]
