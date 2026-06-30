from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from errors.errors_domain.production_order_errors import ProductionOrderInvalidStatusException
from errors.exceptions import NotFoundException


def register_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: str):
        return JSONResponse(status_code=404, content={"detail": f"{exc} não encontrado(a)."})
    
    @app.exception_handler(ProductionOrderInvalidStatusException)
    async def op_invalid_status(request: Request, exc: str):
        return JSONResponse(status_code=400, content={"detail": f"{exc}"})