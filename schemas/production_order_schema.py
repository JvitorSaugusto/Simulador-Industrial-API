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
    actual_start: datetime
    actual_end: datetime
    production_line_id: int
    
    
class ProductionOrderUpdateSchema(BaseModel):
    product_name: str
    quantity_planned: int
    status: ProductionOrderEnum
    planned_start: datetime
    planned_end: datetime