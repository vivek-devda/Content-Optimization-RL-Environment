import json
import re
from environment import ContentOptimizationEnv

def _try_action(action: str, draft: str, keywords: list[str]):
         from actions import apply_action
         try:
             return apply_action(action, draft, keywords)
         except Exception:
             return None

def run_agent(topic: str, draft: str, keywords: list[str], verbose: bool = True) -> dict:
    env = ContentOptimizationEnv()
    env.reset(topic=topic, draft=draft, keywords=keywords)

    initial_score = env.evaluate(env.draft)
    env.last_reward = initial_score
    env.prev_reward = initial_score

    log = []
    result = None  # FIX
    done_reason = None   
    last_actions = []


    if verbose:
        print(f"\n{'='*50}")
        print(f"INITIAL SCORE : {initial_score}")
        print("\n--- ORIGINAL DRAFT ---")
        print(draft)
        print(f"{'='*50}\n")

    while True:
        valid_actions = [
             a for a in env.valid_actions()
             if a not in last_actions[-2:]
    ]

        # ✅ Add repetition detection (smart trigger)
        sentences = re.split(r'(?<=[.!?])\s+', env.draft.strip())
        unique = set(s.strip().lower() for s in sentences)

        if len(unique) < len(sentences):
            if "remove_redundancy" not in valid_actions:
                valid_actions.append("remove_redundancy")

        if not valid_actions:
            break

        best_action = None
        best_reward = -float("inf")

        for action in valid_actions:
            trial_draft = _try_action(action, env.draft, env.keywords)
            if trial_draft is None:
                continue

            trial_reward = env.evaluate(trial_draft)

            if trial_reward <= env.last_reward:
                continue

            if trial_reward > best_reward:
                best_reward = trial_reward
                best_action = action

        if best_action is None:
            done_reason = "no_improvement"
            break

        result = env.step(best_action)
        last_actions.append(best_action)

        log.append({
            "step": result["state"]["step"],
            "action": best_action,
            "reward": result["reward"],
            "delta": result["delta"],
            "done_reason": result["done_reason"],
        })
        print("START")

        if verbose:
            print(f"STEP {result['state']['step']}: {best_action}")
            print(f"Reward: {result['reward']} (Δ {result['delta']:+.4f})\n")

        if result["done"]:
            done_reason = result["done_reason"]
            break
    print("END")
    return {
        "topic": topic,
        "original_draft": draft,
        "best_draft": env.best_draft,
        "best_reward": env.best_reward,
        "steps_taken": env.step_count,
        "done_reason": done_reason if done_reason else "no_steps",
        "log": log,
    }
if __name__ == "__main__":
    result = run_agent(
        topic="productivity",
        draft="basically you should just try to be very productive and actually focus and kind of manage your time. you should just try to be very productive and actually focus.",
        keywords=["productivity", "focus", "time management"],
        verbose=True,
    )

    print("\nFINAL RESULT:\n")
    print(json.dumps(result, indent=2))
