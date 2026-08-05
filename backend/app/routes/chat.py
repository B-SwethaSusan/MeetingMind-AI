from fastapi import APIRouter, HTTPException

from app.models.request_models import ChatRequest
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Meeting Chat"]
)

service = ChatService()


@router.post("/")
async def ask(
    request: ChatRequest,
) -> dict[str, str]:
    if not ChatService.latest_transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Analyze a meeting transcript before asking a question.",
        )
    return await service.ask_question(request.question)
