---
title: Drug Interaction RL Environment
emoji: 💊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Drug Interaction RL Environment

A reinforcement learning environment where an AI agent reviews medical prescriptions and identifies dangerous drug interactions, dosage errors, allergy violations, and contraindications.

Built for the **Meta PyTorch OpenEnv Hackathon 2026**.

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

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /health | GET | Health check |
| /reset | POST | Start new episode |
| /step | POST | Submit prescription analysis |
| /state | GET | Get current episode state |
| /web | GET | Web playground UI |

## Action Space

```python
DrugInteractionAction(
    prescription_analysis: str,       # Full text analysis
    safety_verdict: str,              # "SAFE" or "UNSAFE"
    identified_issues: List[str],     # List of issues found
    confidence_score: float           # 0.0 to 1.0
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

## Tasks

### Easy
Single drug dosage check. Patient has one condition and one medication. Agent checks if dosage is appropriate and flags allergy violations.

### Medium
Multi-drug interaction detection. Patient has 2-3 medications. Agent must identify all drug-drug interactions and allergy violations.

### Hard
Complex elderly patient with 4-6 medications and multiple conditions including kidney disease. Agent must identify all interactions, contraindications, and condition-specific risks.

## Reward Function

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct verdict | 0.40 | Correctly identifies SAFE or UNSAFE |
| Issue detection | 0.30 | Finds specific drug interactions and allergy violations |
| Explanation quality | 0.20 | Length and depth of clinical reasoning |
| Medical terminology | 0.10 | Use of correct medical terms |

## Baseline Scores

| Task | Model | Score |
|------|-------|-------|
| Easy | Qwen2.5-72B | 0.970 |
| Medium | Qwen2.5-72B | 0.970 |
| Hard | Qwen2.5-72B | 0.970 |
| **Average** | | **0.970** |

## Patient Pool

The environment includes 10 randomized patients across difficulty levels:
- 4 Easy patients (1-2 medications)
- 4 Medium patients (2-3 medications, interactions)
- 2 Hard patients (4-6 medications, complex conditions)

## Safety Note

This environment is for AI training simulation only and does not provide real medical advice.
