from enums.factory_enums import DownTimeEventTypeEnum, MachineStatusEnum
from typing import Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from errors.exceptions import NotFoundException
from models.machine_model import MachineModel
from schemas.machine_schema import MachineRequestSchema, MachineUpdateSchema
from services.down_time_service import DownTimeService


class MachineService:
    def __init__(self, db: AsyncSession, downtime_service: DownTimeService):
        self.db = db
        self.downtime_service = downtime_service
        

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
        machine = await self.db.get(MachineModel, machine_id)
        
        if not machine:
            raise NotFoundException("Máquina")
        return machine

    async def update_machine(self, payload: MachineUpdateSchema, machine_id: int) -> MachineModel | None:
        machine_data = await self.db.get(MachineModel, machine_id)

        if not machine_data:
            raise NotFoundException("Máquina")

        updated_data = payload.model_dump(exclude_unset=True)

        for key, value in updated_data.items():
            setattr(machine_data, key, value)
            
        if machine_data.status == MachineStatusEnum.STOP:
            await self.downtime_service.create_down_time_event(machine_id=machine_data.id, type=DownTimeEventTypeEnum.FAILURE)
        elif machine_data.status == MachineStatusEnum.MAINTENANCE:
            await self.downtime_service.create_down_time_event(machine_id=machine_data.id, type=DownTimeEventTypeEnum.PREVENTIVE)
               
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
    
    async def get_all_machines_by_line(self, line_id) -> Sequence[MachineModel]:
        query = select(MachineModel).where(MachineModel.production_line_id == line_id)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        return machines