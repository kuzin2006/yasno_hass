# Data models
from typing import List, Optional
from enum import StrEnum
from pydantic import BaseModel


class YasnoOutageType(StrEnum):
    OFF = "DEFINITE_OUTAGE"


class YasnoOutage(BaseModel):
    start: int
    end: int
    type: YasnoOutageType


class YasnoDailyScheduleEntity(BaseModel):
    title: str
    groups: dict[str, List[YasnoOutage]]


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


class DailyGroupSchedule(BaseModel):
    title: str = "Data unavailable"
    schedule: List[YasnoOutage] = list()


class SensorEntityData(BaseModel):
    group: int
    today: DailyGroupSchedule
    tomorrow: Optional[DailyGroupSchedule]
