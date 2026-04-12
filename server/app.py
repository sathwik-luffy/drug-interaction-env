from fastapi import FastAPI
from fastapi.responses import HTMLResponse

try:
    from ..models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

try:
    from .drug_interaction_env_environment import DrugInteractionEnvironment
    from .database import get_leaderboard, get_episode_history, init_db
except ImportError:
    from server.drug_interaction_env_environment import DrugInteractionEnvironment
    from server.database import get_leaderboard, get_episode_history, init_db

init_db()
app = FastAPI(title="Drug Interaction RL Environment", version="0.3.0")
env = DrugInteractionEnvironment()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "drug-interaction-env", "version": "0.3.0"}

@app.get("/web", response_class=HTMLResponse)
def web():
    return open("static/index.html", encoding="utf-8").read()

@app.post("/reset")
def reset(task_name: str = "easy", model_name: str = "unknown"):
    obs = env.reset(task_name=task_name, model_name=model_name)
    return {"observation": obs.model_dump(), "reward": 0.0, "done": False}

@app.post("/step")
def step(action: DrugInteractionAction):
    obs = env.step(action)
    return {"observation": obs.model_dump(), "reward": obs.reward, "done": obs.done}

@app.get("/state")
def state():
    if not env.patient:
        return {"error": "No active episode. Call /reset first."}
    return {"state": env.state.model_dump()}

@app.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_leaderboard(limit=10)}

@app.get("/history")
def history():
    return {"episodes": get_episode_history(limit=20)}

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()