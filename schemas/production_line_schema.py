from pydantic import BaseModel
from decimal import Decimal


class ProductionLineRequestSchema(BaseModel):
    name: str
    description: str
    target_oee: Decimal
    ideal_production_rate: float


class ProductionLineResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None
    target_oee: Decimal
    ideal_production_rate: float
    current_production_rate: float
    production_rate: float
    total_runtime_minutes: int
    
    model_config = {
        "from_attributes": True
    }
    
class ProductionLineUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    target_oee: Decimal | None = None
    ideal_production_rate: float | None = None