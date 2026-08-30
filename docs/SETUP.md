# Running the Bhagavad Gita RAG Chatbot

Step-by-step guide to install, index verses, and run the chatbot locally.

---

## Prerequisites

- **Python 3.12+** (see `.python-version` in the project root)
- **`uv`** for Python package management
- **Node.js + npm** for the frontend
- **OpenAI API key** — used for embeddings and chat completions
- **Pinecone API key** — used for vector storage and similarity search
- **Bhagavad-gita PDF** — place `Bhagavad-gita-As-It-Is.pdf` in the `data/` folder (this folder is gitignored)

---

## 1. Install dependencies

From the project root:

```bash
uv sync
cd frontend && npm install
```

---

## 2. Environment setup

Copy the example env file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` at the project root:

```env
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=gita-verses
```

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Embeddings (`text-embedding-3-small`) and chat (`gpt-4o-mini`) |
| `PINECONE_API_KEY` | Vector index creation and queries |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `gita-verses`) |

---

## 3. One-time indexing

Before the chatbot can answer questions, verses must be parsed from the PDF, embedded, and stored in Pinecone. This is a **one-time offline step** — the running app only reads from Pinecone, it does not process the PDF.

1. Place the PDF at `data/Bhagavad-gita-As-It-Is.pdf`
2. Run the indexing CLI from the project root:

```bash
# Index all 18 chapters
uv run python scripts/index_all.py

# Index specific chapters
uv run python scripts/index_all.py --chapters 1 2 18

# Index a chapter range
uv run python scripts/index_all.py --start 1 --end 5

# Index a single chapter
uv run python scripts/index_chapter.py --chapter 1
```

Once complete, ~700 verse vectors are stored in Pinecone with translation, commentary, and chapter/verse metadata. The index persists — you only need to re-run indexing if the PDF or embedding logic changes.

---

## 4. Run the app

Start the backend and frontend in **two separate terminals**.

### Terminal 1 — Backend (FastAPI)

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Verify it is running: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Terminal 2 — Frontend (React + Vite)

```bash
cd frontend
npm run dev
```

Open the app: [http://localhost:5173](http://localhost:5173)

The Vite dev server proxies `/api` requests to `http://localhost:8000`, so the frontend talks to the backend without extra configuration.

---

## 5. CLI chat (optional)

You can test the RAG pipeline from the command line without the frontend:

```bash
# Ask a single question
uv run python scripts/chat.py "What is karma yoga?"

# Interactive mode (type 'exit' or 'quit' to stop)
uv run python scripts/chat.py

# Retrieve fewer/more verses
uv run python scripts/chat.py "What is dharma?" --top-k 3
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Missing required environment variable` | Ensure `.env` exists at the project root with all three keys set |
| `No verses found for chapter X` | Check that `data/Bhagavad-gita-As-It-Is.pdf` exists and the filename matches exactly |
| Empty or irrelevant answers | Run indexing first — the Pinecone index must be populated before chat works |
| Frontend cannot reach the API | Confirm the backend is running on port 8000 before starting the frontend |
| CORS errors | Use the frontend at `http://localhost:5173` (the only origin allowed by the API) |

---

## Ports reference

| Service | Port | URL |
|---------|------|-----|
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| Frontend (Vite) | 5173 | http://localhost:5173 |
