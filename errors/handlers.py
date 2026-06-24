from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from errors.exceptions import NotFoundException


def register_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(status_code=404, content={"detail": f"{exc.resource_name} não encontrado(a)."})