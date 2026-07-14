

from enums.factory_enums import DownTimeEventTypeEnum, DownTimeSeverityEnum, MachineStatusEnum
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from errors.exceptions import NotFoundException
from models.machine_model import MachineModel
from typed_dicts.machine_start_result import MachineStartResult

import random

from services.down_time_service import DownTimeService

class MachineSimulator:
    def __init__(self, db: AsyncSession, eventService: DownTimeService):
        self.db = db
        self.eventService = eventService
        
    def _add_wear_per_cycle(self, machine: MachineModel):
        increment_wear = random.uniform(0.5, 1.5)
        machine.wear_level += increment_wear
        
    def _calculate_failure_rate(self, machine: MachineModel) -> float:
        failure_rate = machine.base_failure_rate + machine.wear_level * 0.001
        
        return failure_rate
        
    def _calculate_future_date_random(self) -> datetime:
        seconds_to_wait = random.randint(10, 30)
        now = datetime.now(timezone.utc)
        future_date = now + timedelta(seconds=seconds_to_wait)
        
        return future_date
    
    def _future_date_by_severity(self, severity, future_date) -> datetime:
        if severity == DownTimeSeverityEnum.MEDIUM:
            seconds_to_wait = random.randint(30, 35)
            future_date += timedelta(seconds=seconds_to_wait)
        elif severity == DownTimeSeverityEnum.HIGH:
            seconds_to_wait = random.randint(35, 40)
            future_date += timedelta(seconds=seconds_to_wait)
        
        return future_date
    
    async def _start_machines(self, line_id) -> MachineStartResult:
        query = select(MachineModel).where(MachineModel.production_line_id == line_id, MachineModel.status == MachineStatusEnum.IDLE)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        if not machines:
            raise NotFoundException("Linhas de produção")
        
        success_start_machine = 0
        failed_start_machine = 0
        
        for machine in machines:
            if machine.wear_level >= 95:
                machine.status = MachineStatusEnum.STOP
                failed_start_machine += 1
            else:
                machine.status = MachineStatusEnum.PRODUCTION
                success_start_machine += 1
    
        return {
            'success_count': success_start_machine,
            'failed_count': failed_start_machine,
            'all_started': failed_start_machine == 0,
            'message': f'{success_start_machine} máquinas ligadas com sucesso!'
        }
        

    async def process_machine_states(self, line_id, op_id):
        query = select(MachineModel).where(MachineModel.production_line_id == line_id)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        for machine in machines:
            if machine.status == MachineStatusEnum.PRODUCTION:
                failure_rate = self._calculate_failure_rate(machine)
                self._add_wear_per_cycle(machine)
                 
                if random.random() < failure_rate:
                    machine.maintenance_start_at = self._calculate_future_date_random()
                    machine.breakdown_count += 1 # futuramente teremos lógicas temporais de manutenção preventiva
                    
                    self.eventService.generate_event(machine.id, op_id, DownTimeEventTypeEnum.FAILURE)
                    
                    machine.status = MachineStatusEnum.STOP
            
            elif machine.status == MachineStatusEnum.STOP:
                if machine.maintenance_start_at and machine.maintenance_start_at <= datetime.now(timezone.utc):
                    machine.maintenance_end_at =  self._calculate_future_date_random()
                    
                    machine.status = MachineStatusEnum.MAINTENANCE
                    
                    severity = random.choice(list(DownTimeSeverityEnum))
                    await self.eventService.update_active_event_severity(machine.id, severity)
                    machine.maintenance_end_at = self._future_date_by_severity(severity, machine.maintenance_end_at)
                    
            elif machine.status == MachineStatusEnum.MAINTENANCE:
                if machine.maintenance_end_at and machine.maintenance_end_at <= datetime.now(timezone.utc):
                    # Depois gerar um relatorio aqui sobre o fim da manutencao
                    machine.wear_level = 0.0
                    machine.status = MachineStatusEnum.PRODUCTION
                    
                    machine.maintenance_start_at = None
                    machine.maintenance_end_at = None
                    await self.eventService.close_active_event(machine.id)
                    
        