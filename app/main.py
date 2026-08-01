from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import parse

app = FastAPI(
    title="Resume Parser API",
    description="AI-powered resume parsing — upload a PDF, DOCX, or TXT resume, get back structured JSON data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
