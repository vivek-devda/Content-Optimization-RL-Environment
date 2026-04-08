from actions import apply_action
from reward import compute_reward


class ContentOptimizationEnv:
    def __init__(self):
        self.draft = ""
        self.topic = ""
        self.keywords = []
        self.step_count = 0
        self.max_steps = 5
        self.history = []
        self.last_reward = 0.0
        self.prev_reward = 0.0
        self.best_reward = 0.0
        self.best_draft = ""
        self.penalty_counter = 0

    def reset(self, topic: str, draft: str, keywords: list[str]) -> dict:
        """Reset the environment with a new task."""
        self.draft = draft
        self.topic = topic
        self.keywords = keywords.copy()  # prevent external mutation
        self.step_count = 0
        self.history = []
        self.last_reward = 0.0
        self.best_reward = self.evaluate(draft)
        self.best_draft = draft
        self.penalty_counter = 0
        self.prev_reward = self.evaluate(draft)  # seed with real initial quality

        return self.state()

    def evaluate(self, draft: str) -> float:
        """Centralized reward computation."""
        return compute_reward(draft, self.keywords)

    def step(self, action: str) -> dict:
        """Apply an action and return the new state + reward + done flag."""
        if action not in self.valid_actions():
            return {
                "error": f"Invalid action '{action}'. Valid actions: {self.valid_actions()}",
                "state": self.state(),
                "reward": -1.0,
                "delta": -1.0,
                "done": False,
                "done_reason": None,
            }

        previous_draft = self.draft  # snapshot before applying action

        try:
            new_draft = apply_action(action, self.draft, self.keywords)
        except Exception as e:
            self.draft = previous_draft  # rollback on failure
            return {
                "error": f"Action '{action}' failed: {str(e)}",
                "state": self.state(),
                "reward": -1.0,
                "delta": -1.0,
                "done": False,
                "done_reason": None,
            }

        # Centralized reward computation
        reward = self.evaluate(new_draft)
        delta = reward - self.prev_reward

        # Track best draft
        if reward > self.best_reward:
            self.best_reward = reward
            self.best_draft = new_draft

        # Early failure detection
        if delta < 0:
            self.penalty_counter += 1
        else:
            self.penalty_counter = 0

        # Log step
        self.history.append({
            "step": self.step_count,
            "action": action,
            "reward": reward,
            "delta": delta,
            "draft_snapshot": new_draft[:100]
        })

        # Update state
        self.draft = new_draft
        self.prev_reward = reward
        self.last_reward = reward
        self.step_count += 1

        # Done conditions
        done = (
            reward > 0.9
            or self.step_count >= self.max_steps
            or self.penalty_counter >= 2
        )

        # Done reason
        reason = None
        if reward > 0.9:
            reason = "goal_reached"
        elif self.step_count >= self.max_steps:
            reason = "max_steps"
        elif self.penalty_counter >= 2:
            reason = "early_failure"

        return {
            "state": self.state(),
            "reward": reward,
            "delta": delta,
            "done": done,
            "done_reason": reason,
            "action_applied": action,
            "best_draft": self.best_draft,
            "best_reward": self.best_reward,
        }

    def state(self) -> dict:
        """Return the current observation."""
        return {
            "topic": self.topic,
            "draft": self.draft,
            "keywords": self.keywords,
            "step": self.step_count,
            "max_steps": self.max_steps,
            "score": self.last_reward,
            "best_reward": self.best_reward,
            "penalty_counter": self.penalty_counter,
        }

    def valid_actions(self) -> list[str]:
        score = self.last_reward
        actions = ["improve_clarity", "improve_hook"]
        if score < 0.6:
            actions.append("refine_structure")
        if score < 0.7:
            actions.append("add_keywords")
        # Always allow redundancy removal if repetition exists
        sentences = self.draft.split('.')

        if len(sentences) != len(set(s.strip().lower() for s in sentences)):
            actions.append("remove_redundancy")
        elif score > 0.6 and len(self.draft) > 50:
            actions.append("remove_redundancy")

        return actions  # ← always returns