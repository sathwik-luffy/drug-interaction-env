---
title: Drug Interaction RL Environment
emoji: 💊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
base_path: /web
---

# Drug Interaction RL Environment

Medication errors cause over **1.5 million injuries per year**. This reinforcement learning environment trains AI agents to detect dangerous drug interactions, dosage errors, and allergy violations before they reach patients.

Built for the **Meta PyTorch OpenEnv Hackathon 2026**.

---

## Quick Start

```python
from client import DrugInteractionEnv, DrugInteractionAction

env = DrugInteractionEnv(base_url="https://dasarisathwik27-drug-interaction-env.hf.space")

# Reset environment
obs = env.reset(task_name="medium")
print(obs.patient_info)
print(obs.medications)

# Submit analysis
action = DrugInteractionAction(
    prescription_analysis="This prescription is UNSAFE. Warfarin combined with Aspirin significantly increases bleeding risk. Warfarin combined with Sertraline also increases bleeding risk due to serotonin effects.",
    safety_verdict="UNSAFE",
    identified_issues=["Warfarin+Aspirin bleeding risk", "Warfarin+Sertraline interaction"],
    confidence_score=0.95
)
obs, reward, done = env.step(action)
print(f"Reward: {reward}")
print(f"Feedback: {obs.feedback}")
```

## Install Client

```bash
pip install requests pydantic
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode |
| `/step` | POST | Submit prescription analysis |
| `/state` | GET | Get current episode state |
| `/web` | GET | Web playground UI |

---

## Action Space

```python
DrugInteractionAction(
    prescription_analysis: str,       # Full clinical analysis text
    safety_verdict: str,              # "SAFE" or "UNSAFE"
    identified_issues: List[str],     # List of specific issues found
    confidence_score: float           # Agent confidence 0.0 to 1.0
)
```

## Observation Space

```python
DrugInteractionObservation(
    patient_info: str,        # Patient demographics and conditions
    medications: List[str],   # List of prescribed medications
    task_description: str,    # What the agent needs to do
    feedback: str,            # Feedback from previous step
    score_breakdown: Dict,    # Detailed scoring breakdown
    task_name: str,           # easy / medium / hard
    step_count: int,          # Current step number
    max_steps: int,           # Maximum steps per episode
    episode_score: float      # Running episode score
)
```

---

## Tasks

### Easy
Single drug dosage check. Patient has one or two medications. Agent checks if dosage is appropriate and flags allergy violations.

**Example:** 45-year-old male on Lisinopril 10mg — is the dosage within range?

### Medium
Multi-drug interaction detection. Patient has 2–3 medications. Agent must identify all drug-drug interactions and allergy violations.

**Example:** Female patient on Warfarin + Aspirin + Sertraline — identify all bleeding risks.

### Hard
Complex elderly patient with 4–6 medications and multiple conditions including kidney disease. Agent must identify all interactions, contraindications, and condition-specific risks.

**Example:** 78-year-old male with kidney disease on 5 medications — identify all contraindications and interactions.

---

## Reward Function

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct verdict | 0.40 | Correctly identifies SAFE or UNSAFE |
| Issue detection | 0.30 | Finds specific drug interactions and allergy violations (proportional) |
| Explanation quality | 0.20 | Length and depth of clinical reasoning |
| Medical terminology | 0.10 | Use of correct clinical terms |

**Scoring example:**
```
Input:  Warfarin 5mg + Aspirin 100mg, Female 62yo
Output: UNSAFE — bleeding risk interaction → Score: 1.0

Input:  "Looks fine. No issues found."
Output: Incorrect verdict, no issues detected → Score: 0.0
```

---

## Patient Pool

The environment includes **12 randomized patients** across difficulty levels:

- 4 Easy patients (1–2 medications)
- 4 Medium patients (2–3 medications, interactions)
- 4 Hard patients (4–6 medications, complex conditions)

Each `reset()` call randomly selects a patient from the appropriate difficulty pool, ensuring varied training scenarios.

---

## Baseline Scores

| Task | Model | Score |
|------|-------|-------|
| Easy | Qwen2.5-72B | 0.950 |
| Medium | Qwen2.5-72B | 0.950 |
| Hard | Qwen2.5-72B | 0.950 |
| **Average** | | **0.950** |

---

## Run Inference

```bash
set HF_TOKEN=your_token_here
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
python inference.py
```

---

## Live Environment

[https://huggingface.co/spaces/dasarisathwik27/drug_interaction_env](https://huggingface.co/spaces/dasarisathwik27/drug_interaction_env)

---

## Safety Note

This environment is for AI training simulation only and does not provide real medical advice. All patients and scenarios are fictional.
