import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from .api import client as yasno_client
from . import const
from .models import (
    YasnoOutage,
    SensorEntityData,
    DailyGroupSchedule,
    YasnoDailySchedule,
)

_LOGGER = logging.getLogger(__name__)


class YasnoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="Yasno Power",
            update_interval=timedelta(seconds=30),
            always_update=True,
        )
        self._client = yasno_client

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        await self._async_update_data()

    async def _async_update_data(self):
        try:
            _LOGGER.debug("API data fetch.")
            return await self.hass.async_add_executor_job(self._client.update)
        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}") from e

    @staticmethod
    def _merge_intervals(group_schedule: list[YasnoOutage]) -> list[YasnoOutage]:
        """
        Merge sequential 0.5-hour intervals into one.
        TODO: group by outage type (if any, later)
        """
        merged_schedules = list()
        start_hour, end_hour = None, None
        for item in group_schedule:
            if item.start == end_hour:  # next item to be merged
                end_hour = item.end
            else:
                if start_hour and end_hour:
                    merged_schedules.append(
                        YasnoOutage(start=start_hour, end=end_hour, type=item.type)
                    )
                start_hour, end_hour = item.start, item.end
        else:
            if start_hour and end_hour:
                merged_schedules.append(
                    YasnoOutage(start=start_hour, end=end_hour, type=item.type)
                )
        return merged_schedules

    def city_schedules_for_group(self, city: str, group: str) -> SensorEntityData:
        """
        Return today/tomorrow schedule with merged intervals.
        :param city:
        :param group:
        :return: SensorEntityData
        """
        group_schedule_today, group_schedule_tomorrow = None, None

        if self.data:
            city_daily_schedule: YasnoDailySchedule = self.data[city]
            group_schedule_today = DailyGroupSchedule(
                title=city_daily_schedule.today.title,
                schedule=self._merge_intervals(city_daily_schedule.today.groups[group]),
            )
            if city_daily_schedule.tomorrow:
                group_schedule_tomorrow = (
                    DailyGroupSchedule(
                        title=city_daily_schedule.tomorrow.title,
                        schedule=self._merge_intervals(
                            city_daily_schedule.tomorrow.groups[group]
                        ),
                    )
                    if city_daily_schedule.tomorrow
                    else None
                )

        return SensorEntityData(
            group=group, today=group_schedule_today, tomorrow=group_schedule_tomorrow
        )


async def async_setup_entry(hass, entry: ConfigEntry) -> bool:
    """Set up a new entry."""
    _LOGGER.info("Setup Yasno Power entry started.")

    coordinator = YasnoCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, const.PLATFORMS)
    # entry.async_on_unload(entry.add_update_listener(coordinator.update_config))
    return True
