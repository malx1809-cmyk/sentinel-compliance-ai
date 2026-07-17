import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from services.orchestrator import run_simulation, run_simulation_stream

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

@app.get("/simulate/stream")
def simulate_stream(rounds: int = 5):
    def event_generator():
        for round_data in run_simulation_stream(num_rounds=rounds):
            yield f"data: {json.dumps(round_data)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")