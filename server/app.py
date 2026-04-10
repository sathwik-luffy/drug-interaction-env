from fastapi import FastAPI
from fastapi.responses import HTMLResponse

try:
    from ..models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

try:
    from .drug_interaction_env_environment import DrugInteractionEnvironment
except ImportError:
    from server.drug_interaction_env_environment import DrugInteractionEnvironment

app = FastAPI(title="Drug Interaction RL Environment", version="0.2.0")
env = DrugInteractionEnvironment()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "drug-interaction-env", "version": "0.2.0"}

@app.get("/web", response_class=HTMLResponse)
def web():
    return open("static/index.html", encoding="utf-8").read()

@app.post("/reset")
def reset(task_name: str = "easy"):
    obs = env.reset(task_name)
    return {"observation": obs.dict(), "reward": 0.0, "done": False}

@app.post("/step")
def step(action: DrugInteractionAction):
    obs, reward, done = env.step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done}

@app.get("/state")
def state():
    if not env.patient:
        return {"error": "No active episode. Call /reset first."}
    return {"state": env.state.dict()}
