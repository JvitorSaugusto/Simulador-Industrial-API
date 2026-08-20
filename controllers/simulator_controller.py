from fastapi import APIRouter, Depends
from services.simulation import get_orchestrator
from services.simulation.simulation_service import SimulationOrchestrator
from schemas.simulator_schema import InitializeSimulationRequestSchema, SimulationLineInitRequestSchema


router = APIRouter()

@router.post("/initialize", status_code=201)
async def initialize_simulation(payload: InitializeSimulationRequestSchema, orchestrator: SimulationOrchestrator = Depends(get_orchestrator.get_simulation_service)):
    await orchestrator.initialize_simulation(quantity_lines=payload.quantity_lines, machines_per_line=payload.machines_per_line, auto_generate_op=payload.auto_generate_op)
    return {"message": "Simulação inicializada com sucesso"}


@router.post("/start_line", status_code=201)
async def start_simulation_line(payload: SimulationLineInitRequestSchema, orchestrator: SimulationOrchestrator = Depends(get_orchestrator.get_simulation_service)):
    await orchestrator.start_simulation_line(line_id=payload.line_id, auto_generate=payload.auto_generate)
    return {
        "message": f"Linha de produção {payload.line_id} iniciada com sucesso.",
        "line_id": payload.line_id,
        "status": "RUNNING",
        "auto_generate_op": payload.auto_generate
    }