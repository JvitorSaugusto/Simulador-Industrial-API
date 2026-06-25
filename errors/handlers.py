from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from errors.errors_domain.production_order_errors import ProductionOrderInvalidStatusException
from errors.exceptions import NotFoundException


def register_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(status_code=404, content={"detail": f"{exc.resource_name} não encontrado(a)."})
    
    @app.exception_handler(ProductionOrderInvalidStatusException)
    async def op_invalid_status(request: Request, exc: ProductionOrderInvalidStatusException):
        return JSONResponse(status_code=400, content={"detail": f"O status finalizado não pode ser atribuido a uma Ordem de Produção pendente - OP: {exc.op_code}"})