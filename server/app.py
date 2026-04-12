import uvicorn
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
app = FastAPI(title="Drug Interaction RL Environment", version="0.4.0")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "drug-interaction-env", "version": "0.4.0"}

@app.get("/web", response_class=HTMLResponse)
def web():
    return open("static/index.html", encoding="utf-8").read()

@app.post("/reset")
def reset(task_name: str = "easy", model_name: str = "unknown", seed: int = None):
    env = DrugInteractionEnvironment()
    obs = env.reset(task_name=task_name, model_name=model_name, seed=seed)
    app.state.env = env
    return {"observation": obs.model_dump(), "reward": 0.0, "done": False}

@app.post("/step")
def step(action: DrugInteractionAction):
    env = getattr(app.state, "env", None)
    if env is None or env.patient is None:
        env = DrugInteractionEnvironment()
        env.reset()
        app.state.env = env
    obs = env.step(action)
    return {"observation": obs.model_dump(), "reward": obs.reward, "done": obs.done}

@app.get("/state")
def state():
    env = getattr(app.state, "env", None)
    if env is None or env.patient is None:
        return {"error": "No active episode. Call /reset first."}
    return {"state": env.state.model_dump()}

@app.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_leaderboard(limit=10)}

@app.get("/history")
def history():
    return {"episodes": get_episode_history(limit=20)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    env = DrugInteractionEnvironment()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action_type = msg.get("type", "step")

            if action_type == "reset":
                task_name = msg.get("task_name", "easy")
                model_name = msg.get("model_name", "unknown")
                seed = msg.get("seed", None)
                obs = env.reset(task_name=task_name, model_name=model_name, seed=seed)
                await websocket.send_text(json.dumps({
                    "type": "reset",
                    "observation": obs.model_dump(),
                    "reward": 0.0,
                    "done": False
                }))
            elif action_type == "step":
                action = DrugInteractionAction(
                    prescription_analysis=msg.get("prescription_analysis", ""),
                    safety_verdict=msg.get("safety_verdict", "UNKNOWN"),
                    identified_issues=msg.get("identified_issues", []),
                    confidence_score=msg.get("confidence_score", 0.5)
                )
                obs = env.step(action)
                await websocket.send_text(json.dumps({
                    "type": "step",
                    "observation": obs.model_dump(),
                    "reward": obs.reward,
                    "done": obs.done
                }))
            elif action_type == "state":
                await websocket.send_text(json.dumps({
                    "type": "state",
                    "state": env.state.model_dump()
                }))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
