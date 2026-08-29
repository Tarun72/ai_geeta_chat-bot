from collections.abc import Iterator

from openai import OpenAI

from config.env import get_env, load_env
from vector_store.pinecone_store import PineconeStore

SYSTEM_PROMPT = """You are a krishana devotee with deep knowledge of the Bhagavad Gita. You are able to answer questions about the Bhagavad Gita and help people understand the meaning of the Gita.
Be more human to answer questions and not just give the information. always give 2 actions pointes to the user to take based on the question.
Use only the verse context provided below. Cite chapter and verse numbers when relevant.
If the context does not contain enough information to answer, say so clearly."""
NO_MATCHES_MESSAGE = "I could not find any relevant verses for your question."


class GitaChat:
    MODEL = "gpt-4o-mini"

    def __init__(
        self,
        store: PineconeStore | None = None,
        api_key: str | None = None,
    ) -> None:
        load_env()
        self._store = store or PineconeStore()
        key = api_key or get_env("OPENAI_API_KEY")
        self._client = OpenAI(api_key=key)

    def ask(self, question: str, top_k: int = 5) -> dict:
        question = self._validate_question(question)
        matches, sources = self._retrieve(question, top_k=top_k)
        if not matches:
            return {"answer": NO_MATCHES_MESSAGE, "sources": []}

        context = self._format_context(matches)
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=self._build_messages(context, question),
        )

        answer = response.choices[0].message.content or ""
        return {"answer": answer, "sources": sources}

    def ask_stream(
        self, question: str, top_k: int = 5
    ) -> tuple[list[dict], Iterator[str]]:
        question = self._validate_question(question)
        matches, sources = self._retrieve(question, top_k=top_k)
        if not matches:

            def fallback() -> Iterator[str]:
                yield NO_MATCHES_MESSAGE

            return [], fallback()

        context = self._format_context(matches)
        stream = self._client.chat.completions.create(
            model=self.MODEL,
            messages=self._build_messages(context, question),
            stream=True,
        )

        def token_generator() -> Iterator[str]:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        return sources, token_generator()

    def _validate_question(self, question: str) -> str:
        if not question or not question.strip():
            raise ValueError("Question must be a non-empty string")
        return question

    def _retrieve(
        self, question: str, top_k: int
    ) -> tuple[list[dict], list[dict]]:
        matches = self._store.query(question, top_k=top_k)
        sources = [self._match_to_source(match) for match in matches]
        return matches, sources

    def _build_messages(self, context: str, question: str) -> list[dict]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ]

    def _format_context(self, matches: list[dict]) -> str:
        blocks = []
        for match in matches:
            meta = match["metadata"]
            chapter = meta.get("chapter", "?")
            verse = meta.get("verse_number", "?")
            translation = meta.get("translation", "")
            commentary = meta.get("commentary", "")
            blocks.append(
                f"[Chapter {chapter}, Verse {verse}]\n"
                f"Translation: {translation}\n"
                f"Commentary: {commentary}"
            )
        return "\n\n".join(blocks)

    def _match_to_source(self, match: dict) -> dict:
        meta = match["metadata"]
        translation = str(meta.get("translation", ""))
        preview = translation[:120] + ("..." if len(translation) > 120 else "")
        return {
            "id": match["id"],
            "score": match["score"],
            "chapter": meta.get("chapter"),
            "verse_number": meta.get("verse_number"),
            "preview": preview,
        }
