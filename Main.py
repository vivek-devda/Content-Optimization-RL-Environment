from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from environment import ContentOptimizationEnv
from agent import run_agent

app = FastAPI(
    title="Content Optimization Environment",
    description="RL-style environment for structured content optimization.",
    version="1.0.0",
)

# Global env instance for stateful endpoints
env = ContentOptimizationEnv()


# --- Schemas ---

class ResetRequest(BaseModel):
    topic: str
    draft: str
    keywords: list[str] = []

class StepRequest(BaseModel):
    action: str

class RunAgentRequest(BaseModel):
    topic: str
    draft: str
    keywords: list[str] = []


# --- Endpoints ---

@app.get("/")
def root():
    return {"status": "ok", "message": "Content Optimization Environment is running."}

@app.post("/reset")
def reset(req: ResetRequest):
    state = env.reset(topic=req.topic, draft=req.draft, keywords=req.keywords)
    initial_score = env.evaluate(env.draft)
    env.last_reward = initial_score
    env.prev_reward = initial_score
    state["score"] = initial_score
    return {"status": "reset", "state": state}

@app.post("/step")
def step(req: StepRequest):
    if not env.draft:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    result = env.step(req.action)
    return result

@app.get("/state")
def state():
    if not env.draft:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    return {
    **env.state(),
    "best_draft": env.best_draft,
}

@app.get("/actions")
def actions():
    return {"valid_actions": env.valid_actions()}

@app.post("/run")
def run(req: RunAgentRequest):
    """Run the full agent loop and return the best draft."""
    result = run_agent(
        topic=req.topic,
        draft=req.draft,
        keywords=req.keywords,
        verbose=False,
    )
    return result