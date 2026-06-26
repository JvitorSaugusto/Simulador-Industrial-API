from datetime import datetime

from pydantic import BaseModel

from enums.factory_enums import DownTimeEventTypeEnum, DownTimeSeverityEnum


class DownTimeResponseSchema(BaseModel):
    id: int
    machine_id: int
    start_time: datetime
    end_time: datetime | None
    duration_minutes: float | None
    reason: str
    comment: str | None
    type: DownTimeEventTypeEnum
    severity: DownTimeSeverityEnum
    
    model_config = {
        "from_attributes": True
    }
    

class DownTimeUpdateSchema(BaseModel):
    reason: str | None = None
    comment: str | None = None