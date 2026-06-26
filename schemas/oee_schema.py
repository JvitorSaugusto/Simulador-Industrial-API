from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OeeRecordResponseSerializer(BaseModel):
    id: int
    production_order_id: int
    production_line_id: int
    availability: Decimal
    perfomance: Decimal
    quality: Decimal
    oee: Decimal
    start_period: datetime
    end_period: datetime
    create_at: datetime