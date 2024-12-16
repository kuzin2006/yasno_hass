# Home Assistant Yasno Power Outages Sensor

import logging

from homeassistant.core import callback
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.util import dt as dt_utils
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_GROUPS, CONF_CITY

from .models import DailyGroupSchedule, SensorEntityData


_LOGGER = logging.getLogger(__name__)


class YasnoBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Binary Sensor based on today outages schedule."""

    _attr_device_class = BinarySensorDeviceClass.POWER

    def __init__(self, coordinator, city, group):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._name = "yasno_power_today"
        self.city = city
        self.group = group
        self._schedule: DailyGroupSchedule = DailyGroupSchedule()

        self._attr_unique_id = f"yasno_binary_sensor_{city}_group_{group}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"Runtime data update for {self.name}.")
        runtime_data: SensorEntityData = self.coordinator.city_schedules_for_group(
            self.city, self.group
        )
        self._schedule: DailyGroupSchedule = runtime_data.today or DailyGroupSchedule()
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name}_{self.city}_group_{self.group}"  # `binary_sensor.yasno_power_today_kiev_group_2`

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        for outage in self._schedule.schedule:
            if outage.start <= dt_utils.now() <= outage.end:
                return False
        return True

    @property
    def available(self) -> bool:
        return self._schedule.title != "Data unavailable"

    @staticmethod
    def _to_time_range_str(event):
        return f"{event.start.strftime('%H:%M')}...{event.end.strftime('%H:%M')}"

    @property
    def extra_state_attributes(self):
        """attributes"""
        current_outage = "No outage"
        if not self.is_on:
            current_outage_event = [
                outage
                for outage in self._schedule.schedule
                if outage.start <= dt_utils.now() <= outage.end
            ]

            if current_outage_event:
                current_outage = self._to_time_range_str(current_outage_event[0])
            else:
                current_outage = "Undefined"

        next_outage_event = [
            outage
            for outage in self._schedule.schedule
            if outage.start > dt_utils.now()
        ]
        if not next_outage_event:
            next_outage = "Not today"
        else:
            next_outage = self._to_time_range_str(next_outage_event[0])

        return {
            "title": self._schedule.title,
            "city": self.city,
            "group": self.group,
            "current": current_outage,
            "next": next_outage,
        }


async def async_setup_entry(
    hass,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Yasno outages binary_sensor platform."""
    city = config_entry.data.get(CONF_CITY)
    groups = config_entry.data.get(CONF_GROUPS)
    coordinator = config_entry.runtime_data
    _LOGGER.debug(
        f"Setup new binary_sensors: city - {city}, group(s) - {', '.join(groups)}"
    )

    binary_sensors = [
        YasnoBinarySensorEntity(coordinator, city=city, group=group) for group in groups
    ]

    async_add_entities(binary_sensors)
    _LOGGER.debug(
        f"Setup of Yasno binary sensors is done. {len(binary_sensors)} binary sensors added."
    )
