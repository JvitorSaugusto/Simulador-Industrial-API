from pydantic import BaseModel


class ProductionLineRequestSchema(BaseModel):
    name: str
    description: str
    target_oee: float
    ideal_production_rate: float


class ProductionLineResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None
    target_oee: float
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
    target_oee: float | None = None
    ideal_production_rate: float | None = None