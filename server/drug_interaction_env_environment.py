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
        "issues": [], "safe": True, "difficulty": "easy",
        "issue_keywords": [], "mechanism": [],
    },
    {
        "name": "Robert Lee", "age": 55, "weight": 90, "gender": "Male",
        "allergies": "none", "conditions": ["type 2 diabetes", "hypertension"],
        "medications": ["Metformin 500mg twice daily", "Amlodipine 5mg once daily"],
        "issues": [], "safe": True, "difficulty": "easy",
        "issue_keywords": [], "mechanism": [],
    },
    {
        "name": "Lisa Taylor", "age": 50, "weight": 72, "gender": "Female",
        "allergies": "none", "conditions": ["hypertension", "high cholesterol"],
        "medications": ["Amlodipine 10mg once daily", "Atorvastatin 20mg once daily"],
        "issues": [], "safe": True, "difficulty": "easy",
        "issue_keywords": [], "mechanism": [],
    },
    {
        "name": "James Brown", "age": 60, "weight": 85, "gender": "Male",
        "allergies": "aspirin", "conditions": ["chest pain"],
        "medications": ["Aspirin 100mg once daily", "Clopidogrel 75mg once daily"],
        "issues": ["Patient is allergic to Aspirin — direct allergy violation"],
        "safe": False, "difficulty": "easy",
        "issue_keywords": [["aspirin", "allergy", "allergic"]],
        "mechanism": ["allergy"],
    },

    # MEDIUM — 4 patients
    {
        "name": "Mary Johnson", "age": 62, "weight": 65, "gender": "Female",
        "allergies": "none", "conditions": ["atrial fibrillation", "depression"],
        "medications": ["Warfarin 5mg once daily", "Aspirin 100mg once daily", "Sertraline 50mg once daily"],
        "issues": ["Warfarin+Aspirin increases bleeding risk", "Warfarin+Sertraline increases bleeding risk"],
        "safe": False, "difficulty": "medium",
        "issue_keywords": [
            ["warfarin", "aspirin", "bleeding"],
            ["warfarin", "sertraline", "bleeding", "serotonin"],
        ],
        "mechanism": ["bleeding", "anticoagulant", "serotonin"],
    },
    {
        "name": "Susan Chen", "age": 70, "weight": 58, "gender": "Female",
        "allergies": "penicillin", "conditions": ["pneumonia", "heart failure"],
        "medications": ["Amoxicillin 500mg three times daily", "Furosemide 40mg once daily"],
        "issues": ["Amoxicillin contains penicillin — patient is allergic"],
        "safe": False, "difficulty": "medium",
        "issue_keywords": [["amoxicillin", "penicillin", "allergy", "allergic"]],
        "mechanism": ["allergy", "hypersensitivity"],
    },
    {
        "name": "Emma Davis", "age": 35, "weight": 70, "gender": "Female",
        "allergies": "none", "conditions": ["depression", "anxiety"],
        "medications": ["Sertraline 50mg once daily", "Alprazolam 0.5mg twice daily"],
        "issues": ["Sertraline+Alprazolam CNS depression risk"],
        "safe": False, "difficulty": "medium",
        "issue_keywords": [["sertraline", "alprazolam", "cns", "sedation", "depression"]],
        "mechanism": ["cns", "sedation", "respiratory"],
    },
    {
        "name": "Michael Wong", "age": 58, "weight": 75, "gender": "Male",
        "allergies": "none", "conditions": ["hypertension", "depression"],
        "medications": ["Metoprolol 50mg twice daily", "Fluoxetine 20mg once daily", "Tramadol 50mg as needed"],
        "issues": ["Tramadol+Fluoxetine serotonin syndrome risk", "Metoprolol+Fluoxetine interaction"],
        "safe": False, "difficulty": "medium",
        "issue_keywords": [
            ["tramadol", "fluoxetine", "serotonin"],
            ["metoprolol", "fluoxetine", "bradycardia"],
        ],
        "mechanism": ["serotonin", "bradycardia", "toxicity"],
    },

    # HARD — 4 patients
    {
        "name": "David Wilson", "age": 78, "weight": 55, "gender": "Male",
        "allergies": "sulfa drugs", "conditions": ["kidney disease", "heart failure", "diabetes"],
        "medications": [
            "Metformin 1000mg twice daily", "Ibuprofen 400mg three times daily",
            "Furosemide 40mg once daily", "Digoxin 0.25mg once daily", "Glibenclamide 5mg once daily",
        ],
        "issues": [
            "Metformin contraindicated with kidney disease",
            "Ibuprofen contraindicated with kidney disease",
            "Glibenclamide+Furosemide — potassium loss risk",
        ],
        "safe": False, "difficulty": "hard",
        "issue_keywords": [
            ["metformin", "kidney", "renal", "contraindicated"],
            ["ibuprofen", "kidney", "renal", "nephrotoxic"],
            ["glibenclamide", "furosemide", "potassium", "hypokalemia"],
        ],
        "mechanism": ["renal", "nephrotoxic", "contraindicated", "hypokalemia"],
    },
    {
        "name": "Patricia Moore", "age": 82, "weight": 52, "gender": "Female",
        "allergies": "penicillin", "conditions": ["osteoporosis", "kidney disease", "hypertension", "depression"],
        "medications": [
            "Amoxicillin 500mg three times daily", "Ibuprofen 400mg twice daily",
            "Lisinopril 10mg once daily", "Sertraline 50mg once daily", "Alendronate 70mg weekly",
        ],
        "issues": [
            "Amoxicillin — penicillin allergy violation",
            "Ibuprofen contraindicated with kidney disease",
            "Ibuprofen reduces Lisinopril effectiveness",
        ],
        "safe": False, "difficulty": "hard",
        "issue_keywords": [
            ["amoxicillin", "penicillin", "allergy", "allergic"],
            ["ibuprofen", "kidney", "renal", "contraindicated"],
            ["ibuprofen", "lisinopril", "effectiveness", "reduces"],
        ],
        "mechanism": ["allergy", "renal", "contraindicated", "nephrotoxic"],
    },
    {
        "name": "George Harris", "age": 74, "weight": 68, "gender": "Male",
        "allergies": "sulfa drugs", "conditions": ["heart failure", "gout", "type 2 diabetes"],
        "medications": [
            "Hydrochlorothiazide 25mg once daily", "Allopurinol 300mg once daily",
            "Metformin 500mg twice daily", "Digoxin 0.125mg once daily", "Captopril 25mg twice daily",
        ],
        "issues": [
            "Hydrochlorothiazide is a sulfa drug — allergy violation",
            "Hydrochlorothiazide worsens gout",
            "Digoxin toxicity risk with diuretic-induced hypokalemia",
        ],
        "safe": False, "difficulty": "hard",
        "issue_keywords": [
            ["hydrochlorothiazide", "sulfa", "allergy", "allergic"],
            ["hydrochlorothiazide", "gout", "uric"],
            ["digoxin", "toxicity", "hypokalemia", "potassium"],
        ],
        "mechanism": ["allergy", "toxicity", "hypokalemia", "contraindicated"],
    },
    {
        "name": "Helen Nguyen", "age": 80, "weight": 49, "gender": "Female",
        "allergies": "none", "conditions": ["atrial fibrillation", "kidney disease", "depression", "osteoporosis"],
        "medications": [
            "Warfarin 5mg once daily", "Fluoxetine 20mg once daily",
            "Ibuprofen 400mg three times daily", "Alendronate 70mg weekly", "Digoxin 0.25mg once daily",
        ],
        "issues": [
            "Warfarin+Fluoxetine increases bleeding risk",
            "Ibuprofen contraindicated with kidney disease",
            "Digoxin toxicity risk in elderly",
        ],
        "safe": False, "difficulty": "hard",
        "issue_keywords": [
            ["warfarin", "fluoxetine", "bleeding"],
            ["ibuprofen", "kidney", "renal", "contraindicated"],
            ["digoxin", "toxicity", "elderly"],
        ],
        "mechanism": ["bleeding", "renal", "toxicity", "contraindicated"],
    },
]

TASK_DESCRIPTIONS = {
    "easy": (
        "Review this prescription carefully. Check for allergy violations and obvious dosage errors. "
        "State clearly SAFE or UNSAFE and provide your reasoning."
    ),
    "medium": (
        "Review this multi-drug prescription thoroughly. Identify all drug-drug interactions and allergy violations. "
        "For each issue found, explain the clinical risk and mechanism. State SAFE or UNSAFE with full explanation."
    ),
    "hard": (
        "Review this complex prescription for an elderly patient with multiple conditions. "
        "Identify ALL interactions, contraindications, allergy violations, and dosage issues. "
        "Explain the mechanism of each risk. State SAFE or UNSAFE with comprehensive clinical reasoning."
    ),
}


def _score_verdict(p, agent_says_unsafe, agent_says_safe, confidence):
    """0.40 — verdict with confidence calibration and partial credit."""
    correct = (p["safe"] and agent_says_safe) or (not p["safe"] and agent_says_unsafe)
    wrong = (p["safe"] and agent_says_unsafe) or (not p["safe"] and agent_says_safe)

    if correct:
        score = 0.4 if confidence >= 0.8 else round(0.4 * 0.9, 3)
    elif wrong:
        penalty = round(0.15 * confidence, 3)
        score = max(0.0, round(0.05 - penalty, 3))
    else:
        score = 0.05  # no clear verdict

    return {"correct_verdict": score}


def _score_issues(p, text):
    """0.30 — requires 2+ keywords per issue to count as detected."""
    if not p["issues"]:
        return {"issue_detection": 0.3}

    detected = 0
    for kw_group in p["issue_keywords"]:
        matches = sum(1 for kw in kw_group if kw in text)
        if matches >= 2:
            detected += 1

    ratio = detected / len(p["issues"])
    return {"issue_detection": round(0.3 * ratio, 3)}


def _score_explanation(p, text):
    """0.20 — rewards length + mechanism explanation + drug specificity."""
    score = 0.0

    # Length (max 0.08)
    length = len(text)
    if length > 300:
        score += 0.08
    elif length > 150:
        score += 0.05
    elif length > 60:
        score += 0.02

    # Mechanism — explains WHY (max 0.08)
    mechanism_words = p.get("mechanism", [])
    if mechanism_words:
        mech_hits = sum(1 for m in mechanism_words if m in text)
        score += min(0.08, round(0.08 * (mech_hits / len(mechanism_words)), 3))
    else:
        if "safe" in text and "unsafe" not in text:
            score += 0.04

    # Drug specificity (max 0.04)
    all_drugs = [med.split()[0].lower() for med in p["medications"]]
    drug_hits = sum(1 for d in all_drugs if d in text)
    score += min(0.04, round(0.04 * (drug_hits / max(len(all_drugs), 1)), 3))

    return {"explanation_quality": round(min(score, 0.2), 3)}


def _score_terminology(text):
    """0.10 — checks contextual pairs, not just isolated words."""
    contextual_pairs = [
        ("contraindicated", ["kidney", "renal", "hepatic", "disease"]),
        ("interaction", ["drug", "risk", "bleeding", "serotonin"]),
        ("allergy", ["allergic", "penicillin", "aspirin", "sulfa"]),
        ("bleeding", ["risk", "warfarin", "aspirin", "anticoagulant"]),
        ("toxicity", ["digoxin", "lithium", "narrow", "therapeutic"]),
        ("serotonin", ["syndrome", "risk", "fluoxetine", "tramadol"]),
        ("contraindication", ["renal", "hepatic", "absolute"]),
        ("adverse", ["effect", "reaction", "drug"]),
    ]
    score = 0.0
    per_pair = 0.1 / len(contextual_pairs)
    for term, context_words in contextual_pairs:
        if term in text:
            pos = text.find(term)
            window = text[max(0, pos - 60): pos + 60]
            if any(cw in window for cw in context_words):
                score += per_pair
    return {"medical_terminology": round(min(score, 0.1), 3)}


class DrugInteractionEnvironment(Environment):
    def __init__(self):
        self.task_name = "easy"
        self.step_count = 0
        self.max_steps = 1
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

        is_unsafe_text = bool(re.search(r'\bunsafe\b', text))
        is_safe_text = bool(re.search(r'\bsafe\b', text)) and not is_unsafe_text
        verdict = (action.safety_verdict or "").upper().strip()
        agent_says_unsafe = is_unsafe_text or verdict == "UNSAFE"
        agent_says_safe = (is_safe_text or verdict == "SAFE") and not agent_says_unsafe
        confidence = float(action.confidence_score or 0.5)

        scores = {}
        scores.update(_score_verdict(p, agent_says_unsafe, agent_says_safe, confidence))
        scores.update(_score_issues(p, text))
        scores.update(_score_explanation(p, text))
        scores.update(_score_terminology(text))

        raw = sum(scores.values())
        reward = round(min(max(raw, 0.05), 0.95), 3)

        self.episode_score = round(
            (self.episode_score * (self.step_count - 1) + reward) / self.step_count, 3
        )
        done = self.step_count >= self.max_steps or reward >= 0.8

        verdict_word = "SAFE" if p["safe"] else "UNSAFE"
        if scores["correct_verdict"] >= 0.35:
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