from openenv import SyncEnvClient, GenericAction
from models import DrugInteractionAction, DrugInteractionObservation

class DrugInteractionEnv(SyncEnvClient):
    """
    Client for the Drug Interaction RL Environment.
    
    Usage:
        env = DrugInteractionEnv(base_url="https://dasarisathwik27-drug-interaction-env.hf.space")
        obs = env.reset(task_name="easy")
        result = env.step(DrugInteractionAction(
            prescription_analysis="This prescription is UNSAFE...",
            safety_verdict="UNSAFE",
            identified_issues=["Warfarin+Aspirin bleeding risk"],
            confidence_score=0.95
        ))
        print(result.reward)
    """
    base_url: str = "https://dasarisathwik27-drug-interaction-env.hf.space"
    action_type = DrugInteractionAction
    observation_type = DrugInteractionObservation