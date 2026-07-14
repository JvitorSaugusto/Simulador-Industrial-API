
from datetime import datetime, timezone
import random

from certifi import where
from pydantic_extra_types.pendulum_dt import Duration
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.factory_enums import DownTimeEventStatusEnum, DownTimeEventTypeEnum, DownTimeSeverityEnum
from errors.exceptions import NotFoundException
from models.down_time_model import DownTimeEventModel
from models.machine_model import MachineModel
from schemas.down_time_schema import DownTimeUpdateSchema


class DownTimeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_down_time_event(self, machine_id: int, type: DownTimeEventTypeEnum):
        # Vai ser chamado no machine service na mudança de status == STOP || MAINTENANCE
        start_time = datetime.now(timezone.utc)
        new_event = DownTimeEventModel(
            machine_id=machine_id,
            type=type,
            start_time=start_time,
            reason="Não classificada"
        )
        
        self.db.add(new_event)
        return new_event
    
    async def close_down_time_event(self, event_id: int, start_time: datetime):
        # Vai ser chamado no machine service na SAIDA DO status == PRODUCTION || MAINTENANCE
        end_time = datetime.now(timezone.utc)
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        event = await self.db.get(DownTimeEventModel, event_id)
        
        if not event:
            raise NotFoundException("Evento")
        
        event.end_time = end_time
        event.duration = duration_minutes
        
        self.db.add(event)
        
        return f"Evento fechado com a duração de: {duration_minutes} minutos"
        
        
    async def justify_down_time_event(self, payload: DownTimeUpdateSchema, event_id: int) -> DownTimeEventModel:
        update_data = payload.model_dump(exclude_unset=True)
        event_data = await self.db.get(DownTimeEventModel, event_id)
        
        if not event_data:
            raise NotFoundException("Evento")
        
        for key, value in update_data.items():
            setattr(event_data, key, value)
            
        await self.db.commit()
        await self.db.refresh(event_data)
        
        return event_data
    
    async def delete_down_time_event(self, event_id: int) -> bool:
        event_data = await self.db.get(DownTimeEventModel, event_id)
        
        if event_data:
            await self.db.delete(event_data)
            await self.db.commit()
            return True
        return False
    
    def generate_event(self, machine_id, op_id, type: DownTimeEventTypeEnum, severity: DownTimeSeverityEnum | None = None) -> DownTimeEventModel:
        event_data = {
        "machine_id": machine_id,
        "production_order_id": op_id,
        "type": type,
        "reason": "Parada operacional genérica"
        }

        if type == DownTimeEventTypeEnum.FAILURE:
            event_data["severity"] = severity
            event_data["reason"] = "Favor preencher após manutenção"
            event_data["start_time"] = datetime.now(timezone.utc)

        event = DownTimeEventModel(**event_data)
        
        self.db.add(event)
        
        return event
    
    async def update_active_event_severity(self, machine_id, severity: DownTimeSeverityEnum) -> DownTimeEventModel:
        query = select(DownTimeEventModel).where(DownTimeEventModel.machine_id == machine_id and DownTimeEventModel.status == DownTimeEventStatusEnum.OPEN)
        result = await self.db.execute(query)
        event = result.scalars().first()
        
        if not event:
            raise NotFoundException("evento")
        
        event.severity = severity
        
        await self.db.commit()
        await self.db.refresh(event)
        
        return event
        
    async def close_active_event(self, machine_id):
        query = select(DownTimeEventModel).where(DownTimeEventModel.machine_id == machine_id and DownTimeEventModel.status == DownTimeEventStatusEnum.OPEN)
        result = await self.db.execute(query)
        event = result.scalars().first()
        
        if not event:
            raise NotFoundException("evento")
        
        event.status = DownTimeEventStatusEnum.CLOSE
        
        await self.db.commit()
        await self.db.refresh(event)
        