# app/core/pinecone_client.py

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from uuid import uuid4
import hashlib
import json
import hashlib
from uuid import uuid4

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Create Pinecone client instance
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=1536,  # Adjust if embedding size changes
        metric='euclidean',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

index = pc.Index(PINECONE_INDEX)

def upsert_vector(id: str, vector: list, metadata: dict = None):
    meta = metadata or {}
    index.upsert([(id, vector, meta)])

def query_pinecone(query_vector=None, top_k=5):
    if not query_vector:
        return [
            {"student": "Alice", "score": 90, "topic": "Algebra"},
            {"student": "Bob", "score": 85, "topic": "Photosynthesis"},
        ]
    results = index.query(query_vector, top_k=top_k, include_metadata=True)
    return results.matches

def save_quiz_result(student_email: str, topic: str, difficulty: str, score: int, results: list):
    quiz_id = hashlib.sha256(f"{student_email}:{topic}:{uuid4()}".encode()).hexdigest()

    metadata = {
        "student_email": student_email,
        "topic": topic,
        "difficulty": difficulty,
        "score": score,
        "results_json": json.dumps(results),
        "type": "quiz_result"
    }

    #dummy_vector = [0.0] * 1024
    dummy_vector = [0.1] + [0.0] * 1023  # 1024-dim with a non-zero first value

    from app.core.pinecone_client import index  # ensure `index` is available
    index.upsert([(quiz_id, dummy_vector, metadata)])
    return quiz_id
def fetch_all_quiz_results():
    return [
        {
            "student_email": "student1@example.com",
            "topic": "Probability",
            "score": 80,
            "timestamp": "2025-06-26 22:45"
        },
        {
            "student_email": "student2@example.com",
            "topic": "Algebra",
            "score": 60,
            "timestamp": "2025-06-26 22:50"
        }
    ]
