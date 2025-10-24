from typing import List

from langchain_core.embeddings import Embeddings

class BaseEmbedding(Embeddings):
    """Base class for DHTI embeddings."""

    base_url: str
    model: str
    api_key: str

    def __init__(self, base_url: str, model: str, api_key: str):
        self.base_url = base_url
        self.model = model
        self.api_key = api_key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        import requests
        import json

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "input": texts,
        }
        response = requests.post(
            self.base_url,
            headers=headers,
            data=json.dumps(payload),
        )
        response.raise_for_status()
        embeddings = response.json()["embeddings"]
        # embeddings is a list of lists
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        import requests
        import json

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "input": [text],
        }
        response = requests.post(
            self.base_url,
            headers=headers,
            data=json.dumps(payload),
        )
        response.raise_for_status()
        embeddings = response.json()["embeddings"]
        return embeddings[0]