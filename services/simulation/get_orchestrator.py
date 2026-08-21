from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.down_time_service import DownTimeService
from services.production_line_service import ProductionLineService
from services.production_order_service import ProductionOrderService
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator
from services.simulation.machine_simulator_service import MachineSimulator
from services.simulation.production_line_simulator_service import LineSimulator
from services.simulation.production_order_simulator_service import ProductionOrderSimulator
from services.simulation.simulation_service import SimulationOrchestrator
from services.machine_service import MachineService


def get_simulation_service(db: AsyncSession = Depends(get_db)) -> SimulationOrchestrator:
    op_service = ProductionOrderService(db=db)
    down_time_event_service = DownTimeService(db=db)
    line_service = ProductionLineService(db=db)
    machine_service = MachineService(db=db, downtime_service=down_time_event_service)
    

    down_time_event_simulator = DownTimeEventSimulator(db=db)
    machine_simulator = MachineSimulator(db=db, down_event_simulator=down_time_event_simulator, machine_service=machine_service)
    op_simulator = ProductionOrderSimulator(db=db, machine_service=machine_service , op_service=op_service, machine_simulator=machine_simulator)    
    line_simulator = LineSimulator(db=db, line_service=line_service, machine_service=machine_service)
    
    orchestrator = SimulationOrchestrator(
        db=db, 
        op_service=op_service, 
        op_simulator=op_simulator, 
        machine_simulator=machine_simulator, 
        line_service=line_service, 
        line_simulator=line_simulator,  
        down_time_simulator=down_time_event_simulator,
        down_time_service=down_time_event_service
    )
            
    return orchestrator
