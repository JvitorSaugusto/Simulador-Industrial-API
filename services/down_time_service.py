
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.factory_enums import DownTimeEventStatusEnum, DownTimeEventTypeEnum
from errors.exceptions import NotFoundException
from models.down_time_model import DownTimeEventModel
from schemas.down_time_schema import DownTimeUpdateSchema


class DownTimeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_down_time_event(self, line_id: int, type: DownTimeEventTypeEnum):
        # Vai ser chamado no machine service na mudança de status == STOP || MAINTENANCE
        start_time = datetime.now(timezone.utc)
        new_event = DownTimeEventModel(
            line_id=line_id,
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
        event.status = DownTimeEventStatusEnum.CLOSE
        
        await self.db.commit()
        await self.db.refresh(event)
        
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
        