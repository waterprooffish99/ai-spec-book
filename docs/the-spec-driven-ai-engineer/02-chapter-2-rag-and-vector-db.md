---
slug: /spec-driven-ai-engineer/rag-and-vector-db
title: 'Chapter 2: Building Blocks - RAG and Vector Databases'
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

## The Knowledge Problem

Large Language Models (LLMs) are trained on vast, but static, snapshots of the internet. This leads to two fundamental problems:
1.  **The Knowledge Cutoff:** The model has no information about events, data, or documentation created after its training date.
2.  **The Hallucination Problem:** When asked about topics outside its training data (or even on its fringes), an LLM will often "hallucinate"—generating plausible but factually incorrect information.
3.  **The Privacy Problem:** You cannot use an LLM to answer questions about your private, proprietary data (e.g., internal company documents, user data) because the model has never seen it.

The solution to all three is **Retrieval-Augmented Generation (RAG)**.

## What is RAG?

RAG is a design pattern that gives an LLM access to external, real-time information. Instead of relying solely on its internal, trained knowledge, the agent first **retrieves** relevant data from an outside source and then uses that data to **augment** its prompt when **generating** a response.

The flow is simple but powerful:
1.  **User Query:** The user asks a question, e.g., "What were our Q3 sales figures?"
2.  **Retrieval:** The system doesn't immediately ask the LLM. First, it searches an external knowledge base (like a database of company sales reports) for documents relevant to "Q3 sales figures."
3.  **Augmentation:** The system takes the most relevant documents it found and prepends them to the user's query as context.
4.  **Generation:** The system sends this augmented prompt to the LLM. The final prompt looks something like this:

    ```
    Context:
    "Document 7: Q3 Sales Report. Total revenue was $4.2M, with a 12% increase in the enterprise sector..."
    "Document 12: Q3 Regional Breakdown. North America contributed $2.8M..."

    ---

    Based on the context provided, answer the following question: What were our Q3 sales figures?
    ```
5.  **Response:** The LLM, now equipped with the necessary facts, can generate a correct and fact-based answer.

## Vector Databases: The Engine of RAG

The magic of the "Retrieval" step lies in **vector databases**. To find "relevant" documents, we need to search by semantic meaning, not just keywords.

### How it Works: Embeddings

1.  **Indexing:** When you add a document to your knowledge base, you first use a special kind of model (an "embedding model") to convert the text into a high-dimensional vector—an array of numbers like `[0.02, -0.5, 0.9, ...]`.
    This vector represents the document's semantic meaning. Documents with similar meanings will have vectors that are "close" to each other in vector space.
2.  **Querying:** When a user asks a question, you convert the *query itself* into a vector using the same embedding model.
3.  **Similarity Search:** You then ask the vector database to find the document vectors that are closest to your query vector. The most common way to measure "closeness" is **Cosine Similarity**.

This process allows us to find documents that are about "quarterly earnings" even if the user asks about "how much money we made."

### Introducing Qdrant

While there are many vector databases, **Qdrant** is a powerful, open-source, and production-ready option. It's built in Rust for performance and offers a rich set of features.

**Core Qdrant Concepts:**
- **Collection:** A named set of points, analogous to a table in a SQL database. You would typically have one collection per type of document (e.g., `internal_docs`, `support_tickets`).
- **Point:** The fundamental unit in Qdrant. Each point has:
    - A unique **ID**.
    - A **Vector** (the embedding).
    - An optional **Payload** (a JSON object containing the original text content or other metadata, like `source: "doc_123.pdf"`).

### Practical Example: Setting up and Using Qdrant

Let's build a simple RAG system.

**1. Install Libraries:**
```bash
pip install qdrant-client sentence-transformers
```

**2. Run Qdrant with Docker:**
The easiest way to get started is with Docker.
```bash
docker run -p 6333:6333 qdrant/qdrant
```
This will start a Qdrant instance on `localhost:6333`.

**3. Create a Python script (`rag_example.py`):**

<Tabs>
<TabItem value="python" label="rag_example.py" default>

```python
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
# This model will run locally on your machine
encoder = SentenceTransformer('all-MiniLM-L6-v2') 

# Initialize the Qdrant client
qdrant = QdrantClient("localhost", port=6333)

# --- 1. Indexing Phase ---

# Create a new collection in Qdrant
# We tell it the size of the vectors we'll be using (384 for 'all-MiniLM-L6-v2')
# And the distance metric to use (Cosine similarity)
qdrant.recreate_collection(
    collection_name="my_documents",
    vectors_config=models.VectorParams(size=encoder.get_sentence_embedding_dimension(), distance=models.Distance.COSINE)
)

# Let's create some documents to index
documents = [
    {"id": 1, "text": "The first AI agent was named Shakey and was developed at Stanford in 1966.", "source": "history_of_ai.pdf"},
    {"id": 2, "text": "Spec-Driven Development provides a framework for building reliable agentic systems.", "source": "sdd_whitepaper.doc"},
    {"id": 3, "text": "Qdrant is a high-performance vector database built in Rust.", "source": "qdrant_docs.html"},
    {"id": 4, "text": "Unlike Shakey, modern AI agents leverage the power of large language models.", "source": "modern_robotics.pdf"},
]

# Add the documents to our collection
qdrant.upload_records(
    collection_name="my_documents",
    records=[
        models.Record(
            id=doc["id"],
            vector=encoder.encode(doc["text"]).tolist(),
            payload={"text": doc["text"], "source": doc["source"]}
        ) for doc in documents
    ]
)

print("✅ Documents indexed.")


# --- 2. Retrieval Phase ---

user_query = "What are modern AI agents?"

# Convert the query to a vector
query_vector = encoder.encode(user_query).tolist()

# Perform the similarity search in Qdrant
hits = qdrant.search(
    collection_name="my_documents",
    query_vector=query_vector,
    limit=2 # Find the top 2 most similar documents
)

print("\n🔍 Found relevant documents:")
for hit in hits:
    print(f"  - Source: {hit.payload['source']}, Score: {hit.score:.4f}")
    print(f"    Text: {hit.payload['text']}")

# In a real application, you would now take the text from these hits,
# format it into a prompt, and send it to an LLM.
```
</TabItem>
</Tabs>

**4. Run the script:**
```bash
python rag_example.py
```

**Expected Output:**
```
✅ Documents indexed.

🔍 Found relevant documents:
  - Source: modern_robotics.pdf, Score: 0.8123
    Text: Unlike Shakey, modern AI agents leverage the power of large language models.
  - Source: sdd_whitepaper.doc, Score: 0.6543
    Text: Spec-Driven Development provides a framework for building reliable agentic systems.
```

As you can see, the system correctly identified the most relevant document about "modern AI agents" and also found a tangentially related document about agentic systems. This retrieved context is the raw material you would feed to your LLM to ensure a grounded, factual answer, forming the backbone of any serious agentic workflow.
