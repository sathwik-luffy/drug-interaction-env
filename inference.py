import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN if HF_TOKEN else "dummy")

BASE_URL = "https://dasarisathwik27-drug-interaction-env.hf.space"

def run_task(task_name):
    try:
        print(f"[START] task={task_name} env=drug_interaction_env model={MODEL_NAME}")
        res = requests.post(f"{BASE_URL}/reset", params={"task_name": task_name}, timeout=30)
        obs = res.json()["observation"]
        prompt = f"Patient: {obs['patient_info']}\nMedications: {obs['medications']}\nTask: {obs['task_description']}"
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        action_text = response.choices[0].message.content
        print(f"[STEP] step=1 action={action_text[:80]} reward=pending done=false error=null")
        res2 = requests.post(f"{BASE_URL}/step", json={"prescription_analysis": action_text}, timeout=30)
        result = res2.json()
        reward = result["reward"]
        print(f"[STEP] step=1 action={action_text[:80]} reward={reward:.2f} done=true error=null")
        print(f"[END] success=true steps=1 score={reward:.3f} rewards={reward:.2f}")
        return reward
    except Exception as e:
        print(f"[STEP] step=1 action=error reward=0.01 done=true error={str(e)}")
        print(f"[END] success=false steps=1 score=0.01 rewards=0.01")
        return 0.01

scores = []
for task in ["easy", "medium", "hard"]:
    print(f"[DEBUG] Running task: {task}")
    score = run_task(task)
    print(f"[DEBUG] Task {task} score: {score:.3f}")
    scores.append(score)

print(f"[DEBUG] Average score across all tasks: {sum(scores)/len(scores):.3f}")