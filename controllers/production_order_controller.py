from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.production_order_schema import ProductionOrderRequestSchema, ProductionOrderResponseSchema, ProductionOrderUpdateSchema
from services.production_order_service import ProductionOrderService


router = APIRouter()

def get_production_order_service(db: AsyncSession = Depends(get_db)) -> ProductionOrderService:
    return ProductionOrderService(db)


@router.post("/", response_model=ProductionOrderResponseSchema, status_code=201)
async def create_op(payload: ProductionOrderRequestSchema, service: ProductionOrderService = Depends(get_production_order_service)):
    return await service.create_op(payload=payload)

@router.get("/", response_model=Sequence[ProductionOrderResponseSchema],status_code=200)
async def list_ops(service: ProductionOrderService = Depends(get_production_order_service)):
    return await service.list_ops()

@router.get("/{op_id}", response_model=ProductionOrderResponseSchema, status_code=200)
async def get_detail_op(op_id: int, service: ProductionOrderService = Depends(get_production_order_service)):
    return await service.get_detail_op(op_id=op_id)

@router.put("/{op_id}", response_model=ProductionOrderResponseSchema, status_code=200)
async def update_op(payload: ProductionOrderUpdateSchema, op_id: int, service: ProductionOrderService = Depends(get_production_order_service)):
    return await service.update_op(payload=payload, op_id=op_id)

@router.delete("/{op_id}", status_code=200)
async def delete_op(op_id: int, service: ProductionOrderService = Depends(get_production_order_service)):
    return await service.delete_op(op_id=op_id)