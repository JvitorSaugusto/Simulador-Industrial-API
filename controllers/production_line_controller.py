from typing import Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from enums.production_line_enums import LineStatusEnum
from services.production_line_service import ProductionLineService
from schemas.production_line_schema import ProductionLineRequestSchema, ProductionLineResponseSchema



router = APIRouter()

def get_production_line_service(db: AsyncSession = Depends(get_db)) -> ProductionLineService:
    return ProductionLineService(db)

@router.post("/", response_model=ProductionLineResponseSchema, status_code=201)
async def create_production_line(payload: ProductionLineRequestSchema, service: ProductionLineService = Depends(get_production_line_service)):
    return service.create_production_line(payload)

@router.get("/", response_model=Sequence[ProductionLineResponseSchema])
async def get_all_lines(status: LineStatusEnum | None = Query(None, description="Filtrar linhas por status"), service: ProductionLineService = Depends(get_production_line_service)):
    return service.list_all_production_line(status=status)