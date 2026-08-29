from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat

app = FastAPI(title="Bhagavad Gita Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
