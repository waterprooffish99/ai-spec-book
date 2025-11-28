import os
import traceback # Used for printing detailed error logs
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Use synchronous QdrantClient
from qdrant_client import QdrantClient, models 
from openai import OpenAI
import uvicorn
# Import threadpool utility to safely run synchronous Qdrant code
from starlette.concurrency import run_in_threadpool 

# Load environment variables from .env file
load_dotenv()

# Pydantic models for request and response
class QueryRequest(BaseModel):
    query: str

class AnswerResponse(BaseModel):
    answer: str

class SelectiveQueryRequest(BaseModel):
    query: str
    context: str

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load secrets from environment variables
try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
    qdrant_url = os.environ["QDRANT_URL"]
    qdrant_api_key = os.environ["QDRANT_API_KEY"]
except KeyError as e:
    raise RuntimeError(f"Environment variable {e} not set. Check your .env file.") from e

# Initialize the synchronous QdrantClient 
qdrant_client = QdrantClient( 
    url=qdrant_url,
    api_key=qdrant_api_key,
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# RAG Configuration
QDRANT_COLLECTION_NAME = "ai-spec-book-collection"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-3.5-turbo"

@app.post("/chat", response_model=AnswerResponse)
async def rag_chat(request: QueryRequest):
    """
    Endpoint for general RAG chat. Embeds query, searches Qdrant, and generates an answer.
    """
    try:
        # 1. Embed the user's question
        embedding_response = openai_client.embeddings.create(
            input=request.query, 
            model=EMBEDDING_MODEL,
        )
        query_vector = embedding_response.data[0].embedding

        # 2. Search Qdrant using query_points (Robust Fix)
        # We use run_in_threadpool to make this non-blocking
        search_response = await run_in_threadpool(
            qdrant_client.query_points,
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=4,
            with_payload=True,
        )
        
        # Extract points from the response object
        search_results = search_response.points

        # Extract the text from the search results
        context_chunks = [result.payload.get("text") for result in search_results if result.payload]
        
        if not context_chunks:
            return AnswerResponse(answer="I can only answer questions using the contents of The Spec-Driven AI Engineer book.")

        combined_context = "\n\n---\n\n".join(context_chunks)

        # 3. Construct the system prompt (Grounding the LLM)
        system_prompt = (
            "Answer the user's question based ONLY on the provided context. "
            "If the context does not contain the answer, politely state, "
            "'I can only answer questions using the contents of The Spec-Driven AI Engineer book.'"
        )

        # 4. Send to the LLM for generation
        chat_completion = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {request.query}"},
            ],
            model=LLM_MODEL,
        )

        final_answer = chat_completion.choices[0].message.content
        return AnswerResponse(answer=final_answer)

    except Exception as e:
        # Log the detailed traceback for debugging
        print("\n--- FATAL RAG CHAT ERROR ---")
        traceback.print_exc()
        print("----------------------------\n")
        raise HTTPException(status_code=500, detail="Failed to process chat request.")


@app.post("/chat/selective", response_model=AnswerResponse)
async def selective_context_chat(request: SelectiveQueryRequest):
    """
    Endpoint for the advanced feature: answering based only on user-selected context.
    """
    try:
        # 1. Construct the special system prompt
        system_prompt = (
            f"Answer the user's question based ONLY on this SPECIFIC selected text: '{request.context}'. "
            "Do not use any other knowledge. If the answer is not in this exact text, state, "
            "'I cannot find the answer within the selected text portion.'"
        )
        
        # 2. Send the context and question to the LLM
        chat_completion = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query},
            ],
            model=LLM_MODEL,
        )

        final_answer = chat_completion.choices[0].message.content
        return AnswerResponse(answer=final_answer)

    except Exception as e:
        print(f"An error occurred in selective chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process selective chat request.")

# To run the app, use the command: uvicorn api_server:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)