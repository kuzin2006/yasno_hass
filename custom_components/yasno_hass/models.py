# Data models
from typing import List, Optional, Annotated
from enum import StrEnum
from datetime import datetime, date
from pydantic import BaseModel
import re
import logging

from pydantic.functional_validators import AfterValidator

from homeassistant.components.calendar import CalendarEvent

_LOGGER = logging.getLogger(__name__)


class YasnoOutageType(StrEnum):
    OFF = "DEFINITE_OUTAGE"


class YasnoAPIOutage(BaseModel):
    start: float
    end: float
    type: YasnoOutageType


class YasnoDailyScheduleEntity(BaseModel):
    title: str
    groups: dict[str, List[YasnoAPIOutage]]


class YasnoDailySchedule(BaseModel):
    today: Optional[YasnoDailyScheduleEntity] = None
    tomorrow: Optional[YasnoDailyScheduleEntity] = None


def is_unix_timestamp(v: int) -> int:
    assert v > 0, f"'{v}' is not unix timestamp."
    return v


UnixTimestamp = Annotated[int, AfterValidator(is_unix_timestamp)]


class YasnoAPIComponent(BaseModel):
    template_name: str
    available_regions: List[str] = list()
    title: Optional[str] = None
    lastRegistryUpdateTime: Optional[UnixTimestamp] = 0
    dailySchedule: Optional[dict[str, YasnoDailySchedule]] = dict()

    @property
    def date_title_today(self) -> date | None:
        if not self.dailySchedule:
            return None

        schedule_title_today = self.dailySchedule["kiev"].today
        # Sample title: "Понеділок, 25.12.2024 на 00:58"
        pattern = r"\d{2}\.\d{2}\.\d{4}"
        match = re.search(pattern, schedule_title_today.title)

        if match:
            title_date = match.group()
            _LOGGER.debug(f"Date found in title: {title_date}")
            return datetime.strptime(title_date, "%d.%m.%Y").date()

        return None

    @property
    def deprecated(self) -> bool:
        return datetime.now().date() != self.date_title_today


class YasnoAPIResponse(BaseModel):
    components: List[YasnoAPIComponent] = list()


class YasnoOutage(YasnoAPIOutage):
    start: datetime
    end: datetime


class DailyGroupSchedule(BaseModel):
    title: str = "Data unavailable"
    schedule: List[YasnoOutage] = list()


class SensorEntityData(BaseModel):
    group: str
    today: Optional[DailyGroupSchedule]
    tomorrow: Optional[DailyGroupSchedule]


class YasnoCalendarEvent(CalendarEvent):
    def __init__(self, *args, **kwargs):
        kwargs["summary"] = "Outage"
        super().__init__(*args, **kwargs)
