from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.dashboard_service import DashboardService
from schemas.dashboard_schema import LineSnapshotSchema


router = APIRouter()

def get_dashboard_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DashboardService:
    return DashboardService(db)

ServiceDependency = Annotated[DashboardService, Depends(get_dashboard_service)]


@router.get("/{line_id}", status_code=200, response_model=LineSnapshotSchema)
async def get_dashboard_snapshot(line_id: int, service: ServiceDependency):
    return service.get_line_snapshot(line_id=line_id)