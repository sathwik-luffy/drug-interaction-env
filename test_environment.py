"""
Unit tests for DrugInteractionEnvironment.
Tests reset(), step(), and state() following OpenEnv conventions.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from server.drug_interaction_env_environment import DrugInteractionEnvironment
    from models import DrugInteractionAction
except ImportError:
    from drug_interaction_env.server.drug_interaction_env_environment import DrugInteractionEnvironment
    from drug_interaction_env.models import DrugInteractionAction


# ── helpers ──────────────────────────────────────────────────────────────────

def make_env():
    return DrugInteractionEnvironment()


def correct_action(text="This prescription is UNSAFE. Warfarin combined with Aspirin "
                        "increases bleeding risk due to anticoagulant interaction. "
                        "This combination is contraindicated and should be avoided."):
    return DrugInteractionAction(
        prescription_analysis=text,
        safety_verdict="UNSAFE",
        identified_issues=["Warfarin+Aspirin bleeding risk"],
        confidence_score=0.95,
    )


def wrong_action():
    return DrugInteractionAction(
        prescription_analysis="Everything looks fine. SAFE.",
        safety_verdict="SAFE",
        identified_issues=[],
        confidence_score=0.5,
    )


def vague_action():
    return DrugInteractionAction(
        prescription_analysis="I am not sure about this prescription.",
        safety_verdict="UNKNOWN",
        identified_issues=[],
        confidence_score=0.3,
    )


# ── reset() tests ─────────────────────────────────────────────────────────────

def test_reset_returns_observation():
    env = make_env()
    obs = env.reset(task_name="easy")
    assert obs is not None, "reset() should return an observation"
    print("PASS test_reset_returns_observation")


def test_reset_has_required_fields():
    env = make_env()
    obs = env.reset(task_name="easy")
    assert obs.patient_info, "patient_info should not be empty"
    assert obs.medications, "medications should not be empty"
    assert obs.task_description, "task_description should not be empty"
    assert obs.task_name == "easy", "task_name should match requested difficulty"
    assert obs.reward == 0.0, "initial reward should be 0.0"
    assert obs.done == False, "done should be False after reset"
    print("PASS test_reset_has_required_fields")


def test_reset_medium_task():
    env = make_env()
    obs = env.reset(task_name="medium")
    assert obs.task_name == "medium"
    assert len(obs.medications) >= 2, "medium task should have 2+ medications"
    print("PASS test_reset_medium_task")


def test_reset_hard_task():
    env = make_env()
    obs = env.reset(task_name="hard")
    assert obs.task_name == "hard"
    assert len(obs.medications) >= 4, "hard task should have 4+ medications"
    print("PASS test_reset_hard_task")


def test_reset_randomizes_patient():
    """Run reset 10 times and check we get at least 2 different patients."""
    env = make_env()
    names = set()
    for _ in range(10):
        obs = env.reset(task_name="easy")
        # extract name from patient_info string
        name = obs.patient_info.split("Patient:")[1].split(",")[0].strip()
        names.add(name)
    assert len(names) > 1, "reset() should randomize patients, got only one patient in 10 tries"
    print(f"PASS test_reset_randomizes_patient (got {len(names)} unique patients)")


def test_reset_clears_previous_episode():
    env = make_env()
    env.reset(task_name="easy")
    env.step(wrong_action())
    # now reset again
    obs = env.reset(task_name="easy")
    assert obs.step_count == 0, "step_count should reset to 0"
    assert obs.episode_score == 0.0, "episode_score should reset to 0.0"
    print("PASS test_reset_clears_previous_episode")


# ── step() tests ──────────────────────────────────────────────────────────────

def test_step_returns_observation():
    env = make_env()
    env.reset(task_name="medium")
    obs = env.step(correct_action())
    assert obs is not None, "step() should return an observation"
    print("PASS test_step_returns_observation")


def test_step_reward_in_valid_range():
    env = make_env()
    env.reset(task_name="medium")
    obs = env.step(correct_action())
    assert 0.0 < obs.reward < 1.0, f"reward must be strictly between 0 and 1, got {obs.reward}"
    print(f"PASS test_step_reward_in_valid_range (reward={obs.reward})")


def test_step_correct_answer_scores_high():
    env = make_env()
    # use Mary Johnson — always unsafe with Warfarin+Aspirin
    env.reset(task_name="medium")
    # try up to 5 times to get an unsafe patient
    for _ in range(5):
        obs = env.reset(task_name="medium")
        if "Warfarin" in str(obs.medications):
            break
    obs = env.step(correct_action())
    assert obs.reward >= 0.7, f"correct detailed answer should score >= 0.7, got {obs.reward}"
    print(f"PASS test_step_correct_answer_scores_high (reward={obs.reward})")


def test_step_wrong_answer_scores_low():
    env = make_env()
    env.reset(task_name="medium")
    obs = env.step(wrong_action())
    assert obs.reward <= 0.5, f"wrong answer should score <= 0.5, got {obs.reward}"
    print(f"PASS test_step_wrong_answer_scores_low (reward={obs.reward})")


def test_step_has_score_breakdown():
    env = make_env()
    env.reset(task_name="easy")
    obs = env.step(correct_action())
    assert isinstance(obs.score_breakdown, dict), "score_breakdown should be a dict"
    assert len(obs.score_breakdown) > 0, "score_breakdown should not be empty"
    print(f"PASS test_step_has_score_breakdown ({list(obs.score_breakdown.keys())})")


def test_step_has_feedback():
    env = make_env()
    env.reset(task_name="easy")
    obs = env.step(correct_action())
    assert obs.feedback, "feedback should not be empty after step"
    print(f"PASS test_step_has_feedback")


def test_step_increments_step_count():
    env = make_env()
    env.reset(task_name="easy")
    obs = env.step(vague_action())
    assert obs.step_count == 1, f"step_count should be 1, got {obs.step_count}"
    print("PASS test_step_increments_step_count")


def test_step_done_after_max_steps():
    env = make_env()
    env.reset(task_name="easy")
    obs = env.step(vague_action())
    assert obs.done == True, "done should be True after max_steps=1"
    print("PASS test_step_done_after_max_steps")


def test_step_reward_never_exactly_zero():
    env = make_env()
    for task in ["easy", "medium", "hard"]:
        env.reset(task_name=task)
        obs = env.step(wrong_action())
        assert obs.reward > 0.0, f"reward should never be exactly 0.0, got {obs.reward} on {task}"
    print("PASS test_step_reward_never_exactly_zero")


def test_step_reward_never_exactly_one():
    env = make_env()
    for task in ["easy", "medium", "hard"]:
        env.reset(task_name=task)
        obs = env.step(correct_action())
        assert obs.reward < 1.0, f"reward should never be exactly 1.0, got {obs.reward} on {task}"
    print("PASS test_step_reward_never_exactly_one")


# ── state() tests ─────────────────────────────────────────────────────────────

def test_state_after_reset():
    env = make_env()
    env.reset(task_name="hard")
    state = env.state
    assert state is not None, "state should not be None after reset"
    assert state.task_name == "hard"
    assert state.step_count == 0
    assert state.is_active == True
    assert state.patient_name != "none"
    print(f"PASS test_state_after_reset (patient={state.patient_name})")


def test_state_step_count_updates():
    env = make_env()
    env.reset(task_name="easy")
    env.step(vague_action())
    state = env.state
    assert state.step_count == 1, f"state.step_count should be 1, got {state.step_count}"
    print("PASS test_state_step_count_updates")


def test_state_has_episode_id():
    env = make_env()
    env.reset(task_name="easy")
    state = env.state
    assert state.episode_id, "episode_id should not be empty"
    assert len(state.episode_id) >= 4, "episode_id should be a real ID"
    print(f"PASS test_state_has_episode_id (id={state.episode_id})")


def test_state_episode_id_changes_on_reset():
    env = make_env()
    env.reset(task_name="easy")
    id1 = env.state.episode_id
    env.reset(task_name="easy")
    id2 = env.state.episode_id
    assert id1 != id2, "episode_id should change on each reset"
    print("PASS test_state_episode_id_changes_on_reset")


# ── run all tests ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        # reset
        test_reset_returns_observation,
        test_reset_has_required_fields,
        test_reset_medium_task,
        test_reset_hard_task,
        test_reset_randomizes_patient,
        test_reset_clears_previous_episode,
        # step
        test_step_returns_observation,
        test_step_reward_in_valid_range,
        test_step_correct_answer_scores_high,
        test_step_wrong_answer_scores_low,
        test_step_has_score_breakdown,
        test_step_has_feedback,
        test_step_increments_step_count,
        test_step_done_after_max_steps,
        test_step_reward_never_exactly_zero,
        test_step_reward_never_exactly_one,
        # state
        test_state_after_reset,
        test_state_step_count_updates,
        test_state_has_episode_id,
        test_state_episode_id_changes_on_reset,
    ]

    passed = 0
    failed = 0
    failures = []

    print(f"\nRunning {len(tests)} tests...\n")
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            failures.append((test.__name__, str(e)))
            print(f"FAIL {test.__name__}: {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    if failures:
        print("\nFailed tests:")
        for name, err in failures:
            print(f"  - {name}: {err}")
    else:
        print("All tests passed!")
    print('='*50)
