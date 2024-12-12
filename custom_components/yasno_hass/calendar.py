# Home Assistant Yasno Power Outages Sensor

import logging
from datetime import datetime, timedelta

from homeassistant.core import callback
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_utils

from .const import CONF_GROUPS, CONF_CITY

from .models import DailyGroupSchedule, SensorEntityData, YasnoOutage


_LOGGER = logging.getLogger(__name__)


class YasnoCalendarEntity(CoordinatorEntity, CalendarEntity):
    """Representation of a Binary Sensor based on today outages schedule."""

    def __init__(self, coordinator, city, group, today: bool = True):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._today = today
        self._name = "yasno_power"
        self.city = city
        self.group = group
        self._schedule: DailyGroupSchedule = DailyGroupSchedule()

        self._attr_unique_id = (
            f"yasno_calendar_{'today' if today else 'tomorrow'}_{city}_group_{group}"
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Runtime data update.")
        runtime_data: SensorEntityData = self.coordinator.city_schedules_for_group(
            self.city, self.group
        )
        self._schedule: SensorEntityData = (
            runtime_data.today if self._today else runtime_data.tomorrow
        ) or DailyGroupSchedule()
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name}_{'today' if self._today else 'tomorrow'}_{self.city}_group_{self.group}"  # `calendar.yasno_power_today_kiev_group_2`

    @property
    def available(self) -> bool:
        return self._schedule.title != "Data unavailable"

    def _to_event(self, outage: YasnoOutage) -> CalendarEvent:
        now = dt_utils.now()
        start_date = now.replace(hour=outage.start, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=outage.end, minute=0, second=0, microsecond=0)

        if not self._today:
            start_date += timedelta(days=1)
            end_date += timedelta(days=1)
        return CalendarEvent(start=start_date, end=end_date, summary="Outage")

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current event."""
        for outage in self._schedule.schedule:
            if outage.start <= dt_utils.now().hour <= outage.end:
                return self._to_event(outage)
        return None

    async def async_get_events(
        self,
        hass,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return [self._to_event(outage) for outage in self._schedule.schedule]

    @property
    def extra_state_attributes(self):
        """attributes"""
        return {
            "title": self._schedule.title,
            "city": self.city,
            "group": self.group,
        }


async def async_setup_entry(
    hass,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Yasno outages calendar platform."""
    city = config_entry.data.get(CONF_CITY)
    groups = config_entry.data.get(CONF_GROUPS)
    coordinator = config_entry.runtime_data

    calendars = list()
    for group in groups:
        _LOGGER.debug(f"Setup calendar entry for {city} group {group}")
        calendars.extend(
            [
                YasnoCalendarEntity(coordinator, city=city, group=group),
                YasnoCalendarEntity(coordinator, city=city, group=group, today=False),
            ]
        )
    _LOGGER.debug(groups)

    async_add_entities(calendars)
    _LOGGER.debug(
        f"Setup of Yasno calendars is done. {len(calendars)} calendars added."
    )
