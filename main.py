from fastapi import FastAPI
from errors.handlers import register_exception_handlers

app = FastAPI(title="Simulador Industrial")

register_exception_handlers(app)