from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from enums.factory_enums import DownTimeEventStatusEnum, DownTimeEventTypeEnum, DownTimeSeverityEnum
from models.down_time_model import DownTimeEventModel
from errors.exceptions import NotFoundException


class DownTimeEventSimulator:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def generate_event(self, line_id, op_id, type: DownTimeEventTypeEnum, severity: DownTimeSeverityEnum | None = None) -> DownTimeEventModel | None :
        query = select(DownTimeEventModel).where(DownTimeEventModel.status == DownTimeEventStatusEnum.OPEN, DownTimeEventModel.production_line_id == line_id)
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        if events:
            return
        
        event_data = {
        "production_line_id": line_id,
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
    
    async def update_active_event_severity(self, line_id, severity: DownTimeSeverityEnum) -> DownTimeEventModel:
        query = select(DownTimeEventModel).where(DownTimeEventModel.production_line_id == line_id, DownTimeEventModel.status == DownTimeEventStatusEnum.OPEN)
        result = await self.db.execute(query)
        event = result.scalars().first()
        
        if not event:
            raise NotFoundException("evento")
        
        event.severity = severity
        
        await self.db.commit()
        await self.db.refresh(event)
        
        return event
    
    async def close_active_event(self, line_id):
        query = select(DownTimeEventModel).where(DownTimeEventModel.production_line_id == line_id, DownTimeEventModel.status == DownTimeEventStatusEnum.OPEN)
        result = await self.db.execute(query)
        event = result.scalars().first()
        
        if not event:
            raise NotFoundException("Evento")
        
        end_time = datetime.now(timezone.utc)
        duration_minutes = (end_time - event.start_time).total_seconds() / 60
        
        event.status = DownTimeEventStatusEnum.CLOSE
        event.end_time = end_time
        event.duration = duration_minutes
     
        await self.db.commit()
        await self.db.refresh(event)