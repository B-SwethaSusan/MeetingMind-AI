# MeetingMind-AI

An AI-powered meeting assistant that turns raw meeting transcripts into structured insights — meeting date, department, action items (with deadlines and priority) and per-speaker contribution percentages — and lets you chat with the transcript afterwards.

Stack: **FastAPI · PydanticAI · Ollama (local LLM)**. A small static HTML page is served from the backend so you can use it from any browser, with no React build step.

---

## Project layout

```
meeting-agent/
├── backend/
│   ├── app/
│   │   ├── agent/         # LLM agent + system prompt
│   │   ├── routes/        # FastAPI routers (meeting, chat)
│   │   ├── services/      # Business logic (meeting, statistics, chat, file, memory)
│   │   ├── models/        # Pydantic request / response models
│   │   ├── main.py        # FastAPI app entry point
│   │   └── config.py      # Env-based configuration
│   ├── interface/
│   │   └── index.html     # Built-in static web UI
│   ├── uploads/           # Uploaded transcript files
│   ├── outputs/           # Saved analysis outputs
│   ├── .env               # Local config (Ollama URL, model, timeout)
│   └── requirements.txt
└── frontend/              # Optional React UI (work in progress)
```

---

## Prerequisites

1. **Python 3.10+** (tested with 3.12).
2. **Ollama** installed and running locally — https://ollama.com/download
3. A model pulled, e.g.:
   ```bash
   ollama pull qwen2.5:3b
   ```

   Any small instruction-tuned model works. Set `OLLAMA_MODEL` in `.env` to change it.

---

## Setup (Windows / bash)

```bash
cd "meeting-agent/backend"

# 1. Create / activate a virtual environment
python -m venv .venv
.venv/Scripts/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Ollama (defaults already work for a local server)
#    Edit .env if your setup is different:
#      OLLAMA_BASE_URL=http://localhost:11434/v1
#      OLLAMA_MODEL=qwen2.5:3b
#      OLLAMA_TIMEOUT_SECONDS=900
```

> macOS / Linux: replace `.venv/Scripts/activate` with `source .venv/bin/activate`.

---

## Run

```bash
# Make sure Ollama is running in another terminal:
ollama serve

# Start the backend
cd "meeting-agent/backend"
.venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open any of these in your browser:

| URL                       | What it is                                                 |
|---------------------------|------------------------------------------------------------|
| `http://localhost:8000/`  | **Simple web UI** — paste / upload / chat (recommended)     |
| `http://localhost:8000/ui`| Same UI, alternate path                                    |
| `http://localhost:8000/docs` | Swagger UI (interactive API docs)                       |
| `http://localhost:8000/redoc`| ReDoc API reference                                     |
| `http://localhost:8000/health` | Health check (`{"status":"healthy"}`)                  |

---

## Using the web UI

1. Open `http://localhost:8000/` in a browser.
2. **Paste Text** tab → paste a transcript → click **Analyze Meeting** *or*
3. **Upload .txt** tab → choose a `.txt` file → click **Analyze Meeting**.
4. Right panel shows: meeting date, department, action items, and a bar chart of speaker contribution %.
5. The chat box at the bottom answers questions about the most recently analyzed transcript.

A "Load Sample" button is provided in the UI so you can try it without your own file.

---

## Using the API directly

All endpoints accept and return JSON (or plain text in the request body where noted).

### 1. `POST /meeting/analyze` — paste a transcript as plain text

```bash
curl -X POST http://localhost:8000/meeting/analyze \
     -H "Content-Type: text/plain" \
     --data-binary @transcript.txt
```

Response shape:
```json
{
  "meeting_date": "12 August 2026",
  "department": "AI Platform Engineering",
  "tasks": [
    {
      "name": "Bob",
      "task": "Create API documentation",
      "deadline": "Monday",
      "priority": "High"
    }
  ],
  "speaker_statistics": [
    { "name": "Alice", "percentage": 30 },
    { "name": "Bob",   "percentage": 25 }
  ]
}
```

> Percentages always sum to exactly 100.

### 2. `POST /meeting/upload` — upload a `.txt` file

```bash
curl -X POST http://localhost:8000/meeting/upload \
     -F "file=@transcript.txt"
```

Same response shape as above.

### 3. `POST /chat` — ask about the latest transcript

```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: text/plain" \
     --data "Who is responsible for the QA report?"
```

Response:
```json
{ "question": "...", "answer": "Charlie is responsible for the final QA report." }
```

The latest analyzed / uploaded transcript is kept in memory for the lifetime of the server process.

---

## Accepted transcript formats

The speaker-statistics parser recognizes both styles. Mixing them in the same transcript also works.

**Style A — speaker on its own line:**
```
Alice:
Good morning everyone, let's begin.

Bob:
I finished the auth module.
```

**Style B — speaker and text on the same line:**
```
Alice: Good morning everyone, let's begin.
Bob: I finished the auth module.
```

Optional `Name (Role):` suffix and `[hh:mm]` timestamps are also accepted. A `Meeting Date:` and `Department:` header at the top is recommended for best results.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` to Ollama | Run `ollama serve` in another terminal, or set `OLLAMA_BASE_URL` correctly. |
| `speaker_statistics: []` | Transcript has no recognisable speaker lines. Add `Name:` or `Name: text` markers. |
| `meeting_date: "Not Mentioned"` | Add a `Meeting Date: ...` header or an explicit date in the transcript. |
| UI shows nothing after Analyze | Open browser dev tools → Network. The `/meeting/analyze` request should return 200 with JSON. |
| Very slow responses | Lower the model size (`OLLAMA_MODEL=qwen2.5:1.5b`) or raise `OLLAMA_TIMEOUT_SECONDS`. |

---

## Optional: the React frontend (work in progress)

The `frontend/` directory contains an in-progress React UI (Vite). To run it:

```bash
cd frontend
npm install
npm run dev
```

By default the React dev server expects the backend at `http://localhost:8000`. The simple HTML page served from the backend (`/`) is the recommended UI for now and requires no build step.

---

## Evaluation benchmark

The repository includes a synthetic, anonymized 30-case dataset for measuring
meeting extraction quality. Start Ollama and ensure the selected model is
available before running the benchmark:

```bash
ollama serve
ollama pull qwen2.5:3b

cd backend
.venv/Scripts/python evaluation/run_benchmark.py --model qwen2.5:3b
```

The runner reports date and department accuracy plus action-item precision,
recall, F1, and exact-case accuracy. The dataset is in
`backend/evaluation/meeting_extraction.json`; use anonymized or synthetic data
when adding new cases.
=======


