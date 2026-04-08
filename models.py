from pydantic import BaseModel
from typing import List, Dict

class DrugInteractionAction(BaseModel):
    prescription_analysis: str

class DrugInteractionObservation(BaseModel):
    patient_info: str
    medications: List[str]
    task_description: str
    feedback: str
    score_breakdown: Dict
    task_name: str
