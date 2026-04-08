content = """from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import DrugInteractionAction, DrugInteractionObservation
from server.drug_interaction_env_environment import DrugInteractionEnvironment

app = FastAPI()
env = DrugInteractionEnvironment()

@app.get("/web", response_class=HTMLResponse)
def web():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Drug Interaction RL Environment</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }
  header { background: linear-gradient(135deg, #1a1a3e, #2d2d6b); padding: 24px 40px; border-bottom: 2px solid #4a4aff; }
  header h1 { font-size: 26px; color: #ffffff; letter-spacing: 1px; }
  header p { font-size: 13px; color: #9999cc; margin-top: 4px; }
  .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
  .card { background: #1a1a2e; border: 1px solid #2a2a5a; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
  .card h2 { font-size: 16px; color: #7a7aff; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }
  label { font-size: 13px; color: #9999cc; display: block; margin-bottom: 6px; }
  select { width: 100%; padding: 10px 14px; background: #0f0f1a; border: 1px solid #3a3a7a; border-radius: 8px; color: #e0e0e0; font-size: 14px; margin-bottom: 16px; }
  textarea { width: 100%; padding: 12px 14px; background: #0f0f1a; border: 1px solid #3a3a7a; border-radius: 8px; color: #e0e0e0; font-size: 14px; resize: vertical; min-height: 140px; font-family: inherit; }
  .btn-row { display: flex; gap: 12px; margin-top: 16px; }
  button { padding: 10px 28px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
  .btn-reset { background: #2d2d6b; color: #ffffff; border: 1px solid #4a4aff; }
  .btn-reset:hover { background: #4a4aff; }
  .btn-step { background: #4a4aff; color: #ffffff; }
  .btn-step:hover { background: #6a6aff; }
  .response-box { background: #0f0f1a; border: 1px solid #2a2a5a; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; color: #00ff88; min-height: 100px; white-space: pre-wrap; word-break: break-all; }
  .reward-badge { display: inline-block; padding: 6px 18px; border-radius: 20px; font-weight: 700; font-size: 15px; margin-top: 12px; }
  .footer { text-align: center; padding: 24px; font-size: 12px; color: #555577; }
</style>
</head>
<body>
<header>
  <h1>💊 Drug Interaction RL Environment</h1>
  <p>Reinforcement Learning Environment for Medical Prescription Analysis</p>
</header>
<div class="container">
  <div class="card">
    <h2>Step 1 — Select Task & Reset</h2>
    <label>Difficulty Level</label>
    <select id="task">
      <option value="easy">🟢 Easy — Single drug dosage check</option>
      <option value="medium">🟡 Medium — Multi-drug interaction detection</option>
      <option value="hard">🔴 Hard — Complex elderly patient case</option>
    </select>
    <button class="btn-reset" onclick="reset()">⟳ Reset Environment</button>
  </div>
  <div class="card" id="obs-card" style="display:none">
    <h2>Observation</h2>
    <div class="response-box" id="obs-box">—</div>
  </div>
  <div class="card">
    <h2>Step 2 — Enter Prescription Analysis</h2>
    <label>Your Analysis (state SAFE or UNSAFE and explain why)</label>
    <textarea id="action" placeholder="e.g. This prescription is SAFE. Lisinopril 10mg is within the standard adult dose range of 10-40mg daily..."></textarea>
    <div class="btn-row">
      <button class="btn-step" onclick="step()">▶ Submit Step</button>
    </div>
  </div>
  <div class="card" id="result-card" style="display:none">
    <h2>Result</h2>
    <div class="response-box" id="result-box">—</div>
    <div id="reward-badge"></div>
  </div>
</div>
<div class="footer">Drug Interaction RL Environment — OpenEnv Hackathon 2026</div>
<script>
async function reset() {
  let task = document.getElementById("task").value;
  let r = await fetch("/reset?task_name=" + task, {method: "POST"});
  let d = await r.json();
  document.getElementById("obs-card").style.display = "block";
  document.getElementById("obs-box").innerText = JSON.stringify(d.observation, null, 2);
  document.getElementById("result-card").style.display = "none";
}
async function step() {
  let action = document.getElementById("action").value;
  if (!action.trim()) { alert("Please enter your analysis first!"); return; }
  let r = await fetch("/step", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({prescription_analysis: action})});
  let d = await r.json();
  document.getElementById("result-card").style.display = "block";
  document.getElementById("result-box").innerText = JSON.stringify(d, null, 2);
  let reward = d.reward;
  let color = reward >= 0.8 ? "#00ff88" : reward >= 0.5 ? "#ffaa00" : "#ff4444";
  document.getElementById("reward-badge").innerHTML = "<span class=reward-badge style=background:" + color + "20;color:" + color + ";border:1px solid " + color + ">Reward: " + reward.toFixed(2) + " / 1.00</span>";
}
</script>
</body>
</html>'''

@app.post("/reset")
def reset(task_name: str = "easy"):
    obs = env.reset(task_name)
    return {"observation": obs.dict(), "reward": 0.0, "done": False}

@app.post("/step")
def step(action: DrugInteractionAction):
    obs, reward, done = env.step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done}

@app.get("/state")
def state():
    t = env.tasks[env.task_name]
    obs = DrugInteractionObservation(patient_info=t["patient_info"], medications=t["medications"], task_description=t["task_description"], feedback="Current state.", score_breakdown={}, task_name=env.task_name)
    return {"observation": obs.dict()}
"""
with open("server/app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done!")