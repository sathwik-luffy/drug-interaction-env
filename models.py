from pydantic import BaseModel
from typing import List, Dict, Optional

class DrugInteractionAction(BaseModel):
    prescription_analysis: str
    identified_issues: Optional[List[str]] = []
    safety_verdict: Optional[str] = "UNKNOWN"
    confidence_score: Optional[float] = 0.5

class DrugInteractionObservation(BaseModel):
    patient_info: str
    medications: List[str]
    task_description: str
    feedback: str
    score_breakdown: Dict
    task_name: str
    step_count: int
    max_steps: int
    episode_score: float

class DrugInteractionState(BaseModel):
    task_name: str
    step_count: int
    max_steps: int
    episode_score: float
    patient_name: str
    is_active: bool
