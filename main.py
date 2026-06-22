from fastapi import FastAPI

app = FastAPI()

@app.get(("/"))
def root():
    return {"status": "Simulador Industrial API rodando"}