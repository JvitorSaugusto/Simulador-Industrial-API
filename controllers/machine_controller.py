from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.machine_schema import MachineRequestSchema, MachineResponseSchema, MachineUpdateSchema
from services.down_time_service import DownTimeService
from services.machine_service import MachineService


router = APIRouter()

def get_machine_service(db: AsyncSession = Depends(get_db)) -> MachineService:
    downtime_service = DownTimeService (db)
    return MachineService(db, downtime_service)

@router.post("/", response_model=MachineResponseSchema, status_code=201)
async def create_machine(payload: MachineRequestSchema, service: MachineService = Depends(get_machine_service)):
    return await service.create_machine(payload=payload)

@router.get("/", response_model=Sequence[MachineResponseSchema], status_code=200)
async def list_machines(service: MachineService = Depends(get_machine_service)):
    return await service.list_machines()

@router.get("/{machine_id}", response_model=MachineResponseSchema, status_code=200)
async def get_detail_machine(machine_id: int, service: MachineService = Depends(get_machine_service)):
    return await service.get_details_machine(machine_id=machine_id)

@router.put("/{machine_id}", response_model=MachineResponseSchema, status_code=200)
async def update_machine(machine_id: int, payload: MachineUpdateSchema, service: MachineService = Depends(get_machine_service)):
    return await service.update_machine(machine_id=machine_id, payload=payload)

@router.delete("/{machine_id}", status_code=200)
async def delete_machine(machine_id: int, service: MachineService = Depends(get_machine_service)):
    
    return await service.delete_machine(machine_id=machine_id)
