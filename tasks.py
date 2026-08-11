import models
from datetime import timedelta
import asyncio
from database import async_session_env
from celery import Celery

from services.down_time_service import DownTimeService
from services.production_line_service import ProductionLineService
from services.production_order_service import ProductionOrderService
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator
from services.simulation.machine_simulator_service import MachineSimulator
from services.simulation.production_line_simulator_service import LineSimulator
from services.simulation.production_order_simulator_service import ProductionOrderSimulator
from services.simulation.simulation_service import SimulationOrchestrator
from services.machine_service import MachineService


app = Celery('simulador_industrial', broker='redis://localhost:6379/0')

@app.task(bind=True, name="simulate_factory_tick", max_retries=5, default_retry_delay=10)
def simulate_factory_tick(self):
    try:
        asyncio.run(run_factory_simulation_logic())
    except Exception as e:
        raise self.retry(exc=e)
    
    
    
async def run_factory_simulation_logic():
    async with async_session_env() as session:
        #Services
        op_service = ProductionOrderService(db=session)
        down_time_event_service = DownTimeService(db=session)
        line_service = ProductionLineService(db=session)
        machine_service = MachineService(db=session, downtime_service=down_time_event_service)
        
        #Simulators
        down_time_event_simulator = DownTimeEventSimulator(db=session)
        machine_simulator = MachineSimulator(db=session, down_event_simulator=down_time_event_simulator, machine_service=machine_service)
        op_simulator = ProductionOrderSimulator(db=session, machine_service=machine_service , op_service=op_service, machine_simulator=machine_simulator)     
        line_simulator = LineSimulator(db=session, line_service=line_service, machine_service=machine_service)
        
        
        orchestrator = SimulationOrchestrator(
            db=session, 
            op_service=op_service, 
            op_simulator=op_simulator, 
            machine_simulator=machine_simulator, 
            line_service=line_service, 
            line_simulator=line_simulator,  
            down_time_simulator=down_time_event_simulator
            )
        
        await orchestrator.process_factory_tick()


# CONFIG DO BEAT - depois adicionar o red beat
app.conf.beat_schedule = {
    # Primeira Task: Responsável por rodar o ciclo da fábrica
    'executar-ciclo-da-fabrica-a-cada-10s': {
        'task': 'simulate_factory_tick',
        'schedule': timedelta(seconds=10),
    },
    
    # Segunda Task:  tirar a foto do OEE a cada 1 minuto
    # 'calcular-oee-acumulado-a-cada-minuto': {
    #     'task': 'calculate_factory_oee_tick',
    #     'schedule': timedelta(minutes=1),
    # },
}