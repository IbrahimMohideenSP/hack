from fastapi import FastAPI
from pydantic import BaseModel
import faiss, pickle, numpy as np
from sentence_transformers import SentenceTransformer
import openai, os

# Load API key from Render environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load FAISS index & clauses
index = faiss.read_index("vector_index.faiss")
with open("clauses.pkl", "rb") as f:
    clauses = pickle.load(f)

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI(
    title="HackRx Webhook LLM",
    description="LLM-powered clause retrieval + decision-making for insurance queries",
    version="1.0"
)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/v1/hackrx/run")
async def hackrx_webhook(req: QueryRequest):
    query = req.query

    # Step 1: Find most relevant clause
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    distances, ids = index.search(np.array(q_emb), k=1)
    best_clause = clauses[ids[0][0]]

    # Step 2: Ask OpenAI to decide
    prompt = f"""
    You are an insurance claim decision assistant.
    Query: {query}
    Relevant policy clause: {best_clause}
    Based on this, respond ONLY in valid JSON with:
    - decision: "Approved" or "Rejected"
    - amount: null or a number
    - justification: Explain briefly, referencing the clause
    """

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    decision_json = completion.choices[0].message["content"]
    return {"result": decision_json}
