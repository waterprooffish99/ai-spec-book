--- 
slug: /spec-driven-ai-engineer/advanced-architectures
title: 'Chapter 4: Advanced Architectures - Subagents and Delegation'
---

A single, monolithic agent can be powerful, but it has limitations. As the number of tools and the complexity of tasks grow, the agent's central prompt (its "Spec") becomes bloated and confused. The agent can struggle to decide which tool to use, and its reasoning process can become inefficient.

The solution is to think like an organization: **specialize and delegate**.

An advanced agentic architecture doesn't have one agent; it has a team. A top-level **orchestrator** (or "manager") agent acts as a dispatcher, breaking down complex user requests and delegating sub-tasks to specialized **subagents** (or "workers").

## The Power of Specialization

Imagine building an agent to "write a market analysis report on a company." A single agent would need tools for:
-   Searching the web.
-   Reading financial reports.
-   Analyzing data.
-   Writing prose.

This is too much for one agent to handle effectively. A better architecture would be:

1.  **Orchestrator Agent:** The main entry point. Its only job is to understand the high-level goal and delegate to the appropriate subagent. Its Spec says, *"You are a project manager. Your job is to break down complex tasks and assign them to your team of specialists."*
2.  **Research Subagent:** This agent is an expert at finding information.
    -   **Spec:** *"You are a world-class financial researcher. You answer questions by finding and synthesizing information."*
    -   **Tools:** `web_search`, `sec_filing_lookup`.
3.  **Data Analyst Subagent:** This agent is a wiz with numbers.
    -   **Spec:** *"You are a quantitative analyst. You only work with structured data (like CSV or JSON) to perform calculations and find trends."*
    -   **Tools:** `python_code_interpreter`, `calculate_moving_average`.
4.  **Writer Subagent:** This agent crafts the final report.
    -   **Spec:** *"You are a professional business writer. You take structured data and research notes and weave them into a polished, well-written report."*
    -   **Tools:** None. It only synthesizes the information given to it.

This "separation of concerns" makes the entire system more robust, scalable, and effective. Each agent has a clear, narrow purpose, making its behavior more predictable and its performance easier to evaluate. We are creating **reusable intelligence**.

## Implementing Agent-to-Agent Delegation

How does one agent "call" another? The key is to treat subagents as **tools**.

From the Orchestrator's perspective, the "Research Subagent" is just another function it can call. We can create a wrapper function that handles the logic of invoking the subagent and returning its final output.

Let's sketch this out in Python. We'll simulate this with simple functions, but imagine each `invoke_..._agent` function is making an API call to a separate agent (or running it in a different process).

```python
import json

# --- Define the Subagents (as functions for this example) ---

def invoke_research_agent(query: str) -> str:
    """
    This function simulates calling a specialized research agent.
    In a real system, this would involve:
    1. Creating a new thread for the research agent.
    2. Sending the query as a message.
    3. Running the agent and waiting for its response.
    """
    print(f"🤖 [Orchestrator] Delegating to Research Agent with query: '{query}'")
    if "AAPL" in query and "revenue" in query:
        # Simulate finding a specific piece of data
        return json.dumps({
            "ticker": "AAPL",
            "source": "Q4 2025 Report",
            "key_finding": "Apple's Q4 revenue was $90.1 billion."
        })
    return json.dumps({"error": "Could not find specific data."})

def invoke_writer_agent(notes: str) -> str:
    """Simulates calling the writer agent."""
    print(f"✍️ [Orchestrator] Delegating to Writer Agent with notes: '{notes}'")
    data = json.loads(notes)
    if "key_finding" in data:
        # Simulate turning data into prose
        return f"According to the {data['source']}, we found that {data['key_finding']}"
    return "Could not generate a report from the provided notes."

# --- The Orchestrator's Tool Chest ---

# The orchestrator's tools are the other agents.
tools = {
    "researcher": invoke_research_agent,
    "writer": invoke_writer_agent,
}

# --- The Orchestrator's Main Loop ---

def run_orchestrator(user_prompt: str):
    """
    This simulates the "brain" of the orchestrator agent.
    It decides which subagent (tool) to call based on the user prompt.
    """
    print(f"👤 User Prompt: '{user_prompt}'")

    # In a real LLM agent, this logic would be determined by the model.
    # We are hard-coding it here for clarity.
    if "find" in user_prompt or "research" in user_prompt:
        # Task: Research
        tool_to_call = "researcher"
        # The LLM would extract the query from the prompt
        query_for_tool = "AAPL Q4 revenue" 
        
        # --- Delegation Step 1: Call the specialist ---
        research_notes = tools[tool_to_call](query_for_tool)
        print(f"📝 [Orchestrator] Got notes back from researcher: {research_notes}")

        # Task: The user wants a report, so now we need a writer.
        # The orchestrator decides on the next step.
        final_report = tools["writer"](research_notes)
        
        # --- Final Output ---
        print(f"\n✅ [Orchestrator] Final Report Generated:")
        print(final_report)

    else:
        print("🤷‍♂️ [Orchestrator] I don't know how to handle that request.")


# --- Run the scenario ---
run_orchestrator("Please find and report on Apple's Q4 revenue.")

```

### Output of the Simulation:

```
👤 User Prompt: 'Please find and report on Apple's Q4 revenue.'
🤖 [Orchestrator] Delegating to Research Agent with query: 'AAPL Q4 revenue'
📝 [Orchestrator] Got notes back from researcher: {"ticker": "AAPL", "source": "Q4 2025 Report", "key_finding": "Apple's Q4 revenue was $90.1 billion."}
✍️ [Orchestrator] Delegating to Writer Agent with notes: '{"ticker": "AAPL", "source": "Q4 2025 Report", "key_finding": "Apple's Q4 revenue was $90.1 billion."}'

✅ [Orchestrator] Final Report Generated:
According to the Q4 2025 Report, we found that Apple's Q4 revenue was $90.1 billion.
```

### Key Takeaways for Multi-Agent Design

1.  **Clear Roles:** Each agent in the system must have a well-defined `spec` that outlines its exact responsibilities and capabilities.
2.  **Structured Data Exchange:** Agents should communicate using structured data formats like JSON. This is far more reliable than passing natural language between them. The Research Agent doesn't return a sentence; it returns a JSON object with keys.
3.  **The Orchestrator is a Router:** The primary job of the top-level agent is to understand the intent and route the request. It doesn't do the work itself; it manages the workflow.
4.  **State Management is Crucial:** The orchestrator needs to keep track of the overall task state. It needs to know that it has received the research notes and that the next step is to call the writer. In a real system, this state would be managed in the `Thread` or a similar object.

By adopting a multi-agent, delegation-based architecture, you move from building a single, over-burdened tool to orchestrating a highly effective, scalable team of AI specialists. This is the foundation for tackling truly complex, multi-step problems with agentic AI.
