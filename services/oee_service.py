from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.oee_model import OeeRecordModel
from models.production_order_model import ProductionOrderModel


class OeeRecordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
        
    def disponibility(self, oee_id: int):
        stmt = (
            select(OeeRecordModel)
            .options(joinedload(OeeRecordModel.production_line_id))
        )