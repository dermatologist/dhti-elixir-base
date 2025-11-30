import json

import requests
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

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        return self._get_embeddings(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        embeddings = self._get_embeddings([text])
        return embeddings[0]

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Helper method to get embeddings for a list of texts."""
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
        resp_json = response.json()
        if "embeddings" not in resp_json:
            raise ValueError(f"API response missing 'embeddings' key: {resp_json}")
        embeddings = resp_json["embeddings"]
        # embeddings is a list of lists
        return embeddings
