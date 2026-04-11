from pydantic import Field
from typing import List, Dict, Optional
from openenv.core.env_server.types import Action, Observation, State

class DrugInteractionAction(Action):
    prescription_analysis: str = Field(..., description="Full text analysis of the prescription")
    identified_issues: Optional[List[str]] = Field(default=[], description="List of issues found")
    safety_verdict: Optional[str] = Field(default="UNKNOWN", description="SAFE or UNSAFE")
    confidence_score: Optional[float] = Field(default=0.5, description="Confidence 0.0 to 1.0")

class DrugInteractionObservation(Observation):
    patient_info: str = Field(..., description="Patient demographics and conditions")
    medications: List[str] = Field(..., description="List of prescribed medications")
    task_description: str = Field(..., description="What the agent needs to do")
    feedback: str = Field(..., description="Feedback from previous step")
    score_breakdown: Dict = Field(default={}, description="Detailed scoring breakdown")
    task_name: str = Field(..., description="easy / medium / hard")
    step_count: int = Field(default=0, description="Current step number")
    max_steps: int = Field(default=3, description="Maximum steps per episode")
    episode_score: float = Field(default=0.0, description="Running episode score")

class DrugInteractionState(State):
    task_name: str = Field(default="easy", description="Current task difficulty")
    step_count: int = Field(default=0, description="Current step number")
    max_steps: int = Field(default=3, description="Maximum steps per episode")
    episode_score: float = Field(default=0.0, description="Running episode score")
    patient_name: str = Field(default="none", description="Current patient name")
    is_active: bool = Field(default=False, description="Whether episode is active")
