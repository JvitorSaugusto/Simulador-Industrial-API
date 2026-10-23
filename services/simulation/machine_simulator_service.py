from enums.factory_enums import DownTimeEventTypeEnum, DownTimeSeverityEnum, MachineStatusEnum
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from errors.exceptions import NotFoundException
from models.machine_model import MachineModel
from services.machine_service import MachineService
from typed_dicts.machine_start_result import MachineStartResult

import random
import logging
from schemas.machine_schema import MachineRequestSchema
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator


MOCK_MACHINE_NAMES = [
        "Injetora de Plástico Hidráulica IP-01",
        "Torno CNC de Alta Precisão TC-03",
        "Prensa Estampadora Pneumática PE-02",
        "Robô de Solda Braço Articulado RS-05",
        "Esteira Transportadora Integrada ET-10",
        "Fresadora Universal Digital FU-01",
        "Furadeira de Bancada Industrial FB-04",
        "Célula de Paletização Automatizada CP-08",
        "Bobinadora de Fios de Cobre BC-02",
        "Forno de Tratamento Térmico FT-01"
    ]

logger = logging.getLogger(__name__)

class MachineSimulator:
    def __init__(self, db: AsyncSession, down_event_simulator: DownTimeEventSimulator, machine_service: MachineService):
        self.db = db
        self.down_event_simulator = down_event_simulator
        self.machine_service = machine_service
    
    def _add_wear_per_cycle(self, machine: MachineModel):
        increment_wear = random.uniform(0.5, 1.5)
        machine.wear_level += increment_wear
        
    def _calculate_failure_rate(self, machine: MachineModel) -> float:
        brute_rate = machine.base_failure_rate + (machine.wear_level * 0.001)
        
        percent = brute_rate / 100.0
        
        failure_rate_per_tick = percent / 100.0
        
        return failure_rate_per_tick
        
    def _calculate_future_date_random(self, time_unit) -> datetime:
        seconds_to_wait = random.randint(10, 30)
        now = datetime.now(timezone.utc)
        
        if time_unit == 'seconds':
            future_date = now + timedelta(seconds=seconds_to_wait)
        elif time_unit == 'minutes':
            future_date = now + timedelta(minutes=seconds_to_wait)
        return future_date
    
    def _future_date_by_severity(self, severity, future_date) -> datetime:
        if severity == DownTimeSeverityEnum.MEDIUM:
            seconds_to_wait = random.randint(30, 35)
            future_date += timedelta(seconds=seconds_to_wait)
        elif severity == DownTimeSeverityEnum.HIGH:
            seconds_to_wait = random.randint(35, 40)
            future_date += timedelta(seconds=seconds_to_wait)
        
        return future_date
    
    async def start_all_machines(self, line_id) -> MachineStartResult:
        query = select(MachineModel).where(MachineModel.production_line_id == line_id, MachineModel.status == MachineStatusEnum.IDLE)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        if not machines:
            logger.warning(f"Tentativa de iniciar máquinas: Nenhuma máquina em estado IDLE encontrada na linha {line_id}.")
            
            return {
            'success_count': 0,
            'failed_count': 0,
            'all_started': False,
            'message': 'Nenhuma máquina em estado IDLE encontrada na linha!'
        }
        
        success_start_machine = 0
        failed_start_machine = 0
        
        for machine in machines:
            if machine.wear_level >= 95:
                machine.status = MachineStatusEnum.STOP
                failed_start_machine += 1
                machine.maintenance_start_at =  self._calculate_future_date_random('seconds')
                await self.down_event_simulator.generate_event(line_id=line_id, op_id=op_id, type=DownTimeEventTypeEnum.FAILURE)
                                    
            else:
                machine.status = MachineStatusEnum.PRODUCTION
                success_start_machine += 1
    
        return {
            'success_count': success_start_machine,
            'failed_count': failed_start_machine,
            'all_started': failed_start_machine == 0,
            'message': f'{success_start_machine} máquinas ligadas com sucesso!'
        }
        
    async def idle_all_machines(self, line_id):
        query = select(MachineModel).where(MachineModel.production_line_id == line_id, MachineModel.status != MachineStatusEnum.MAINTENANCE)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        for machine in machines:
            machine.status = MachineStatusEnum.IDLE

    async def process_machine_states(self, line_id, op_id):
        query = select(MachineModel).where(MachineModel.production_line_id == line_id)
        result = await self.db.execute(query)
        machines = result.scalars().all()
        
        for machine in machines:
            if machine.status == MachineStatusEnum.PRODUCTION:
                failure_rate = self._calculate_failure_rate(machine)
                self._add_wear_per_cycle(machine)
                 
                if random.random() < failure_rate:
                    machine.maintenance_start_at = self._calculate_future_date_random('seconds')
                    machine.breakdown_count += 1 # futuramente teremos lógicas temporais de manutenção preventiva
                    
                    await self.down_event_simulator.generate_event(line_id=line_id, op_id=op_id, type=DownTimeEventTypeEnum.FAILURE)
                    
                    machine.status = MachineStatusEnum.STOP
            
            elif machine.status == MachineStatusEnum.STOP:
                if machine.maintenance_start_at and machine.maintenance_start_at <= datetime.now(timezone.utc):
                    machine.maintenance_end_at =  self._calculate_future_date_random('minutes')
                    
                    machine.status = MachineStatusEnum.MAINTENANCE
                    
                    severity = random.choice(list(DownTimeSeverityEnum))
                    
                    await self.down_event_simulator.update_active_event_severity(line_id, severity)
                    machine.maintenance_end_at = self._future_date_by_severity(severity, machine.maintenance_end_at)
                    
            elif machine.status == MachineStatusEnum.MAINTENANCE:
                if machine.maintenance_end_at and machine.maintenance_end_at <= datetime.now(timezone.utc):
                    # Depois gerar um relatorio aqui sobre o fim da manutencao
                    machine.wear_level = 0.0
                    machine.status = MachineStatusEnum.PRODUCTION
                    
                    machine.maintenance_start_at = None
                    machine.maintenance_end_at = None
                    await self.down_event_simulator.close_active_event(line_id)
                    
    
    async def generate_machine_mock(self, line_id, quantity_machines):
        query = select(MachineModel.name)
        result = await self.db.execute(query)
        existing_names = set(result.scalars().all())
        
        available_names = []
        
        for name in MOCK_MACHINE_NAMES:
            if name not in existing_names:
                available_names.append(name)
                
        if not available_names:
            raise ValueError("Todas as maquinas possiveis ja foram criadas")
                
        num_to_create = min(quantity_machines, len(MOCK_MACHINE_NAMES))
        selected_names = random.sample(MOCK_MACHINE_NAMES, num_to_create)
        
        created_machines = []
        
        for machine_name in selected_names:
            payload = MachineRequestSchema(
                name=machine_name,
                base_failure_rate=round(random.uniform(1.5, 4.5), 2)
            )   
            
            new_machine = await self.machine_service.create_machine(payload)
            new_machine.production_line_id = line_id
            
            created_machines.append(new_machine)
        await self.db.commit()
        return created_machines