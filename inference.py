import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
BASE_URL = "https://dasarisathwik27-drug-interaction-env.hf.space"

def run_task(task_name):
    print(f"[START] task={task_name} env=drug_interaction_env model={MODEL_NAME}")
    
    # Reset
    res = requests.post(f"{BASE_URL}/reset", params={"task_name": task_name})
    data = res.json()
    obs = data.get("observation", data)
    
    patient_info = obs.get("patient_info", "")
    medications = obs.get("medications", [])
    task_desc = obs.get("task_description", "")
    
    prompt = f"Patient: {patient_info}\nMedications: {medications}\nTask: {task_desc}"
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    action_text = response.choices[0].message.content
    
    # Step
    res2 = requests.post(
        f"{BASE_URL}/step",
        json={"prescription_analysis": action_text, "safety_verdict": "UNSAFE" if "unsafe" in action_text.lower() else "SAFE"},
        headers={"Content-Type": "application/json"}
    )
    result = res2.json()
    
    # Handle both old and new response formats
    reward = result.get("reward", 0.0)
    done = result.get("done", True)
    obs2 = result.get("observation", {})
    if isinstance(obs2, dict):
        reward = obs2.get("reward", reward)
    
    print(f"[STEP] step=1 action={action_text[:80]} reward={reward:.2f} done={str(done).lower()} error=null")
    print(f"[END] success=true steps=1 score={reward:.3f} rewards={reward:.2f}")
    return reward

scores = []
for task in ["easy", "medium", "hard"]:
    print(f"[DEBUG] Running task: {task}")
    score = run_task(task)
    print(f"[DEBUG] Task {task} score: {score:.3f}")
    scores.append(score)

print(f"[DEBUG] Average score across all tasks: {sum(scores)/len(scores):.3f}")