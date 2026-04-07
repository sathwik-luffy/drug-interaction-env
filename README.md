---
title: Drug Interaction RL Environment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

python -c "
content = '''# Drug Interaction RL Environment

## Problem
AI systems must safely analyze prescriptions to avoid dangerous drug interactions.
This environment simulates that real-world task for training RL agents.

## Action Space
Agent provides:
- Interaction level (none / low / moderate / critical)
- Recommended action (safe / monitor / adjust / avoid)
- Issues found
- Explanation

## Observation Space
- Patient information (age, weight, conditions, allergies)
- List of prescribed medications with dosages
- Task description
- Feedback from previous step
- Score breakdown

## Tasks

### Easy
Single drug dosage check for a hypertension patient.

### Medium
Multi-drug interaction detection (Warfarin + Aspirin + Sertraline).

### Hard
Complex elderly patient with 6 medications, kidney disease and penicillin allergy.

## Reward Function
- Interaction detection: 0.4
- Severity classification: 0.3
- Recommendation: 0.2
- Structured format: 0.1

## Baseline Scores
- Easy: 1.000
- Medium: 1.000
- Hard: 1.000
- Average: 1.000

## Safety Note
This environment is for AI training simulation only and does not provide real medical advice.
'''
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
"