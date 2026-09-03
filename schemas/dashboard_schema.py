from datetime import datetime
from typing import List

from pydantic import BaseModel
from enums.factory_enums import LineStatusEnum, MachineStatusEnum, ProductionOrderEnum


class MachineSnapshotSchema(BaseModel):
    id: int
    name: str
    base_failure_rate: float
    wear_level: float
    last_start_time: datetime | None
    last_stop_time: datetime | None
    maintenance_start_at: datetime | None
    maintenance_end_at: datetime | None
    status: MachineStatusEnum
    
    model_config = {
        "from_attributes": True
    }
    
    
class OpSnapshotSchema(BaseModel):
    id: int
    code: str
    product_name: str
    quantity_planned: int
    quantity_produced: int
    quantity_good: int
    quantity_bad: int
    status: ProductionOrderEnum
    planned_start: datetime
    planned_end: datetime
    actual_start: datetime | None
    actual_end: datetime | None
    
    @property
    def progress_percentage(self) -> float:
        if self.quantity_planned == 0:
            return 0.0
        return round((self.quantity_produced / self.quantity_planned) * 100, 2)
    
    model_config = {
        "from_attributes": True
    }
    
    
class LineSnapshotSchema(BaseModel):
    id: int
    name: str
    target_oee: float
    ideal_production_rate: float
    current_production_rate: float
    total_runtime_minutes: int
    simulation_status: LineStatusEnum
    
    machines: List[MachineSnapshotSchema] = []
    active_op: OpSnapshotSchema | None = None
    
    model_config = {
        "from_attributes": True
    }