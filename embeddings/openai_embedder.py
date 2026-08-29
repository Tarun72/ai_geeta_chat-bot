from openai import OpenAI

from config.env import get_env, load_env


class OpenAIEmbedder:
    MODEL = "text-embedding-3-small"
    DIMENSIONS = 768

    def __init__(self, api_key: str | None = None) -> None:
        load_env()
        key = api_key or get_env("OPENAI_API_KEY")
        self._client = OpenAI(api_key=key)

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string (user query or one verse)."""
        if not text or not text.strip():
            raise ValueError("Text must be a non-empty string")

        response = self._client.embeddings.create(
            model=self.MODEL,
            input=text,
            dimensions=self.DIMENSIONS,
        )
        vector = response.data[0].embedding
        self._validate_vector(vector)
        return vector

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple strings (e.g. all verses)."""
        if not texts:
            raise ValueError("Texts must be a non-empty list")

        for index, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"Text at index {index} must be a non-empty string")

        response = self._client.embeddings.create(
            model=self.MODEL,
            input=texts,
            dimensions=self.DIMENSIONS,
        )
        vectors = [item.embedding for item in response.data]
        for index, vector in enumerate(vectors):
            self._validate_vector(vector, index=index)
        return vectors

    def _validate_vector(self, vector: list[float], *, index: int | None = None) -> None:
        if len(vector) != self.DIMENSIONS:
            label = f" at index {index}" if index is not None else ""
            raise ValueError(
                f"Expected embedding dimension {self.DIMENSIONS}{label}, got {len(vector)}"
            )
