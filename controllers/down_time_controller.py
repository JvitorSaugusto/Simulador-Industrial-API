from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.down_time_schema import DownTimeResponseSchema, DownTimeUpdateSchema
from services.down_time_service import DownTimeService


router = APIRouter()

def get_down_time_service(db: AsyncSession = Depends(get_db)) -> DownTimeService:
    return DownTimeService(db)


@router.put("/{event_id}", response_model=DownTimeResponseSchema, status_code=200)
async def justify_down_time_event(payload: DownTimeUpdateSchema, event_id: int, service: DownTimeService = Depends(get_down_time_service)):
    return await service.justify_down_time_event(payload=payload, event_id=event_id)

@router.delete("/{event_id}", status_code=200)
async def delete_down_time_event(event_id: int, service: DownTimeService = Depends(get_down_time_service)):
    return await service.delete_down_time_event(event_id=event_id)