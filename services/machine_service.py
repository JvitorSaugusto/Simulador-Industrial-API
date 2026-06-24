from typing import Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.machine_models import MachineModel
from schemas.machine_schema import MachineRequestSchema, MachineUpdateSchema


class MachineService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_machine(self, payload: MachineRequestSchema) -> MachineModel:
        new_machine_data = MachineModel(**payload.model_dump())
        unique_hash = uuid.uuid4().hex[:8].upper()
        new_machine_data.code = f"MAC-{unique_hash}"
        
        self.db.add(new_machine_data)
        await self.db.commit()
        await self.db.refresh(new_machine_data)
        
        return new_machine_data
    
    async def list_machines(self) -> Sequence[MachineModel]:
        query = select(MachineModel)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        return machines
    
    async def get_details_machine(self, machine_id: int) -> MachineModel | None:
        return await self.db.get(MachineModel, machine_id)
    
    async def update_machine(self, payload: MachineUpdateSchema, machine_id: int) -> MachineModel | None:
        machine_data = await self.db.get(MachineModel, machine_id)
        updated_data = payload.model_dump(exclude_unset=True)
        
        for key, value in updated_data:
            setattr(machine_data, key, value)
            
        await self.db.commit()
        await self.db.refresh(machine_data)
        
        return machine_data
    
    async def delete_machine(self, machine_id: int) -> bool:
        machine_data = await self.db.get(MachineModel, machine_id)
        
        if machine_data:
            await self.db.delete(machine_data)
            await self.db.commit()
            return True
        return False