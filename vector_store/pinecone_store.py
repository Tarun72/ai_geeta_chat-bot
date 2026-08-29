from pinecone import Pinecone, ServerlessSpec

from config.env import get_env, load_env
from embeddings.openai_embedder import OpenAIEmbedder


class PineconeStore:
    DEFAULT_INDEX_NAME = "gita-verses"
    METADATA_MAX_BYTES = 40000

    def __init__(
        self,
        api_key: str | None = None,
        index_name: str | None = None,
        embedder: OpenAIEmbedder | None = None,
    ) -> None:
        load_env()
        key = api_key or get_env("PINECONE_API_KEY")
        self._index_name = index_name or get_env(
            "PINECONE_INDEX_NAME",
            required=False,
        ) or self.DEFAULT_INDEX_NAME
        self._client = Pinecone(api_key=key)
        self._embedder = embedder or OpenAIEmbedder()
        self._index = None

    def ensure_index(self) -> None:
        if not self._client.has_index(self._index_name):
            self._client.create_index(
                name=self._index_name,
                dimension=OpenAIEmbedder.DIMENSIONS,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        self._index = self._client.Index(self._index_name)

    def _get_index(self) -> object:
        if self._index is None:
            self.ensure_index()
        return self._index

    def _verse_to_metadata(self, verse: dict[str, str | int]) -> dict[str, str | int]:
        metadata: dict[str, str | int] = {
            "chapter": verse["chapter"],
            "verse_number": verse["verse_number"],
            "source": str(verse["source"]),
            "translation": str(verse["translation"]),
            "commentary": str(verse["commentary"]),
            "sanskrit": str(verse.get("sanskrit", "")),
            "transliteration": str(verse.get("transliteration", "")),
        }
        return self._truncate_metadata(metadata)

    def _truncate_metadata(
        self, metadata: dict[str, str | int]
    ) -> dict[str, str | int]:
        commentary = str(metadata["commentary"])
        encoded = commentary.encode("utf-8")
        if len(encoded) <= self.METADATA_MAX_BYTES:
            return metadata

        truncated = encoded[:self.METADATA_MAX_BYTES].decode("utf-8", errors="ignore")
        metadata["commentary"] = truncated
        return metadata

    def upsert_verses(self, verses: list[dict[str, str | int]]) -> int:
        if not verses:
            raise ValueError("Verses must be a non-empty list")

        texts = [str(verse["text"]) for verse in verses]
        vectors = self._embedder.embed_texts(texts)

        records = [
            {
                "id": str(verse["id"]),
                "values": vector,
                "metadata": self._verse_to_metadata(verse),
            }
            for verse, vector in zip(verses, vectors, strict=True)
        ]

        index = self._get_index()
        index.upsert(vectors=records, batch_size=100)
        return len(records)

    def index_chapter(self, chapter: int) -> int:
        from ingestion.pdf_loader import PdfLoader

        loader = PdfLoader()
        verses = loader.read_pdf(chapter=chapter)
        if not verses:
            raise ValueError(f"No verses found for chapter {chapter}")
        return self.upsert_verses(verses)

    def query(self, text: str, top_k: int = 5) -> list[dict]:
        if not text or not text.strip():
            raise ValueError("Query text must be a non-empty string")

        query_vector = self._embedder.embed_text(text)
        index = self._get_index()
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
        )

        return [
            {
                "id": match["id"],
                "score": match["score"],
                "metadata": match.get("metadata", {}),
            }
            for match in response["matches"]
        ]
