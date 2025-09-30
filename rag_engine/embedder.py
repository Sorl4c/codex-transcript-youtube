"""
Module for generating text embeddings using different backends.

Follows a Strategy design pattern with a factory for easy extension.
"""

import requests
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
from typing import List

from .config import (
    EMBEDDER_TYPE,
    LOCAL_EMBEDDER_MODEL,
    API_EMBEDDER_URL,
    API_EMBEDDER_MODEL
)

class Embedder(ABC):
    """Abstract base class for all embedder implementations."""

    @abstractmethod
    def embed(self, chunks: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text chunks.

        Args:
            chunks (List[str]): A list of text chunks to embed.

        Returns:
            List[List[float]]: A list of embeddings, where each embedding is a list of floats.
        """
        pass


class LocalEmbedder(Embedder):
    """Embedder that uses a local sentence-transformer model."""

    def __init__(self, model_name: str = LOCAL_EMBEDDER_MODEL):
        """
        Initializes the LocalEmbedder.

        Args:
            model_name (str): The name of the sentence-transformer model to use.
        """
        # Force CPU to avoid CUDA compatibility issues
        self.model = SentenceTransformer(model_name, device='cpu')

    def embed(self, chunks: List[str]) -> List[List[float]]:
        """Generates embeddings locally."""
        print(f"Generating {len(chunks)} embeddings locally using '{LOCAL_EMBEDDER_MODEL}'...")
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        # Convert numpy arrays to lists of floats
        return [embedding.tolist() for embedding in embeddings]


class APIEmbedder(Embedder):
    """Embedder that uses an OpenAI-compatible API endpoint."""

    def __init__(self, api_url: str = API_EMBEDDER_URL, model_name: str = API_EMBEDDER_MODEL):
        """
        Initializes the APIEmbedder.

        Args:
            api_url (str): The URL of the embeddings API endpoint.
            model_name (str): The name of the model to use via the API.
        """
        self.api_url = api_url
        self.model_name = model_name

    def embed(self, chunks: List[str]) -> List[List[float]]:
        """Generates embeddings by calling an external API."""
        print(f"Generating {len(chunks)} embeddings via API using '{self.model_name}' at {self.api_url}...")
        try:
            response = requests.post(
                self.api_url,
                json={"input": chunks, "model": self.model_name},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            
            # Sort embeddings to match the original order of chunks
            embeddings = sorted(data['data'], key=lambda e: e['index'])
            
            return [embedding['embedding'] for embedding in embeddings]
        except requests.exceptions.RequestException as e:
            print(f"Error calling embedding API: {e}")
            raise


class EmbedderFactory:
    """Factory to create an embedder instance based on configuration."""

    @staticmethod
    def create_embedder(embedder_type: str = EMBEDDER_TYPE) -> Embedder:
        """
        Creates and returns an embedder instance.

        Args:
            embedder_type (str): The type of embedder to create ('local' or 'api').

        Returns:
            Embedder: An instance of the requested embedder.

        Raises:
            ValueError: If an unsupported embedder type is provided.
        """
        if embedder_type == 'local':
            return LocalEmbedder()
        elif embedder_type == 'api':
            return APIEmbedder()
        else:
            raise ValueError(f"Unsupported embedder type: {embedder_type}")
