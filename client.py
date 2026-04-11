from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState


class DrugInteractionEnv(EnvClient[DrugInteractionAction, DrugInteractionObservation, DrugInteractionState]):

    def _step_payload(self, action: DrugInteractionAction) -> dict:
        return {
            "prescription_analysis": action.prescription_analysis,
            "identified_issues": action.identified_issues,
            "safety_verdict": action.safety_verdict,
            "confidence_score": action.confidence_score,
        }

    def _parse_result(self, payload: dict) -> StepResult[DrugInteractionObservation]:
        obs_data = payload.get("observation", {})
        obs = DrugInteractionObservation(
            patient_info=obs_data.get("patient_info", ""),
            medications=obs_data.get("medications", []),
            task_description=obs_data.get("task_description", ""),
            feedback=obs_data.get("feedback", ""),
            score_breakdown=obs_data.get("score_breakdown", {}),
            task_name=obs_data.get("task_name", "easy"),
            step_count=obs_data.get("step_count", 0),
            max_steps=obs_data.get("max_steps", 3),
            episode_score=obs_data.get("episode_score", 0.0),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
        )
        return StepResult(
            observation=obs,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> DrugInteractionState:
        return DrugInteractionState(
            task_name=payload.get("task_name", "easy"),
            step_count=payload.get("step_count", 0),
            max_steps=payload.get("max_steps", 3),
            episode_score=payload.get("episode_score", 0.0),
            patient_name=payload.get("patient_name", "none"),
            is_active=payload.get("is_active", False),
            episode_id=payload.get("episode_id", ""),
        )
