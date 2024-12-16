import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_utils


from .api import client as yasno_client
from . import const
from .models import (
    YasnoAPIOutage,
    SensorEntityData,
    DailyGroupSchedule,
    YasnoDailySchedule,
    YasnoOutage,
    YasnoOutageType,
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
                schedule=_merge_intervals(
                    city_daily_schedule.today.groups[group],
                    today=True,
                ),
            )
            if city_daily_schedule.tomorrow:
                group_schedule_tomorrow = (
                    DailyGroupSchedule(
                        title=city_daily_schedule.tomorrow.title,
                        schedule=_merge_intervals(
                            city_daily_schedule.tomorrow.groups[group],
                            today=False,
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


def _to_datetime(val: float):
    time_parts = [int(i) for i in str(val).split(".")]
    assert len(time_parts) == 2, "Incorrect time input."

    return dt_utils.now().replace(
        hour=time_parts[0], minute=30 if time_parts[1] else 0, second=0, microsecond=0
    )


def _to_outage(
    start: float, end: float, today: bool, type: YasnoOutageType
) -> YasnoOutage:
    start_dt = _to_datetime(start)
    end_dt = _to_datetime(end)
    if not today:
        start_dt += timedelta(days=1)
        end_dt += timedelta(days=1)
    return YasnoOutage(
        start=start_dt,
        end=end_dt,
        type=type,
    )


def _merge_intervals(
    group_schedule: list[YasnoAPIOutage], today: bool
) -> list[YasnoAPIOutage]:
    """
    Merge sequential intervals into one.
    TODO: group by outage type (if any, later)
    """
    merged_schedules = list()
    start, end = None, None
    for item in group_schedule:
        if item.start == end:  # next item to be merged
            end = item.end
        else:
            if start and end:
                merged_schedules.append(
                    _to_outage(start=start, end=end, today=today, type=item.type)
                )
            start, end = item.start, item.end

    else:
        if start and end:
            merged_schedules.append(
                _to_outage(start=start, end=end, today=today, type=item.type)
            )
    return merged_schedules
