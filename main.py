from logging_config import setup_logging
from fastapi import FastAPI
from controllers import dashboard_controller, down_time_controller, machine_controller, production_line_controller, production_order_controller, simulator_controller
from errors.handlers import register_exception_handlers

setup_logging()

app = FastAPI(title="Simulador Industrial")

register_exception_handlers(app)

app.include_router(production_line_controller.router, prefix="/api/lines", tags=["Linhas de Producao"])
app.include_router(production_order_controller.router, prefix="/api/ops", tags=["Ordens de Producao"])
app.include_router(machine_controller.router, prefix="/api/machines", tags=["Maquinas"])
app.include_router(down_time_controller.router, prefix="/api/events", tags=["Eventos de queda de tempo"])
app.include_router(simulator_controller.router, prefix="/api/simulator", tags=["Simulador"])
app.include_router(dashboard_controller.router, prefix="/api/dashboard", tags=["Dashboard"])