from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from enums.production_line_enums import LineStatusEnum
from schemas.production_line_schema import ProductionLineRequestSchema, ProductionLineUpdateSchema
from models.production_line_model import ProductionLineModel


class ProductionLineService:
    def __init__(self, db: AsyncSession):
        self.db = db
    

    async def create_production_line(self, payload: ProductionLineRequestSchema) -> ProductionLineModel:
        new_production_line = ProductionLineModel(**payload.model_dump())
        
        self.db.add(new_production_line)
        await self.db.commit()
        await self.db.refresh(new_production_line)
        
        return new_production_line
    
    async def list_all_production_line(self, status: LineStatusEnum | None = None) -> Sequence[ProductionLineModel]:
        query = select(ProductionLineModel)
        
        if status:
            query = query.where(ProductionLineModel.status == status)
        
        result = await self.db.execute(query)
        production_lines = result.scalars().all()
    
        return production_lines
    
    async def get_details_line(self, line_id: int) -> ProductionLineModel | None:    
        return await self.db.get(ProductionLineModel, line_id)
    
    async def update_line(self, line_id: int, payload: ProductionLineUpdateSchema) -> ProductionLineModel | None:
        line_data = await self.db.get(ProductionLineModel, line_id)
        
        if not line_data:
            return None
        
        update_data = payload.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(line_data, field, value)
            
        await self.db.commit()
        await self.db.refresh(line_data)
        
        return line_data
    
    async def delete_line(self, line_id: int) -> bool:
        line = await self.db.get(ProductionLineModel, line_id)
        
        if line:
            await self.db.delete(line)
            await self.db.commit()
            return True
        return False