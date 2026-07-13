from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.orchestrator import run_simulation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Sentinel backend is running"}

@app.get("/simulate")
def simulate(rounds: int = 5):
    result = run_simulation(num_rounds=rounds)
    return {"rounds": result}