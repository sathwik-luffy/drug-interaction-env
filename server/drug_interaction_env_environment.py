from models import DrugInteractionAction, DrugInteractionObservation

class DrugInteractionEnvironment:
    def __init__(self):
        self.task_name = "easy"
        self.step_count = 0
        self.tasks = {
            "easy": {"patient_info": "Patient: Male, 45 years old, 80kg, no known allergies. Diagnosed with hypertension.", "medications": ["Lisinopril 10mg once daily"], "task_description": "Review this prescription. Check if Lisinopril 10mg dosage is appropriate. Standard adult dose is 10-40mg daily. State SAFE or UNSAFE and explain why.", "safe": True},
            "medium": {"patient_info": "Patient: Female, 62 years old, 65kg, no known allergies. Diagnosed with atrial fibrillation and depression.", "medications": ["Warfarin 5mg once daily", "Aspirin 100mg once daily", "Sertraline 50mg once daily"], "task_description": "Review this prescription for dangerous drug interactions. Warfarin+Aspirin increases bleeding risk. Warfarin+Sertraline also increases bleeding risk. State SAFE or UNSAFE.", "safe": False},
            "hard": {"patient_info": "Patient: Female, 78 years old, 55kg, penicillin allergy. Diagnosed with type 2 diabetes, hypertension, kidney disease, heart failure.", "medications": ["Metformin 1000mg twice daily", "Lisinopril 20mg once daily", "Amoxicillin 500mg three times daily", "Ibuprofen 400mg three times daily", "Furosemide 40mg once daily", "Digoxin 0.25mg once daily"], "task_description": "Review this complex prescription. Patient has penicillin allergy but is prescribed Amoxicillin. Ibuprofen is contraindicated with kidney disease. Metformin is risky with kidney disease. Find all issues and state SAFE or UNSAFE.", "safe": False}
        }

    def reset(self, task_name="easy"):
        self.task_name = task_name
        self.step_count = 0
        t = self.tasks[task_name]
        return DrugInteractionObservation(patient_info=t["patient_info"], medications=t["medications"], task_description=t["task_description"], feedback="New episode started. Please review the prescription.", score_breakdown={}, task_name=task_name)

    def step(self, action):
        self.step_count += 1
        t = self.tasks[self.task_name]
        text = action.prescription_analysis.lower()
        scores = {}
        scores["correct_assessment"] = 0.4 if ("unsafe" in text and not t["safe"]) or ("safe" in text and t["safe"] and "unsafe" not in text) else 0.0
        scores["explanation"] = 0.3 if len(action.prescription_analysis) > 50 else 0.1
        scores["dosage_check"] = 0.3 if any(w in text for w in ["dose","dosage","mg","interaction","contraindicated","allergy","risk"]) else 0.0
        reward = min(sum(scores.values()), 1.0)
        fb = "Correct assessment!" if scores["correct_assessment"] == 0.4 else "Incorrect assessment."
        obs = DrugInteractionObservation(patient_info=t["patient_info"], medications=t["medications"], task_description=t["task_description"], feedback=fb, score_breakdown=scores, task_name=self.task_name)
        return obs, reward, True
