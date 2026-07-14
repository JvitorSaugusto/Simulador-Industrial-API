from datetime import datetime, timezone
from typing import Sequence
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from enums.factory_enums import ProductionOrderEnum
from errors.errors_domain.production_order_errors import ProductionOrderInvalidStatusException
from errors.exceptions import NotFoundException
from models.production_order_model import ProductionOrderModel
from schemas.production_order_schema import ProductionOrderRequestSchema, ProductionOrderUpdateSchema


class ProductionOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    def _validate_op_status(self, op_data: ProductionOrderModel, current_status: str, new_status: str):
        if current_status == ProductionOrderEnum.PENDING and new_status == ProductionOrderEnum.FINISHED:
                raise ProductionOrderInvalidStatusException(op_data.code)
            
        if new_status == ProductionOrderEnum.PRODUCTION:
            op_data.actual_start = datetime.now(timezone.utc)
        elif new_status == ProductionOrderEnum.FINISHED:
            op_data.actual_end = datetime.now(timezone.utc)
            
        return op_data
        
    async def create_op(self, payload: ProductionOrderRequestSchema) -> ProductionOrderModel:
        new_op = ProductionOrderModel(**payload.model_dump())
        unique_hash = uuid.uuid4().hex[:8].upper()
        new_op.code = f"OP-{unique_hash}"
        
        self.db.add(new_op)
        await self.db.commit()
        await self.db.refresh(new_op)
        
        return new_op
    
    async def list_ops(self) -> Sequence[ProductionOrderModel]:
        query = select(ProductionOrderModel)
        result = await self.db.execute(query)
        ops = result.scalars().all()

        return ops
    
    async def get_detail_op(self, op_id: int) -> ProductionOrderModel | None:
        op = await self.db.get(ProductionOrderModel, op_id)
        
        if not op:
            raise NotFoundException("Ordem de Produção")
        return op
    
    async def update_op(self, payload: ProductionOrderUpdateSchema, op_id: int) -> ProductionOrderModel | None:
        op_data = await self.db.get(ProductionOrderModel, op_id)
        updated_data = payload.model_dump(exclude_unset=True)
        
        if not op_data:
            raise NotFoundException("Ordem de Produção")
        
        current_status = op_data.status
        
        new_status = updated_data.get("status", current_status)
        
        for key, value in updated_data.items():
            if key == "status":
                new_status = value

        op_data = self._validate_op_status(op_data=op_data, current_status=current_status, new_status=new_status)
            
        for key, value in updated_data.items():
            setattr(op_data, key, value)
        
        await self.db.commit()
        await self.db.refresh(op_data)
        
        return op_data
    
    async def delete_op(self, op_id: int) -> bool:
        op = await self.db.get(ProductionOrderModel, op_id)
        
        if op:
            await self.db.delete(op)
            await self.db.commit()
            return True
        return False
        
        