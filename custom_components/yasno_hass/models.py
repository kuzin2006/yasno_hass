# Data models
from typing import List, Optional
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel

from homeassistant.components.calendar import CalendarEvent


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
    today: YasnoDailyScheduleEntity
    tomorrow: Optional[YasnoDailyScheduleEntity] = None


class YasnoAPIComponent(BaseModel):
    template_name: str
    available_regions: List[str] = list()
    title: Optional[str] = None
    lastRegistryUpdateTime: Optional[int] = 0
    dailySchedule: Optional[dict[str, YasnoDailySchedule]] = dict()


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
    today: DailyGroupSchedule
    tomorrow: Optional[DailyGroupSchedule]


class YasnoCalendarEvent(CalendarEvent):
    def __init__(self, *args, **kwargs):
        kwargs["summary"] = "Outage"
        super().__init__(*args, **kwargs)
