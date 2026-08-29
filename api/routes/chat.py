import json
from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas import ChatRequest
from chat.gita_chat import GitaChat

router = APIRouter()
_chat: GitaChat | None = None


def get_chat() -> GitaChat:
    global _chat
    if _chat is None:
        _chat = GitaChat()
    return _chat


def _format_sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


def _stream_response(question: str, top_k: int) -> Iterator[str]:
    chat = get_chat()
    try:
        sources, token_stream = chat.ask_stream(question, top_k=top_k)
        yield _format_sse("sources", json.dumps(sources))

        for token in token_stream:
            yield _format_sse("token", json.dumps(token))

        yield _format_sse("done", "")
    except ValueError as exc:
        yield _format_sse("error", json.dumps(str(exc)))
    except Exception as exc:
        yield _format_sse("error", json.dumps(f"An unexpected error occurred: {exc}"))


@router.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _stream_response(request.question.strip(), request.top_k),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
