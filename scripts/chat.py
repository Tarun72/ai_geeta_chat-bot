import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chat.gita_chat import GitaChat


def print_sources(sources: list[dict]) -> None:
    if not sources:
        return

    print("\nSources:")
    for source in sources:
        score = source["score"]
        chapter = source["chapter"]
        verse = source["verse_number"]
        preview = source["preview"]
        print(f"  [{score:.2f}] Chapter {chapter}, Verse {verse} — {preview}")


def print_streaming_response(chat: GitaChat, question: str, top_k: int) -> None:
    sources, token_stream = chat.ask_stream(question, top_k=top_k)
    print("\nAnswer:")
    for token in token_stream:
        print(token, end="", flush=True)
    print()
    print_sources(sources)


def run_interactive(chat: GitaChat, top_k: int) -> None:
    print("Gita Chat (type 'exit' or 'quit' to stop)\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        print_streaming_response(chat, question, top_k=top_k)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask questions about the Bhagavad Gita using RAG"
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask (omit for interactive mode)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of verses to retrieve (default: 5)",
    )
    args = parser.parse_args()

    chat = GitaChat()

    if args.question:
        print_streaming_response(chat, args.question, top_k=args.top_k)
    else:
        run_interactive(chat, top_k=args.top_k)


if __name__ == "__main__":
    main()
