import asyncio
import websockets
import json

async def test():
    uri = "wss://dasarisathwik27-drug-interaction-env.hf.space/ws"
    async with websockets.connect(uri) as ws:
        # Reset
        await ws.send(json.dumps({"type": "reset", "task_name": "easy", "seed": 42}))
        resp = await ws.recv()
        data = json.loads(resp)
        print("Reset:", data["observation"]["patient_info"])
        
        # Step
        await ws.send(json.dumps({
            "type": "step",
            "prescription_analysis": "This prescription is SAFE. Lisinopril 10mg is within therapeutic range for hypertension. No interactions or contraindications found.",
            "safety_verdict": "SAFE",
            "identified_issues": [],
            "confidence_score": 0.9
        }))
        resp = await ws.recv()
        data = json.loads(resp)
        print("Reward:", data["reward"])
        print("Done:", data["done"])

asyncio.run(test())