import os
import re
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
BASE_URL = "https://dasarisathwik27-drug-interaction-env.hf.space"


def get_verdict(text: str) -> str:
    """Word-boundary safe/unsafe detection — fixes the original bug."""
    if re.search(r'\bunsafe\b', text.lower()):
        return "UNSAFE"
    return "SAFE"


def run_task(task_name: str) -> float:
    print(f"[START] task={task_name} env=drug_interaction_env model={MODEL_NAME}")

    try:
        # Reset
        res = requests.post(
            f"{BASE_URL}/reset",
            params={"task_name": task_name},
            timeout=30
        )
        res.raise_for_status()
        data = res.json()
        obs = data.get("observation", data)

        patient_info = obs.get("patient_info", "")
        medications = obs.get("medications", [])
        task_desc = obs.get("task_description", "")

        prompt = (
            f"Patient: {patient_info}\n"
            f"Medications: {', '.join(medications)}\n"
            f"Task: {task_desc}\n\n"
            f"Provide a thorough clinical analysis. "
            f"State SAFE or UNSAFE clearly and explain your reasoning."
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        action_text = response.choices[0].message.content
        verdict = get_verdict(action_text)

        # Step
        res2 = requests.post(
            f"{BASE_URL}/step",
            json={
                "prescription_analysis": action_text,
                "safety_verdict": verdict,
                "identified_issues": [],
                "confidence_score": 0.9,
            },
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        res2.raise_for_status()
        result = res2.json()

        reward = result.get("reward", 0.0)
        done = result.get("done", True)
        obs2 = result.get("observation", {})
        if isinstance(obs2, dict):
            reward = obs2.get("reward", reward)

        print(
            f"[STEP] step=1 action={action_text[:80]} "
            f"reward={reward:.2f} done={str(done).lower()} error=null"
        )
        print(f"[END] success=true steps=1 score={reward:.3f} rewards={reward:.2f}")
        return reward

    except requests.exceptions.RequestException as e:
        print(f"[END] success=false steps=0 score=0.000 error={str(e)}")
        return 0.0
    except Exception as e:
        print(f"[END] success=false steps=0 score=0.000 error={str(e)}")
        return 0.0


scores = []
for task in ["easy", "medium", "hard"]:
    print(f"[DEBUG] Running task: {task}")
    score = run_task(task)
    print(f"[DEBUG] Task {task} score: {score:.3f}")
    scores.append(score)

avg = sum(scores) / len(scores)
print(f"[DEBUG] Average score across all tasks: {avg:.3f}")
