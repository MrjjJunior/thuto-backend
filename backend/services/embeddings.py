import os
import requests

OPENROUTER_API_KEY = os.getenv("")

def get_embedding(text):
    repsonse = request.post(
        "https://openrouter.ai/api/v1/embeddings",
        header={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        json={
            "model": "text-embedding-3-small",
            "input": text,
        },
    )
    return response.json()["data"][0]["embedding"]
