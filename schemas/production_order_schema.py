from datetime import datetime

from pydantic import BaseModel

from enums.factory_enums import ProductionOrderEnum


class ProductionOrderRequestSchema(BaseModel):
    product_name: str
    quantity_planned: int
    planned_start: datetime
    planned_end: datetime
    

class ProductionOrderResponseSchema(BaseModel):
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
    production_line_id: int
    
    model_config = {
        "from_attributes": True
    }
    
class ProductionOrderUpdateSchema(BaseModel):
    product_name: str | None = None
    quantity_planned: int | None = None
    status: ProductionOrderEnum | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None