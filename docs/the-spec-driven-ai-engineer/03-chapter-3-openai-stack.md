---
slug: /spec-driven-ai-engineer/openai-stack
title: 'Chapter 3: The OpenAI Agentic Stack'
---

The release of GPT-4 marked a turning point, but the true revolution in AI development is the ecosystem being built around the models. The paradigm is shifting from simple, one-shot "prompt-and-response" to persistent, tool-using **agents**. OpenAI provides a powerful, if sometimes opaque, stack for building these agents.

This chapter will focus on the conceptual framework of the **Assistants API** and how to interact with it. While the hosted OpenAI platform is excellent for rapid prototyping, understanding these principles is key to building custom, open-source agentic systems later.

## From Completions to Assistants

The original way to interact with an LLM was through the **Completions API**. You sent a prompt, and the model returned a completion. This is a stateless, one-time transaction.

The **Assistants API** introduces the concept of state and capabilities. An `Assistant` is a more persistent entity that you configure with:
-   **Instructions:** A detailed prompt defining its persona and objective (the "Spec").
-   **Model:** The underlying LLM to use (e.g., `gpt-4-turbo-preview`).
-   **Tools:** A list of functions the Assistant can decide to call to get external information or perform actions.
-   **Knowledge:** A set of files that OpenAI will automatically manage in a RAG system for you.

### The Core Objects

Interacting with the Assistants API involves a few key objects:

1.  **Assistant:** The configuration of your agent. You create this once.
2.  **Thread:** A conversation session. A thread contains all the messages in a conversation. You create one thread per user or per conversation.
3.  **Message:** A single turn in the conversation, from either the `user` or the `assistant`.
4.  **Run:** An execution of the Assistant on a Thread. When you add a new user message, you create a `Run`. The Assistant then takes over, reading the thread, deciding whether to call tools or generate a response, and adding its own message to the thread.

This stateful, asynchronous model is what makes it "agentic." The Assistant can decide on a multi-step reasoning process, call multiple tools, and even correct itself within a single `Run`.

## Building a Simple RAG Agent with Assistants API

Let's build an agent that can answer questions about the documents we indexed in the previous chapter. For this example, instead of using our own Qdrant instance, we'll upload a file directly to OpenAI and let it handle the RAG implementation.

**1. Install Libraries:**
```bash
pip install openai
```

**2. Set up your environment:**
Make sure you have your OpenAI API key set as an environment variable.
```bash
export OPENAI_API_KEY='sk-...'
```

**3. Create a knowledge file (`knowledge.txt`):**
```text
The first AI agent was named Shakey and was developed at Stanford in 1966.
Spec-Driven Development provides a framework for building reliable agentic systems.
Qdrant is a high-performance vector database built in Rust.
Unlike Shakey, modern AI agents leverage the power of large language models.
```

**4. Create the Python script (`assistant_example.py`):**

```python
import time
import os
from openai import OpenAI

# Initialize the client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- 1. Create Knowledge File and Assistant ---

# Upload our knowledge file to OpenAI
file = client.files.create(
  file=open("knowledge.txt", "rb"),
  purpose='assistants'
)
print(f"📄 Uploaded knowledge file: {file.id}")

# Create the Assistant
# We enable the "Retrieval" tool (OpenAI's managed RAG)
# And we associate our uploaded file with it.
assistant = client.beta.assistants.create(
  name="Spec-Driven AI Expert",
  instructions="You are an expert on AI development. Use your knowledge base to answer questions about agentic systems and AI history.",
  model="gpt-4-turbo-preview",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)
print(f"🤖 Created Assistant: {assistant.id}")


# --- 2. Create a Thread and Run the Conversation ---

# Create a conversation thread
thread = client.beta.threads.create()
print(f"🧵 Created Thread: {thread.id}")

# Add the user's first message to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the difference between early AI agents and modern ones?"
)

# Create a "Run" to process the thread
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
)
print(f"🏃‍♂️ Created Run: {run.id}")


# --- 3. Wait for Completion and Display the Result ---

# The Run is asynchronous. We need to poll until it's done.
while run.status in ['queued', 'in_progress', 'cancelling']:
  time.sleep(1)
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )
  print(f"  - Run status: {run.status}")


if run.status == 'completed': 
  # List the messages in the thread
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )

  # Find the assistant's response
  # Messages are returned in descending order
  assistant_message = next(m for m in messages.data if m.role == 'assistant')
  
  print("\n✅ Assistant Response:")
  # The content is an array, get the first text element
  response_text = assistant_message.content[0].text.value
  print(response_text)

  # OpenAI's Retrieval tool often adds citations
  annotations = assistant_message.content[0].text.annotations
  if annotations:
    print("\n📚 Citations:")
    print(annotations[0].file_citation)

else:
  print(f"\n❌ Run failed with status: {run.status}")
  print(run.last_error)

```

**5. Run the script:**
```bash
python assistant_example.py
```

### What's Happening Under the Hood?

When you create the `Run`, the Assistant executes its core loop:
1.  **Analyze:** It reads the entire thread history.
2.  **Decide:** It sees the user's question. Because it has the `retrieval` tool enabled, it decides it needs to search its knowledge base.
3.  **Act:** It formulates a search query (e.g., "early AI agents vs modern AI agents") and runs it against the `knowledge.txt` file you provided.
4.  **Observe:** It gets the search results, which include the lines about "Shakey" and "modern AI agents leverage LLMs."
5.  **Generate:** It synthesizes these retrieved facts into a coherent, natural language response, citing the source.
6.  **Respond:** It adds this new message to the thread.

This loop of `Analyze -> Decide -> Act -> Observe -> Generate` is the fundamental pattern of all agentic systems. While the Assistants API abstracts much of this away, mastering this pattern is essential for building advanced, custom architectures, as we'll see in the next chapter. The hosted solution is a great starting point, but true power comes from controlling this loop yourself.
