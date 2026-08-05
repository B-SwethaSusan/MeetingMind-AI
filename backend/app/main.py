from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routes.meeting import router as meeting_router
from app.routes.chat import router as chat_router


BASE_DIR = Path(__file__).resolve().parent
INTERFACE_DIR = BASE_DIR.parent / "interface"

app = FastAPI(
    title="Meeting Transcript AI",
    description="""
# 🤖 Meeting Transcript AI

An AI-powered meeting assistant built with FastAPI, PydanticAI, and Ollama.

## Features

- 📄 Analyze meeting transcripts (paste plain text or upload .txt)
- 💬 Ask follow-up questions about the latest transcript
- 📊 Speaker contribution statistics
- ✅ Action item extraction
- 📅 Deadline detection
- 🔥 Priority detection

## Workflow

### Option 1 — Web UI
Open the home page in your browser (served at `/`) and paste or upload a transcript.

### Option 2 — Swagger / cURL
- **POST /meeting/analyze** — send a plain text body
- **POST /meeting/upload** — multipart upload of a .txt file
- **POST /chat** — send a plain text question

The latest analyzed/uploaded transcript is kept in memory for chatting.
""",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(meeting_router)
app.include_router(chat_router)


# --- Serve the simple HTML interface if it exists ---
if INTERFACE_DIR.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=INTERFACE_DIR),
        name="interface-static",
    )


@app.get("/", tags=["Home"], summary="API Home / Web UI")
def home():
    index = INTERFACE_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {
        "message": "Meeting Transcript AI API is running 🚀",
        "version": "2.0.0",
        "docs": "/docs",
        "ui": "interface/index.html not found",
    }


@app.get("/ui", tags=["Home"], summary="Open the web UI")
def ui():
    index = INTERFACE_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"], summary="Health Check")
def health():
    return {"status": "healthy"}
