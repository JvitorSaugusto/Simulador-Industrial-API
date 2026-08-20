from pydantic import BaseModel


class InitializeSimulationRequestSchema(BaseModel):
    quantity_lines: int
    machines_per_line: int
    auto_generate_op: bool
    
    
class SimulationLineInitRequestSchema(BaseModel):
    line_id: int
    auto_generate: bool