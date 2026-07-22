from fastapi import FastAPI

app = FastAPI(
    title="Meeting Transcript Agent",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Meeting Transcript Agent API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }