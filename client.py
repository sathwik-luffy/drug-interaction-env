import requests
from typing import Optional
from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

class DrugInteractionEnv:
    """
    Client for the Drug Interaction RL Environment.
    
    Usage:
        env = DrugInteractionEnv(base_url="https://dasarisathwik27-drug-interaction-env.hf.space")
        obs = env.reset(task_name="easy")
        obs, reward, done = env.step(DrugInteractionAction(
            prescription_analysis="This prescription is SAFE...",
            safety_verdict="SAFE"
        ))
    """

    def __init__(self, base_url: str = "https://dasarisathwik27-drug-interaction-env.hf.space"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health(self) -> dict:
        r = self.session.get(f"{self.base_url}/health")
        r.raise_for_status()
        return r.json()

    def reset(self, task_name: str = "easy") -> DrugInteractionObservation:
        r = self.session.post(f"{self.base_url}/reset", params={"task_name": task_name})
        r.raise_for_status()
        data = r.json()
        return DrugInteractionObservation(**data["observation"])

    def step(self, action: DrugInteractionAction):
        r = self.session.post(
            f"{self.base_url}/step",
            json=action.dict(),
            headers={"Content-Type": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        obs = DrugInteractionObservation(**data["observation"])
        reward = data["reward"]
        done = data["done"]
        return obs, reward, done

    def state(self) -> DrugInteractionState:
        r = self.session.get(f"{self.base_url}/state")
        r.raise_for_status()
        data = r.json()
        return DrugInteractionState(**data["state"])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()
