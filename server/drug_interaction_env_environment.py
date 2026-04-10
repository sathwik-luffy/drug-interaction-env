import random
import uuid

try:
    from ..models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

PATIENTS = [
    {"name": "John Smith", "age": 45, "weight": 80, "gender": "Male", "allergies": "none", "conditions": ["hypertension"], "medications": ["Lisinopril 10mg once daily"], "issues": [], "safe": True, "difficulty": "easy"},
    {"name": "Robert Lee", "age": 55, "weight": 90, "gender": "Male", "allergies": "none", "conditions": ["type 2 diabetes", "hypertension"], "medications": ["Metformin 500mg twice daily", "Amlodipine 5mg once daily"], "issues": [], "safe": True, "difficulty": "easy"},
    {"name": "Lisa Taylor", "age": 50, "weight": 72, "gender": "Female", "allergies": "none", "conditions": ["hypertension", "high cholesterol"], "medications": ["Amlodipine 10mg once daily", "Atorvastatin 20mg once daily"], "issues": [], "safe": True, "difficulty": "easy"},
    {"name": "James Brown", "age": 60, "weight": 85, "gender": "Male", "allergies": "aspirin", "conditions": ["chest pain"], "medications": ["Aspirin 100mg once daily", "Clopidogrel 75mg once daily"], "issues": ["Patient allergic to Aspirin"], "safe": False, "difficulty": "easy"},
    {"name": "Mary Johnson", "age": 62, "weight": 65, "gender": "Female", "allergies": "none", "conditions": ["atrial fibrillation", "depression"], "medications": ["Warfarin 5mg once daily", "Aspirin 100mg once daily", "Sertraline 50mg once daily"], "issues": ["Warfarin+Aspirin increases bleeding risk", "Warfarin+Sertraline increases bleeding risk"], "safe": False, "difficulty": "medium"},
    {"name": "Susan Chen", "age": 70, "weight": 58, "gender": "Female", "allergies": "penicillin", "conditions": ["pneumonia", "heart failure"], "medications": ["Amoxicillin 500mg three times daily", "Furosemide 40mg once daily"], "issues": ["Amoxicillin contains penicillin - patient is allergic"], "safe": False, "difficulty": "medium"},
    {"name": "Emma Davis", "age": 35, "weight": 70, "gender": "Female", "allergies": "none", "conditions": ["depression", "anxiety"], "medications": ["Sertraline 50mg once daily", "Alprazolam 0.5mg twice daily"], "issues": ["Sertraline+Alprazolam CNS depression risk"], "safe": False, "difficulty": "medium"},
    {"name": "Michael Wong", "age": 58, "weight": 75, "gender": "Male", "allergies": "none", "conditions": ["hypertension", "depression"], "medications": ["Metoprolol 50mg twice daily", "Fluoxetine 20mg once daily", "Tramadol 50mg as needed"], "issues": ["Tramadol+Fluoxetine serotonin syndrome risk", "Metoprolol+Fluoxetine interaction"], "safe": False, "difficulty": "medium"},
    {"name": "David Wilson", "age": 78, "weight": 55, "gender": "Male", "allergies": "sulfa drugs", "conditions": ["kidney disease", "heart failure", "diabetes"], "medications": ["Metformin 1000mg twice daily", "Ibuprofen 400mg three times daily", "Furosemide 40mg once daily", "Digoxin 0.25mg once daily", "Glibenclamide 5mg once daily"], "issues": ["Metformin risky with kidney disease", "Ibuprofen contraindicated with kidney disease", "Glibenclamide+Furosemide interaction"], "safe": False, "difficulty": "hard"},
    {"name": "Patricia Moore", "age": 82, "weight": 52, "gender": "Female", "allergies": "penicillin", "conditions": ["osteoporosis", "kidney disease", "hypertension", "depression"], "medications": ["Amoxicillin 500mg three times daily", "Ibuprofen 400mg twice daily", "Lisinopril 10mg once daily", "Sertraline 50mg once daily", "Alendronate 70mg weekly"], "issues": ["Amoxicillin - penicillin allergy", "Ibuprofen contraindicated with kidney disease", "Ibuprofen reduces Lisinopril effectiveness"], "safe": False, "difficulty": "hard"},
]

TASK_DESCRIPTIONS = {
    "easy": "Review this prescription carefully. Check for allergy violations and obvious dosage errors. State clearly SAFE or UNSAFE and provide your reasoning.",
    "medium": "Review this multi-drug prescription thoroughly. Identify all drug-drug interactions and allergy violations. For each issue found, explain the clinical risk. State SAFE or UNSAFE with full explanation.",
    "hard": "Review this complex prescription for an elderly patient with multiple conditions. Identify ALL interactions, contraindications, allergy violations, and dosage issues specific to the patient conditions. State SAFE or UNSAFE with comprehensive clinical reasoning."
}

class DrugInteractionEnvironment:
    def __init__(self):
        self.task_name = "easy"
        self.step_count = 0
        self.max_steps = 3
        self.episode_score = 0.0
        self.patient = None
        self.episode_id = None

    def _get_random_patient(self, difficulty):
        pool = [p for p in PATIENTS if p["difficulty"] == difficulty]
        return random.choice(pool)

    def _build_patient_info(self, p):
        return (f"Patient: {p['name']}, {p['gender']}, {p['age']} years old, "
                f"{p['weight']}kg. Allergies: {p['allergies']}. "
                f"Conditions: {', '.join(p['conditions'])}.")

    def reset(self, task_name="easy"):
        self.task_name = task_name
        self.step_count = 0
        self.episode_score = 0.0
        self.episode_id = str(uuid.uuid4())[:8]
        self.patient = self._get_random_patient(task_name)
        return DrugInteractionObservation(
            patient_info=self._build_patient_info(self.patient),
            medications=self.patient["medications"],
            task_description=TASK_DESCRIPTIONS[task_name],
            feedback="New episode started. Please review the prescription carefully.",
            score_breakdown={},
            task_name=task_name,
            step_count=0,
            max_steps=self.max_steps,
            episode_score=0.0
        )

    def step(self, action):
        self.step_count += 1
        p = self.patient
        text = action.prescription_analysis.lower()
        verdict = (action.safety_verdict or "").upper()
        scores = {}

        # 1. Correct safety verdict (0.4 points)
        is_safe_text = "safe" in text and "unsafe" not in text
        is_unsafe_text = "unsafe" in text
        if p["safe"]:
            scores["correct_verdict"] = 0.4 if (is_safe_text or verdict == "SAFE") else 0.0
        else:
            scores["correct_verdict"] = 0.4 if (is_unsafe_text or verdict == "UNSAFE") else 0.0

        # 2. Issue detection (0.3 points)
        if not p["issues"]:
            scores["issue_detection"] = 0.3 if scores["correct_verdict"] == 0.4 else 0.0
        else:
            detected = 0
            for issue in p["issues"]:
                keywords = issue.lower().split()[:4]
                if any(kw in text for kw in keywords if len(kw) > 3):
                    detected += 1
            scores["issue_detection"] = round(0.3 * (detected / len(p["issues"])), 2)

        # 3. Explanation quality (0.2 points)
        length = len(action.prescription_analysis)
        scores["explanation_quality"] = 0.2 if length > 150 else (0.1 if length > 60 else 0.0)

        # 4. Medical terminology (0.1 points)
        terms = ["contraindicated", "interaction", "allergy", "allergic", "dosage",
                 "adverse", "therapeutic", "bleeding", "renal", "hepatic",
                 "serotonin", "toxicity", "contraindication", "hypersensitivity"]
        term_count = sum(1 for t in terms if t in text)
        scores["medical_terminology"] = 0.1 if term_count >= 3 else (0.05 if term_count >= 1 else 0.0)

        reward = round(min(sum(scores.values()), 1.0), 3)
        self.episode_score = round((self.episode_score * (self.step_count - 1) + reward) / self.step_count, 3)

        done = self.step_count >= self.max_steps or (scores["correct_verdict"] == 0.4 and reward >= 0.8)

        if scores["correct_verdict"] == 0.4:
            fb = f"Correct! This prescription is {'SAFE' if p['safe'] else 'UNSAFE'}."
        else:
            fb = f"Incorrect. This prescription is {'SAFE' if p['safe'] else 'UNSAFE'}."
        if p["issues"]:
            fb += f" Key issues: {'; '.join(p['issues'][:2])}."

        return DrugInteractionObservation(
            patient_info=self._build_patient_info(p),
            medications=p["medications"],
            task_description=TASK_DESCRIPTIONS[self.task_name],
            feedback=fb,
            score_breakdown=scores,
            task_name=self.task_name,
            step_count=self.step_count,
            max_steps=self.max_steps,
            episode_score=self.episode_score
        ), reward, done

    @property
    def state(self):
        return DrugInteractionState(
            task_name=self.task_name,
            step_count=self.step_count,
            max_steps=self.max_steps,
            episode_score=self.episode_score,
            patient_name=self.patient["name"] if self.patient else "none",
            is_active=self.patient is not None
        )
