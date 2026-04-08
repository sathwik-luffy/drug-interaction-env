from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import DrugInteractionAction, DrugInteractionObservation
from server.drug_interaction_env_environment import DrugInteractionEnvironment

app = FastAPI()
env = DrugInteractionEnvironment()

@app.get("/web", response_class=HTMLResponse)
def web():
    html = open("/app/env/static/index.html", encoding="utf-8").read()
    return html

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
    t = env.tasks[env.task_name]
    obs = DrugInteractionObservation(patient_info=t["patient_info"], medications=t["medications"], task_description=t["task_description"], feedback="Current state.", score_breakdown={}, task_name=env.task_name)
    return {"observation": obs.dict()}
