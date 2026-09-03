from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from enums.factory_enums import LineStatusEnum, ProductionOrderEnum
from errors.exceptions import NotFoundException
from models.machine_model import MachineModel
from models.production_line_model import ProductionLineModel
from models.production_order_model import ProductionOrderModel


class DashboardService:
    def __init__ (self, db: AsyncSession):
        self.db = db
        
    async def get_line_snapshot(self, line_id) -> dict:
        query_line = select(ProductionLineModel).where(ProductionLineModel.id == line_id, ProductionLineModel.simulation_status == LineStatusEnum.RUNNING)
        result = await self.db.execute(query_line)
        line = result.scalars().first()
        
        if not line:
            raise NotFoundException("Linha de produção")
        
        query_op = select(ProductionOrderModel).where(
            ProductionOrderModel.production_line_id == line_id, 
            ProductionOrderModel.status.in_([
                ProductionOrderEnum.PRODUCTION, 
                ProductionOrderEnum.STOP
                ])
            )
        result_ops = await self.db.execute(query_op)
        op = result_ops.scalars().first()
        
        query_machines = select(MachineModel).where(MachineModel.production_line_id == line_id)
        result_machines = await self.db.execute(query_machines)
        machines = result_machines.scalars().all()
        
        snapshot = {
            "id": line.id,
            "name": line.name,
            "target_oee": line.target_oee,
            "ideal_production_rate": line.ideal_production_rate,
            "current_production_rate": line.current_production_rate,
            "total_runtime_minutes": line.total_runtime_minutes,
            "simulation_status": line.simulation_status,
            "machines": machines,
            "active_op": op,
        }
        
        return snapshot