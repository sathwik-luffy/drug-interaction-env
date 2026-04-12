import uuid
import random
from openenv.core.env_server.interfaces import Environment

try:
    from ..models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState
except ImportError:
    from models import DrugInteractionAction, DrugInteractionObservation, DrugInteractionState

try:
    from .database import init_db, get_random_patient, log_episode, log_step, complete_episode, update_leaderboard
except ImportError:
    from server.database import init_db, get_random_patient, log_episode, log_step, complete_episode, update_leaderboard

init_db()

TASK_DESCRIPTIONS = {
    "easy": "Review this prescription carefully. Check for allergy violations and obvious dosage errors. State clearly SAFE or UNSAFE and provide your reasoning.",
    "medium": "Review this multi-drug prescription thoroughly. Identify all drug-drug interactions and allergy violations. For each issue found, explain the clinical risk. State SAFE or UNSAFE with full explanation.",
    "hard": "Review this complex prescription for an elderly patient with multiple conditions. Identify ALL interactions, contraindications, allergy violations, and dosage issues. State SAFE or UNSAFE with comprehensive clinical reasoning."
}

class DrugInteractionEnvironment(Environment):
    def __init__(self):
        self.task_name = "easy"
        self.step_count = 0
        self.max_steps = 3
        self.episode_score = 0.0
        self.patient = None
        self.episode_id = None
        self.model_name = "unknown"

    def _build_patient_info(self, p):
        return (f"Patient: {p['name']}, {p['gender']}, {p['age']} years old, "
                f"{p['weight']}kg. Allergies: {p['allergies']}. "
                f"Conditions: {', '.join(p['conditions'])}.")

    def reset(self, task_name="easy", model_name="unknown", seed=None, **kwargs):
        self.task_name = task_name
        self.step_count = 0
        self.episode_score = 0.0
        self.episode_id = str(uuid.uuid4())[:8]
        self.model_name = model_name
        if seed is not None:
            random.seed(seed)
        self.patient = get_random_patient(task_name)
        log_episode(self.episode_id, task_name, self.patient["name"], model_name)
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
            reward=0.0
        )

    def step(self, action, **kwargs):
        self.step_count += 1
        p = self.patient
        text = action.prescription_analysis.lower()
        verdict = (action.safety_verdict or "").upper()
        scores = {}

        is_safe_text = "safe" in text and "unsafe" not in text
        is_unsafe_text = "unsafe" in text

        if p["safe"]:
            scores["correct_verdict"] = 0.4 if (is_safe_text or verdict == "SAFE") else 0.0
        else:
            scores["correct_verdict"] = 0.4 if (is_unsafe_text or verdict == "UNSAFE") else 0.0

        if not p["issues"]:
            scores["issue_detection"] = 0.3 if scores["correct_verdict"] == 0.4 else 0.0
        else:
            detected = 0
            for issue in p["issues"]:
                keywords = issue.lower().split()[:4]
                if sum(1 for kw in keywords if kw in text and len(kw) > 3) >= 2:
                    detected += 1
            scores["issue_detection"] = round(0.3 * (detected / len(p["issues"])), 2)

        meds_mentioned = sum(1 for med in p["medications"] if med.split()[0].lower() in text)
        length = len(action.prescription_analysis)
        if meds_mentioned >= len(p["medications"]) and length > 200:
            scores["explanation_quality"] = 0.2
        elif meds_mentioned >= 1 and length > 100:
            scores["explanation_quality"] = 0.12
        else:
            scores["explanation_quality"] = 0.05

        terms = ["contraindicated", "interaction", "allergy", "allergic", "dosage",
                 "adverse", "therapeutic", "bleeding", "renal", "hepatic",
                 "serotonin", "toxicity", "contraindication", "hypersensitivity",
                 "pharmacokinetic", "drug-drug", "side effect", "risk"]
        term_count = sum(1 for t in terms if t in text)
        scores["medical_terminology"] = 0.1 if term_count >= 6 else (0.07 if term_count >= 4 else (0.04 if term_count >= 2 else 0.01))

        raw = sum(scores.values())
        noise = random.uniform(-0.04, 0.04)
        reward = round(min(max(raw + noise, 0.01), 0.99), 3)

        self.episode_score = round((self.episode_score * (self.step_count - 1) + reward) / self.step_count, 3)
        done = self.step_count >= self.max_steps or (scores["correct_verdict"] == 0.4 and reward >= 0.75)

        log_step(self.episode_id, self.step_count, action.prescription_analysis, verdict, reward, scores)
        if done:
            complete_episode(self.episode_id, self.step_count, self.episode_score)
            update_leaderboard(self.model_name, self.task_name, self.episode_score, self.episode_id)

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
            episode_score=self.episode_score,
            done=done,
            reward=reward
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
            episode_id=self.episode_id or ""
        )
