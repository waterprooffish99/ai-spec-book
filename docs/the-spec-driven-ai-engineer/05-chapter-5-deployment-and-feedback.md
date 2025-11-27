---
slug: /spec-driven-ai-engineer/deployment-and-feedback
title: 'Chapter 5: Deployment & The Feedback Loop'
---

An AI agent running on your laptop is a prototype. A production-grade AI system is one that is deployed, scalable, and constantly improving. This final chapter covers the two critical, intertwined components of productionizing your agentic workflow: deploying it as a robust service and creating a feedback loop to iteratively improve its `spec`.

## Part 1: Deployment with FastAPI

Your AI agent's "brain"—the orchestrator loop that we designed—needs to live inside a web server to be accessible by other applications (like a web front-end, a Slack bot, or another microservice). **FastAPI** is an excellent choice for this, as it's a modern, high-performance Python web framework that supports `async` operations out of the box, which is perfect for long-running agent tasks.

### Structuring the FastAPI Application

Let's wrap the multi-agent orchestrator from the previous chapter in a FastAPI service.

**1. Install Libraries:**
```bash
pip install fastapi "uvicorn[standard]"
```

**2. Create the FastAPI script (`main.py`):**

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import json
import time

# --- Agentic Code (from Chapter 4, simplified) ---
# In a real project, this would be in a separate 'agents' module.

def invoke_research_agent(query: str) -> str:
    """Simulates a time-consuming research task."""
    time.sleep(3) # Simulate network/computation time
    if "AAPL" in query and "revenue" in query:
        return json.dumps({
            "ticker": "AAPL",
            "source": "Q4 2025 Report",
            "key_finding": "Apple's Q4 revenue was $90.1 billion."
        })
    return json.dumps({"error": "Could not find specific data."})

def invoke_writer_agent(notes: str) -> str:
    """Simulates the writer agent."""
    time.sleep(1)
    data = json.loads(notes)
    if "key_finding" in data:
        return f"According to the {data['source']}, we found that {data['key_finding']}"
    return "Could not generate a report from the provided notes."

def run_orchestrator_task(user_prompt: str) -> str:
    """The full, synchronous agent workflow."""
    print(f"INFO: Running orchestrator for prompt: '{user_prompt}'")
    research_notes = invoke_research_agent("AAPL Q4 revenue")
    final_report = invoke_writer_agent(research_notes)
    print(f"INFO: Orchestrator finished. Report: '{final_report}'")
    return final_report

# --- FastAPI Application ---

app = FastAPI()

# Pydantic models for request and response validation
class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    status: str
    report: str | None = None

# In-memory "database" to store results of async tasks
task_results = {}

def background_agent_runner(task_id: str, prompt: str):
    """A wrapper to run our agent and store the result."""
    report = run_orchestrator_task(prompt)
    task_results[task_id] = {"status": "completed", "report": report}


@app.post("/generate-report", response_model=AgentResponse)
async def generate_report(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Asynchronous endpoint to trigger the agent workflow.
    It starts the agent in the background and immediately returns a task ID.
    """
    task_id = f"task_{int(time.time())}"
    task_results[task_id] = {"status": "in_progress", "report": None}
    
    # Run the time-consuming agent logic in the background
    background_tasks.add_task(background_agent_runner, task_id, request.prompt)
    
    return {"status": f"Task {task_id} started. Check status endpoint for results."}

@app.get("/report-status/{task_id}", response_model=AgentResponse)
async def get_report_status(task_id: str):
    """Endpoint to check the status and get the result of a task."""
    result = task_results.get(task_id, {"status": "not_found"})
    return result

```

**3. Run the server:**
```bash
uvicorn main:app --reload
```

Now you have a running API server on `http://127.0.0.1:8000`. You can interact with it using a tool like `curl` or a Python script:
1.  **POST** to `/generate-report` to start the task.
2.  **GET** from `/report-status/{task_id}` to check on it and get the final report.

This async, task-based pattern is essential for agentic systems, where a single "request" might take 30 seconds or more to complete.

## Part 2: The Feedback Loop

Deployment is just the beginning. An agent's performance will drift, users will find edge cases, and new data will become available. A system for **collecting, analyzing, and acting on feedback** is the engine of iterative improvement in Spec-Driven Development.

### Types of Feedback

1.  **Explicit Feedback:** Ask users directly. After displaying a result, show a simple "👍 / 👎" button. If they click "👎", open a small text box asking "What was wrong with this response?"
2.  **Implicit Feedback:** Track user behavior. If a user immediately re-phrases their query and tries again after getting a response, it's a strong signal the first response was poor.
3.  **Evaluation-driven Feedback:** Periodically run your "Golden Set" (from Chapter 1) of evaluation examples against the deployed agent. If a prompt that used to work now fails, that's a regression that needs to be fixed.

### Closing the Loop

All this collected feedback is gold. It is the input for the next iteration of your development cycle.

1.  **Collect:** Store all feedback in a database. A simple schema might be: `(timestamp, user_prompt, agent_response, feedback_score, feedback_text)`.
2.  **Analyze:** Look for patterns in the feedback.
    -   Are users consistently disliking answers about a specific topic? *Maybe your RAG knowledge base is missing documents on that topic.*
    -   Is the agent failing to use the right tool for a certain kind of question? *Maybe the tool's description in the agent's spec needs to be clearer.*
    -   Is the agent's tone wrong? *Maybe the persona definition in the spec needs to be adjusted.*
3.  **Refine the Spec:** This is the core of SDD. You use the analysis to update your specification document.
    -   **Old Spec:** `"Tool: get_stock_price(ticker: str)"`
    -   **Feedback:** *"Agent fails to get prices for international stocks."*
    -   **New Spec:** `"Tool: get_stock_price(ticker: str, market: str = 'US')"` -> This leads to a change in the tool's implementation.
4.  **Redeploy:** Deploy the updated agent and measure the impact of your changes on the feedback metrics.

This cycle of **Deploy -> Collect -> Analyze -> Refine -> Redeploy** turns a static prototype into a living, learning system that gets progressively more aligned with its purpose.

## Deploying the Book to GitHub Pages

Finally, to share your knowledge, you can easily deploy this Docusaurus site.

1.  **Set `url` and `baseUrl` in `docusaurus.config.ts`:**
    ```typescript
    // docusaurus.config.ts
    const config = {
      // ...
      url: 'https://<YOUR_GITHUB_USERNAME>.github.io',
      baseUrl: '/<YOUR_REPOSITORY_NAME>/',
      // ...
    };
    ```

2.  **Add a deployment script to `package.json`:**
    ```json
    // package.json
    "scripts": {
      "deploy": "docusaurus deploy"
    },
    ```
    
3. **Push your code to a new GitHub repository.**

4.  **Run the deploy command:**
    ```bash
    GIT_USER=<YOUR_GITHUB_USERNAME> npm run deploy
    ```
    This command will build your site and push the static files to the `gh-pages` branch of your repository, making it live.

By mastering deployment and feedback, you complete the journey from a conceptual idea to a robust, continuously improving AI-powered product.
