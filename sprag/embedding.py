import os
from abc import ABC, abstractmethod
from openai import OpenAI
import cohere
import voyageai


dimensionality = {
    "embed-english-v3.0": 1024,
    "embed-multilingual-v3.0": 1024,
    "embed-english-light-v3.0": 384,
    "embed-multilingual-light-v3.0": 384,
    "voyage-large-2": 1536,
    "voyage-law-2": 1024,
    "voyage-code-2": 1536,
}

class Embedding(ABC):
    def __init__(self, dimension=None):
        self.dimension = dimension

    @abstractmethod
    def get_embeddings(self, text, input_type=None):
        pass

class OpenAIEmbedding(Embedding):
    def __init__(self, model: str = "text-embedding-3-small", dimension: int = 768):
        """
        Only v3 models are supported.
        """
        super().__init__(dimension)
        self.model = model
        self.client = OpenAI()

    def get_embeddings(self, text, input_type=None):
        response = self.client.embeddings.create(input=text, model=self.model, dimensions=int(self.dimension))
        embeddings = [embedding_item.embedding for embedding_item in response.data]
        return embeddings[0] if isinstance(text, str) else embeddings

class CohereEmbedding(Embedding):
    def __init__(self, model: str = "embed-english-v3.0", dimension: int = None):
        super().__init__()
        self.model = model
        self.client = cohere.Client(os.environ['COHERE_API_KEY'])
        
        # Set dimension if not provided
        if dimension is None:
            try:
                self.dimension = dimensionality[model]
            except KeyError:
                raise ValueError(f"Dimension for model {model} is unknown. Please provide the dimension manually.")
        else:
            self.dimension = dimension

    def get_embeddings(self, text, input_type=None):
        if input_type == "query":
            input_type = "search_query"
        elif input_type == "document":
            input_type = "search_document"
        response = self.client.embed(texts=[text] if isinstance(text, str) else text, input_type=input_type, model=self.model)
        return response.embeddings[0] if isinstance(text, str) else response.embeddings

class VoyageAIEmbedding(Embedding):
    def __init__(self, model: str = "voyage-large-2", dimension: int = None):
        super().__init__()
        self.model = model

        # Set dimension if not provided
        if dimension is None:
            try:
                self.dimension = dimensionality[model]
            except KeyError:
                raise ValueError(f"Dimension for model {model} is unknown. Please provide the dimension manually.")
        else:
            self.dimension = dimension

    def get_embeddings(self, text, input_type=None):
        if isinstance(text, str):
            return voyageai.get_embedding(text, model=self.model, input_type=input_type)
        else:
            return voyageai.get_embeddings(text, model=self.model, input_type=input_type)