# Bhagavad Gita RAG Chatbot

**Ask Krishna's Wisdom** — answers grounded in *Bhagavad-gita As It Is*, with chapter and verse citations.

<video src="docs/assets/demo.mov" controls autoplay muted loop playsinline width="100%">
  Bhagavad Gita RAG Chatbot demo
</video>

---

## About

An AI-powered chatbot that lets you ask philosophical questions about the Bhagavad Gita in natural language and receive thoughtful, grounded answers. Instead of searching through 700 verses manually, you ask a question like *"What is karma? If everything is already written in destiny"* and get a synthesized response backed by the most relevant verses.

The interface walks through three states:

1. **Landing** — A clean chat window with example prompts such as *"What is karma yoga?"* or *"How should one act without attachment?"*
2. **Streaming answer** — A *Krishna's Wisdom* card with a multi-paragraph explanation, chapter/verse references woven into the text, and actionable advice to apply the teaching.
3. **Source attribution** — A *SOURCES* section listing the retrieved verses with chapter and verse numbers, relevance scores, and text previews so every claim is traceable.

---

## Challenges It Resolves

| Challenge | How it's solved |
|-----------|-----------------|
| **LLM hallucination** | Answers are restricted to retrieved verse context; the system prompt requires citing chapter and verse numbers |
| **Hard to search 700 verses** | Semantic vector search over translation and commentary via Pinecone |
| **Trust and transparency** | Source cards show chapter, verse, relevance score, and a text preview for every answer |
| **Complex philosophy made accessible** | Conversational UI with actionable advice — two action points per answer |
| **Real-time UX** | Server-Sent Events (SSE) streaming from FastAPI to React for token-by-token responses |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.12+ |
| **LLM** | OpenAI `gpt-4o-mini` |
| **Embeddings** | OpenAI `text-embedding-3-small` (768 dimensions) |
| **Vector DB** | Pinecone (serverless, cosine similarity) |
| **PDF parsing** | `pypdf` + custom regex parser |
| **API** | FastAPI + Uvicorn (SSE streaming) |
| **Frontend** | React 19, TypeScript, Vite 6 |
| **Package management** | `uv` (Python), npm (frontend) |

No LangChain — the RAG pipeline is implemented end to end with the OpenAI SDK and Pinecone client directly.

---

## Getting Started

See [docs/SETUP.md](docs/SETUP.md) for prerequisites, environment setup, one-time indexing, and how to run the backend and frontend locally.

---

## Architecture

The system has two independent pipelines that share only the Pinecone index — ingestion runs once offline via CLI, while the chat app queries the pre-built index at runtime.

### System Overview

```mermaid
flowchart TB
    subgraph ingestion ["One-time ingestion (offline CLI)"]
        PDF["Bhagavad-gita PDF"] --> Parser["pdf_loader + gita_parser"]
        Parser --> Embed["OpenAI Embeddings"]
        Embed --> Pinecone[("Pinecone Index")]
    end

    subgraph runtime ["Runtime user flow (on every question)"]
        User["User"] --> UI["React Frontend"]
        UI --> API["FastAPI /api/chat"]
        API --> RAG["GitaChat RAG"]
        RAG --> Pinecone
        RAG --> LLM["GPT-4o-mini"]
        LLM --> SSE["SSE stream"]
        SSE --> UI
    end
```

### Offline Ingestion Pipeline

Run once before deploying the chat app — completely separate from user requests.

```mermaid
flowchart TB
    CLI["Step 1 — Run indexing CLI\nuv run python scripts/index_all.py"]
    Parse["Step 2 — Parse PDF into verses\nGitaIndexer → PdfLoader → gita_parser"]
    Embed["Step 3 — Embed verse text\nOpenAI text-embedding-3-small"]
    Store["Step 4 — Upsert vectors\nPinecone index: gita-verses"]

    CLI --> Parse --> Embed --> Store
```

- **Trigger:** Run once before deploying the chat app — completely separate from user requests.
- **Input:** `data/Bhagavad-gita-As-It-Is.pdf` (local, gitignored).
- **Output:** ~700 verse vectors stored in Pinecone with translation, commentary, and chapter/verse metadata.
- **After indexing:** The index persists in Pinecone; the FastAPI app only reads from it — no PDF or ingestion code runs at request time.

### User Flow

Every question triggers the runtime pipeline below. The frontend receives three SSE event types from `POST /api/chat`: `sources` (retrieved verses), `token` (streamed answer text), and `done`.

```mermaid
sequenceDiagram
    participant User
    participant React as React Frontend
    participant API as FastAPI
    participant Chat as GitaChat
    participant Pinecone
    participant OpenAI

    User->>React: Type question and submit
    React->>API: POST /api/chat (SSE)
    API->>Chat: ask_stream(question, top_k)
    Chat->>Pinecone: Embed query + similarity search
    Pinecone-->>Chat: Top-K verse matches
    Chat-->>API: sources metadata
    API-->>React: SSE event sources
    React-->>User: Show source citation cards
    Chat->>OpenAI: Stream completion with verse context
    loop Each token
        OpenAI-->>Chat: token
        Chat-->>API: token
        API-->>React: SSE event token
        React-->>User: Append to answer card
    end
    API-->>React: SSE event done
```

1. **Landing** — User types a question or picks an example prompt in the React chat window.
2. **Streaming answer** — Source cards appear first (`sources` event), then GPT-4o-mini streams the answer token by token (`token` events) into the *Krishna's Wisdom* card.
3. **Source attribution** — Retrieved verses remain visible with chapter, verse, relevance score, and text preview for every answer.

---

## Project Structure

```
├── ingestion/       # PDF loading, verse parsing, and indexing orchestration
├── embeddings/      # OpenAI text-embedding-3-small wrapper
├── vector_store/    # Pinecone index management and similarity search
├── chat/            # RAG retrieval and LLM generation
├── api/             # FastAPI app and POST /api/chat SSE endpoint
├── scripts/         # CLI tools for indexing chapters and interactive chat
├── frontend/        # React + Vite chat UI
├── config/          # Environment variable loading
└── data/            # Source PDF (local, gitignored)
```

| Module | Role |
|--------|------|
| `ingestion/` | Reads the Gita PDF, extracts verses by chapter, and upserts them into Pinecone |
| `embeddings/` | Converts verse text into 768-dimensional vectors |
| `vector_store/` | Creates the Pinecone index, upserts vectors, and runs similarity queries |
| `chat/` | Retrieves relevant verses and generates grounded answers via GPT-4o-mini |
| `api/` | Exposes a streaming chat endpoint consumed by the frontend |
| `scripts/` | Command-line indexing and chat for development and testing |
| `frontend/` | Chat window, message bubbles, and source citation cards |

---

## Screenshots

### Landing page

![Landing page](docs/assets/landing.png)

### Streaming answer

![Streaming answer](docs/assets/answer.png)

### Source citations

![Source citations with relevance scores](docs/assets/sources.png)

---

*Source text: Bhagavad-gita As It Is (A.C. Bhaktivedanta Swami Prabhupada)*
