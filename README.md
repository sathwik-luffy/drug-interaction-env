# 💊 Drug Interaction RL Environment

An OpenEnv-compliant Reinforcement Learning environment for training AI agents to analyze medical prescriptions and detect dangerous drug interactions.

## 🏥 Overview

This environment simulates a clinical prescription review task where an AI agent must:
- Identify dangerous drug-drug interactions
- Detect allergy violations
- Flag dosage errors and contraindications
- Provide clinical reasoning for its assessment

## 🎯 Tasks

| Difficulty | Description | Example |
|------------|-------------|---------|
| 🟢 Easy | Single drug dosage check | Lisinopril for hypertension |
| 🟡 Medium | Multi-drug interaction detection | Warfarin + Aspirin + Sertraline |
| 🔴 Hard | Complex elderly patient case | 6 medications with kidney disease + allergy |

## 📐 Action Space

```python
class DrugInteractionAction(Action):
    prescription_analysis: str    # Full clinical analysis text
    safety_verdict: str           # "SAFE" or "UNSAFE"
    identified_issues: List[str]  # List of issues found
    confidence_score: float       # Confidence 0.0 to 1.0
```

## 👁️ Observation Space

```python
class DrugInteractionObservation(Observation):
    patient_info: str         # Patient demographics and conditions
    medications: List[str]    # List of prescribed medications
    task_description: str     # What the agent needs to do
    feedback: str             # Feedback from previous step
    score_breakdown: Dict     # Detailed scoring breakdown
    task_name: str            # easy / medium / hard
    step_count: int           # Current step number
    max_steps: int            # Maximum steps per episode
    episode_score: float      # Running episode score
    done: bool                # Whether episode is complete
    reward: float             # Step reward (strictly 0.01–0.99)
```

## 🏆 Reward Function

Rewards are strictly between 0.01 and 0.99, computed from 4 components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct Verdict | 0.40 | SAFE/UNSAFE assessment accuracy |
| Issue Detection | 0.30 | Identifying specific drug interactions |
| Explanation Quality | 0.20 | Depth and completeness of analysis |
| Medical Terminology | 0.10 | Use of clinical language |

## 🚀 Quick Start

### Run with Docker
```bash
docker build -t drug-interaction-env .
docker run -p 7860:7860 drug-interaction-env
```

### Run locally
```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Run inference
```bash
export HF_TOKEN=your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
python inference.py
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start new episode |
| `/step` | POST | Submit prescription analysis |
| `/state` | GET | Get current environment state |
| `/health` | GET | Health check |
| `/leaderboard` | GET | Top model scores |
| `/history` | GET | Recent episodes |
| `/web` | GET | Interactive web UI |
| `/ws` | WebSocket | Real-time interaction |

## 📊 Baseline Results

| Task | Model | Score |
|------|-------|-------|
| Easy | Qwen2.5-72B | 0.990 |
| Medium | Qwen2.5-72B | 0.990 |
| Hard | Qwen2.5-72B | 0.595 |
| **Average** | | **0.858** |

## 🏗️ Environment Structure