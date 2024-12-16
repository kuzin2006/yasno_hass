import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, ConfigEntry
from typing import Any
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from . import const


_LOGGER = logging.getLogger(__name__)


def get_config_value(
    entry: ConfigEntry | None,
    key: str,
    default: Any = None,
) -> Any:
    """Get a value from the config entry or default."""
    if entry is not None:
        return entry.options.get(key, entry.data.get(key, default))
    return default


class YasnoConfigFlow(ConfigFlow, domain=const.DOMAIN):
    # TODO - translations
    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        super().__init__()
        self.data = dict()

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id("yasno_power_outage_integration")

        if user_input is not None:
            _LOGGER.debug("User input: %s", user_input)
            self.data.update(user_input)
            return self.async_create_entry(title="Yasno Power", data=self.data)

        data_schema = {
            vol.Required(const.CONF_CITY): SelectSelector(
                SelectSelectorConfig(
                    options=const.CITIES,
                    translation_key="city",
                ),
            ),
            vol.Required(const.CONF_GROUPS): SelectSelector(
                SelectSelectorConfig(
                    options=const.YASNO_GROUPS,
                    translation_key="group",
                    multiple=True,
                    mode=SelectSelectorMode.DROPDOWN,
                ),
            ),
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))
