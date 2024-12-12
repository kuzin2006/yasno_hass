from homeassistant.const import Platform


DOMAIN = "yasno_hass"

CONF_CITY = "city"
CONF_GROUPS = "groups"

YASNO_GROUPS = 6
CITIES = ["kiev", "dnipro"]

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR]
