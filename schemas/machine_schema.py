from datetime import datetime

from pydantic import BaseModel


class MachineRequestSchema(BaseModel):
    name: str
    base_failure_rate: float
    

class MachineResponseSchema(BaseModel):
    id: int
    name: str
    code: str
    base_failure_rate: float
    wear_level: float
    production_line_id: int | None
    last_start_time: datetime | None
    last_stop_time: datetime | None
    last_maintenance_date: datetime | None
    
    model_config = {
        "from_attributes": True
    }
    
    
class MachineUpdateSchema(BaseModel):
    name: str
    base_failure_rate: float