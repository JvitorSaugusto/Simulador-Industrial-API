from datetime import datetime

from pydantic import BaseModel
from enums.factory_enums import MachineStatusEnum


class MachineRequestSchema(BaseModel):
    name: str
    base_failure_rate: float
    

class MachineResponseSchema(BaseModel):
    id: int
    name: str
    code: str
    base_failure_rate: float
    wear_level: float
    production_line_id: int
    last_start_time: datetime | None
    last_stop_time: datetime | None
    maintenance_start_at: datetime | None
    maintenance_end_at: datetime | None
    status: MachineStatusEnum
    
    model_config = {
        "from_attributes": True
    }
    
    
class MachineUpdateSchema(BaseModel):
    name: str | None = None
    base_failure_rate: float | None = None
    status: MachineStatusEnum | None = None
