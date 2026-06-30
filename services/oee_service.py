from datetime import datetime, timezone

from sqlalchemy import func, select

from sqlalchemy.ext.asyncio import AsyncSession

from enums.factory_enums import ProductionOrderEnum
from models.down_time_model import DownTimeEventModel
from models.production_order_model import ProductionOrderModel
from errors.exceptions import NotFoundException
from errors.errors_domain.production_order_errors import ProductionOrderInvalidStatusException


class OeeRecordService:
    def __init__(self, db: AsyncSession):
        self.db = db    
        
    async def get_active_op_by_line(self, line_id: int):
        op = await self.db.execute(
            select(ProductionOrderModel).where(
                ProductionOrderModel.production_line_id == line_id,
                ProductionOrderModel.status == ProductionOrderEnum.PRODUCTION))
        
        active_op = op.scalars().first()
        return active_op
        
    def _calculate_availability(self, runtime: float, total_runtime: float):
        if total_runtime <= 0:
            return 1.0
        return runtime / total_runtime
    
    def _calculate_perfomance(self, ideal_cycle: float, real_cycle: float):
        if ideal_cycle == 0:
            return 0.0
        return real_cycle / ideal_cycle
    
    def _calculate_quality(self, current_correct_count: int, current_total_count: int):
        if current_total_count == 0:
            return 1.0
        return current_correct_count / current_total_count
    
    def get_oee(self, availability: float, perfomance: float, quality: float) -> float:
        return (availability * perfomance * quality) * 100
    
    async def calculate_current_oee(self, line_id: int) -> float:
        active_op = await self.get_active_op_by_line(line_id)
        
        if not active_op:
            raise NotFoundException("Nenhuma Ordem de Produção ativa.")
        
        if not active_op.actual_start:
            raise ProductionOrderInvalidStatusException("A Ordem de Produção ativa ainda não foi iniciada.")
        
        time_delta = datetime.now(timezone.utc) - active_op.actual_start
        total_runtime = time_delta.total_seconds() / 60
        
        down_time_calculate = await self.db.execute(
            select(func.sum(DownTimeEventModel.duration)).where(
                DownTimeEventModel.production_order_id == active_op.id))
        
        current_stop_time = down_time_calculate.scalar() or 0.0
        runtime = total_runtime - current_stop_time
        
        # --- Disponibilidade ---
        _cal_availability = self._calculate_availability(runtime, total_runtime)
        
        # --- Performance ---
        planned_production_quant = active_op.quantity_planned
        time_planned_delta = active_op.planned_end - active_op.planned_start
        planned_production_time_minutes = time_planned_delta.total_seconds() / 60
        
        if planned_production_time_minutes <= 0 or runtime <= 0:
            _cal_perfomance = 1.0
        else:
            ideal_cycle = (planned_production_quant / planned_production_time_minutes)
            real_cycle = (active_op.quantity_produced / runtime)
            _cal_perfomance = self._calculate_perfomance(ideal_cycle, real_cycle)
        
        # --- Qualidade ---
        current_correct_count = active_op.quantity_good
        current_total_count = active_op.quantity_produced
        
        _cal_quality = self._calculate_quality(current_correct_count, current_total_count)
        
        # --- OEE FINAL ---
        oee = self.get_oee(_cal_availability, _cal_perfomance, _cal_quality)
        
        return oee
  