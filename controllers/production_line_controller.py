from typing import Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from enums.factory_enums import LineStatusEnum
from errors.exceptions import NotFoundException
from services.production_line_service import ProductionLineService
from schemas.production_line_schema import ProductionLineRequestSchema, ProductionLineResponseSchema, ProductionLineUpdateSchema



router = APIRouter()

def get_production_line_service(db: AsyncSession = Depends(get_db)) -> ProductionLineService:
    return ProductionLineService(db)


@router.post("/", response_model=ProductionLineResponseSchema, status_code=201)
async def create_line(payload: ProductionLineRequestSchema, service: ProductionLineService = Depends(get_production_line_service)):
    return await service.create_production_line(payload)


@router.get("/", response_model=Sequence[ProductionLineResponseSchema])
async def get_all_lines(status: LineStatusEnum | None = Query(None, description="Filtrar linhas por status"), service: ProductionLineService = Depends(get_production_line_service)):
    return await service.list_all_production_line(status=status)


@router.get("/{line_id}", response_model=ProductionLineResponseSchema, status_code=200)
async def get_line(line_id: int, service: ProductionLineService = Depends(get_production_line_service)):
    return await service.get_details_line(line_id=line_id)



@router.put("/{line_id}", response_model=ProductionLineResponseSchema)
async def update_line(payload: ProductionLineUpdateSchema, line_id: int, service: ProductionLineService = Depends(get_production_line_service)):
    return await service.update_line(payload=payload, line_id=line_id)



@router.delete("/{line_id}")
async def delete_line(line_id: int, service: ProductionLineService = Depends(get_production_line_service)):
    return await service.delete_line(line_id=line_id)
