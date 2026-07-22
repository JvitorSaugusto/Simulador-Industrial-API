import random

from sqlalchemy.ext.asyncio import AsyncSession
from enums.factory_enums import DownTimeEventTypeEnum
from services.production_line_service import ProductionLineService
from services.production_order_service import ProductionOrderService
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator
from services.simulation.machine_simulator_service import MachineSimulator
from services.simulation.production_order_simulator_service import ProductionOrderSimulator
from services.simulation.production_line_simulator_service import LineSimulator

#maestro dos outros simulators services
class SimulationOrchestrator:
    def __init__(self, db: AsyncSession, op_service: ProductionOrderService, op_simulator: ProductionOrderSimulator, machine_simulator: MachineSimulator, line_simulator: LineSimulator, line_service: ProductionLineService, down_time_simulator: DownTimeEventSimulator):
        self.db = db
        self.op_service = op_service
        self.op_simulator = op_simulator
        self.machine_simulator = machine_simulator
        self.line_simulator = line_simulator
        self.line_service = line_service
        self.down_time_simulator = down_time_simulator

    async def initialize_simulation(self, quantity_lines: int, machines_per_line: int, auto_generate_op: bool):
        created_lines = await self.line_simulator.generate_line_mock(quantity_lines)
        
        for line in created_lines:
            await self.machine_simulator.generate_machine_mock(line.id, machines_per_line)
            
            if auto_generate_op:
                await self.op_simulator.generate_op_mock(line.id)
        
    async def start_simulation_line(self, line_id, auto_generate: bool):
               
        await self.line_simulator.start_line(line_id)
        
        await self.machine_simulator.start_all_machines(line_id)
        
        active_op = await self.op_service.get_active_op_by_line(line_id=line_id)
        
        if not active_op:
            if auto_generate:
                await self.op_simulator.generate_op_mock(line_id)

            
    async def process_factory_tick(self):
        """
        Executado pelo Celery a cada X segundos.

        Responsável por percorrer todas as linhas em execução e
        delegar o processamento aos simuladores especializados.
        """

        running_lines = await self.line_service.get_running_lines()

        if not running_lines:
            return

        for line in running_lines:
            active_op = await self.op_service.get_active_op_by_line(line.id)
            op_id = active_op.id if active_op else None

            await self.machine_simulator.process_machine_states(line_id=line.id, op_id=op_id,)
            
            cycle_pieces = await self.line_simulator.process_line_production(line)

            if active_op:              
                finished_op = await self.op_simulator.process_op_state(line_id=line.id, op_id=op_id, cycle_pieces=cycle_pieces)
                
                if finished_op:
                    if random.random() > 0.20: #chance das maquina não desligarem no fim de uma op
                        await self.machine_simulator.idle_all_machines(line.id)
                
            else:
                await self.down_time_simulator.generate_event(line_id=line.id, type=DownTimeEventTypeEnum.UNDEFINED_PRODUCTION)
                
                if random.random() > 0.20: #chance de adiar o inicio de uma op, simulando atrasos
                    await self.op_simulator.start_op(line.id)
                    await self.down_time_simulator.close_active_event(line.id)
                    
                await self.op_simulator.auto_generate_ops_backlog(line.id)
         
        await self.db.commit()
                