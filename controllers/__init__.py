from controllers.down_time_controller import router as down_time_router
from controllers.machine_controller import router as machine_router
from controllers.production_line_controller import router as production_line_router
from controllers.production_order_controller import router as production_order_router

__all__ = [
    "down_time_router",
    "machine_router",
    "production_line_router",
    "production_order_router",
]