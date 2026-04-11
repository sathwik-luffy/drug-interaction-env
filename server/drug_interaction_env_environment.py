import re
import random
import uuid
from openenv.core.env_server.interfaces import Environment

try:
    from ..models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

PATIENTS = [
    # EASY — 4 patients
    {
        "name": "John Smith", "age": 45, "weight": 80, "gender": "Male",
        "allergies": "none", "conditions": ["hypertension"],
        "medications": ["Lisinopril 10mg once daily"],
        "issues": [], "safe": True, "difficulty": "easy"
    },
    {
        "name": "Robert Lee", "age": 55, "weight": 90, "gender": "Male",
        "allergies": "none", "conditions": ["type 2 diabetes", "hypertension"],
        "medications": ["Metformin 500mg twice daily", "Amlodipine 5mg once daily"],
        "issues": [], "safe": True, "difficulty": "easy"
    },
    {
        "name": "Lisa Taylor", "age": 50, "weight": 72, "gender": "Female",
        "allergies": "none", "conditions": ["hypertension", "high cholesterol"],
        "medications": ["Amlodipine 10mg once daily", "Atorvastatin 20mg once daily"],
        "issues": [], "safe": True, "difficulty": "easy"
    },
    {
        "name": "James Brown", "age": 60, "weight": 85, "gender": "Male",
        "allergies": "aspirin", "conditions": ["chest pain"],
        "medications": ["Aspirin 100mg once daily", "Clopidogrel 75mg once daily"],
        "issues": ["Patient is allergic to Aspirin — direct allergy violation"],
        "safe": False, "difficulty": "easy"
    },

    # MEDIUM — 4 patients
    {
        "name": "Mary Johnson", "age": 62, "weight": 65, "gender": "Female",
        "allergies": "none", "conditions": ["atrial fibrillation", "depression"],
        "medications": ["Warfarin 5mg once daily", "Aspirin 100mg once daily", "Sertraline 50mg once daily"],
        "issues": ["Warfarin+Aspirin increases bleeding risk", "Warfarin+Sertraline increases bleeding risk"],
        "safe": False, "difficulty": "medium"
    },
    {
        "name": "Susan Chen", "age": 70, "weight": 58, "gender": "Female",
        "allergies": "penicillin", "conditions": ["pneumonia", "heart failure"],
        "medications": ["Amoxicillin 500mg three times daily", "Furosemide 40mg once daily"],
        "issues": ["Amoxicillin contains penicillin — patient is allergic"],
        "safe": False, "difficulty": "medium"
    },
    {
        "name": "Emma Davis", "age": 35, "weight": 70, "gender": "Female",
        "allergies": "none", "conditions": ["depression", "anxiety"],
        "medications": ["Sertraline 50mg once daily", "Alprazolam 0.5mg twice daily"],
        "issues": ["Sertraline+Alprazolam CNS depression risk"],
        "safe": False, "difficulty": "medium"
    },
    {
        "name": "Michael Wong", "age": 58, "weight": 75, "gender": "Male",
        "allergies": "none", "conditions": ["hypertension", "depression"],
        "medications": ["Metoprolol 50mg twice daily", "Fluoxetine 20mg once daily", "Tramadol 50mg as needed"],
        "issues": ["Tramadol+Fluoxetine serotonin syndrome risk", "Metoprolol+Fluoxetine interaction"],
        "safe": False, "difficulty": "medium"
    },

    # HARD — 4 patients (added 2 more for better variety)
    {
        "name": "David Wilson", "age": 78, "weight": 55, "gender": "Male",
        "allergies": "sulfa drugs", "conditions": ["kidney disease", "heart failure", "diabetes"],
        "medications": [
            "Metformin 1000mg twice daily", "Ibuprofen 400mg three times daily",
            "Furosemide 40mg once daily", "Digoxin 0.25mg once daily",
            "Glibenclamide 5mg once daily"
        ],
        "issues": [
            "Metformin contraindicated with kidney disease",
            "Ibuprofen contraindicated with kidney disease",
            "Glibenclamide+Furosemide interaction — potassium loss"
        ],
        "safe": False, "difficulty": "hard"
    },
    {
        "name": "Patricia Moore", "age": 82, "weight": 52, "gender": "Female",
        "allergies": "penicillin", "conditions": ["osteoporosis", "kidney disease", "hypertension", "depression"],
        "medications": [
            "Amoxicillin 500mg three times daily", "Ibuprofen 400mg twice daily",
            "Lisinopril 10mg once daily", "Sertraline 50mg once daily",
            "Alendronate 70mg weekly"
        ],
        "issues": [
            "Amoxicillin — penicillin allergy violation",
            "Ibuprofen contraindicated with kidney disease",
            "Ibuprofen reduces Lisinopril effectiveness"
        ],
        "safe": False, "difficulty": "hard"
    },
    {
        "name": "George Harris", "age": 74, "weight": 68, "gender": "Male",
        "allergies": "sulfa drugs", "conditions": ["heart failure", "gout", "type 2 diabetes"],
        "medications": [
            "Hydrochlorothiazide 25mg once daily", "Allopurinol 300mg once daily",
            "Metformin 500mg twice daily", "Digoxin 0.125mg once daily",
            "Captopril 25mg twice daily"
        ],
        "issues": [
            "Hydrochlorothiazide is a sulfa drug — allergy violation",
            "Hydrochlorothiazide worsens gout",
            "Digoxin toxicity risk increases with diuretic-induced hypokalemia"
        ],
        "safe": False, "difficulty": "hard"
    },
    {
        "name": "Helen Nguyen", "age": 80, "weight": 49, "gender": "Female",
        "allergies": "none", "conditions": ["atrial fibrillation", "kidney disease", "depression", "osteoporosis"],
        "medications": [
            "Warfarin 5mg once daily", "Fluoxetine 20mg once daily",
            "Ibuprofen 400mg three times daily", "Alendronate 70mg weekly",
            "Digoxin 0.25mg once daily"
        ],
        "issues": [
            "Warfarin+Fluoxetine significantly increases bleeding risk",
            "Ibuprofen+Warfarin increases bleeding risk",
            "Ibuprofen contraindicated with kidney disease",
            "Digoxin toxicity risk in elderly with low body weight"
        ],
        "safe": False, "difficulty": "hard"
    },
]

TASK_DESCRIPTIONS = {
    "easy": (
        "Review this prescription carefully. Check for allergy violations and obvious dosage errors. "
        "State clearly SAFE or UNSAFE and provide your reasoning."
    ),
    "medium": (
        "Review this multi-drug prescription thoroughly. Identify all drug-drug interactions and allergy violations. "
        "For each issue found, explain the clinical risk. State SAFE or UNSAFE with full explanation."
    ),
    "hard": (
        "Review this complex prescription for an elderly patient with multiple conditions. "
        "Identify ALL interactions, contraindications, allergy violations, and dosage issues specific to "
        "the patient's conditions. State SAFE or UNSAFE with comprehensive clinical reasoning."
    ),
}


class DrugInteractionEnvironment(Environment):
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
        return (
            f"Patient: {p['name']}, {p['gender']}, {p['age']} years old, "
            f"{p['weight']}kg. Allergies: {p['allergies']}. "
            f"Conditions: {', '.join(p['conditions'])}."
        )

    def reset(self, task_name="easy", **kwargs):
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
            episode_score=0.0,
            done=False,
            reward=0.0,
        )

    def step(self, action, **kwargs):
        self.step_count += 1
        p = self.patient
        text = action.prescription_analysis.lower()
        scores = {}

        # --- FIXED: word-boundary safe/unsafe detection ---
        is_unsafe_text = bool(re.search(r'\bunsafe\b', text))
        is_safe_text = bool(re.search(r'\bsafe\b', text)) and not is_unsafe_text

        # Use structured verdict if provided, else fall back to text
        verdict = (action.safety_verdict or "").upper().strip()
        agent_says_unsafe = is_unsafe_text or verdict == "UNSAFE"
        agent_says_safe = (is_safe_text or verdict == "SAFE") and not agent_says_unsafe

        # 0.4 — correct verdict
        if p["safe"]:
            scores["correct_verdict"] = 0.4 if agent_says_safe else 0.0
        else:
            scores["correct_verdict"] = 0.4 if agent_says_unsafe else 0.0

        # 0.3 — issue detection (proportional)
        if not p["issues"]:
            scores["issue_detection"] = 0.3 if scores["correct_verdict"] == 0.4 else 0.0
        else:
            detected = 0
            for issue in p["issues"]:
                keywords = [w for w in issue.lower().split() if len(w) > 3][:4]
                if any(kw in text for kw in keywords):
                    detected += 1
            scores["issue_detection"] = round(0.3 * (detected / len(p["issues"])), 2)

        # 0.2 — explanation quality (by length)
        length = len(action.prescription_analysis)
        scores["explanation_quality"] = 0.2 if length > 150 else (0.1 if length > 60 else 0.0)

        # 0.1 — medical terminology
        terms = [
            "contraindicated", "interaction", "allergy", "allergic", "dosage",
            "adverse", "therapeutic", "bleeding", "renal", "hepatic",
            "serotonin", "toxicity", "contraindication", "hypersensitivity",
            "hypokalemia", "nephrotoxic", "ototoxic", "bradycardia",
        ]
        term_count = sum(1 for t in terms if t in text)
        scores["medical_terminology"] = 0.1 if term_count >= 3 else (0.05 if term_count >= 1 else 0.0)

        reward = round(min(max(sum(scores.values()), 0.05), 0.95), 3)
        self.episode_score = round(
            (self.episode_score * (self.step_count - 1) + reward) / self.step_count, 3
        )
        done = self.step_count >= self.max_steps or (
            scores["correct_verdict"] == 0.4 and reward >= 0.8
        )

        # Build feedback
        verdict_word = "SAFE" if p["safe"] else "UNSAFE"
        if scores["correct_verdict"] == 0.4:
            fb = f"Correct! This prescription is {verdict_word}."
        else:
            fb = f"Incorrect. This prescription is {verdict_word}."
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
            episode_score=self.episode_score,
            done=done,
            reward=reward,
        )

    @property
    def state(self):
        return DrugInteractionState(
            task_name=self.task_name,
            step_count=self.step_count,
            max_steps=self.max_steps,
            episode_score=self.episode_score,
            patient_name=self.patient["name"] if self.patient else "none",
            is_active=self.patient is not None,
            episode_id=self.episode_id or "",
        )
