from fastapi import FastAPI
from controllers import down_time_controller, machine_controller, production_line_controller, production_order_controller
from errors.handlers import register_exception_handlers

app = FastAPI(title="Simulador Industrial")

register_exception_handlers(app)

app.include_router(production_line_controller.router, prefix="/api/lines", tags=["Linhas de Producao"])
app.include_router(production_order_controller.router, prefix="/api/ops", tags=["Ordens de Producao"])
app.include_router(machine_controller.router, prefix="/api/machines", tags=["Maquinas"])
app.include_router(down_time_controller.router, prefix="/api/events", tags=["Eventos de queda de tempo"])