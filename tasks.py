import asyncio
import logging
import sys
from pathlib import Path

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from database import async_session_env
from services.down_time_service import DownTimeService
from services.machine_service import MachineService
from services.production_line_service import ProductionLineService
from services.production_order_service import ProductionOrderService
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator
from services.simulation.machine_simulator_service import MachineSimulator
from services.simulation.production_line_simulator_service import LineSimulator
from services.simulation.production_order_simulator_service import (
    ProductionOrderSimulator,
)
from services.simulation.simulation_service import SimulationOrchestrator

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))



@after_setup_logger.connect
@after_setup_task_logger.connect
def config_loggers(*args, **kwargs):
    from logging_config import setup_logging
    setup_logging()

logger = logging.getLogger(__name__)

app = Celery('simulador_industrial', broker='redis://127.0.0.1:6379/0')

@app.task(bind=True, name="simulate_factory_tick", max_retries=5, default_retry_delay=10)
def simulate_factory_tick(self):
    logger.info("[CELERY] Task simulate_factory_tick foi disparada e iniciada.")
    try:
        asyncio.run(run_factory_simulation_logic())
        logger.info("[CELERY] Task simulate_factory_tick concluída com sucesso.")
    except Exception as e:
        logger.error(f"[CELERY] Erro na task simulate_factory_tick: {e}")
        raise self.retry(exc=e)
    
    
async def run_factory_simulation_logic():
    logger.info("[ASYNC] Entrando em run_factory_simulation_logic e abrindo sessão do banco...")
    async with async_session_env() as session:
        logger.info("[ASYNC] Sessão aberta com sucesso. Instanciando services e simulators...")
        
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
        
        logger.info("[ASYNC] Chamando orchestrator.process_factory_tick()...")
        await orchestrator.process_factory_tick()
        logger.info("[ASYNC] orchestrator.process_factory_tick() finalizado.")


# CONFIG DO BEAT - depois adicionar o red beat
app.conf.beat_schedule = {
    # Primeira Task: Responsável por rodar o ciclo da fábrica
    'executar-ciclo-da-fabrica-a-cada-20s': {
        'task': 'simulate_factory_tick',
        'schedule': 20.0,
    },
    
    # Segunda Task:  tirar a foto do OEE a cada 1 minuto
    # 'calcular-oee-acumulado-a-cada-minuto': {
    #     'task': 'calculate_factory_oee_tick',
    #     'schedule': timedelta(minutes=1),
    # },
}