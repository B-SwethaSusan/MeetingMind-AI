from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.request_models import TranscriptRequest
from app.models.response_models import MeetingAnalysis
from app.services.meeting_service import MeetingService
from app.services.file_service import FileService

router = APIRouter(
    prefix="/meeting",
    tags=["Meeting"]
)

meeting_service = MeetingService()
file_service = FileService()


@router.post(
    "/analyze",
    response_model=MeetingAnalysis,
    summary="Analyze a meeting transcript (paste plain text)",
    description=(
        "Paste a meeting transcript as plain text in the request body. "
        "Returns meeting date, department, action items (tasks) and "
        "speaker contribution statistics."
    ),
)
async def analyze(
    request: TranscriptRequest,
) -> MeetingAnalysis:
    """
    Analyze a JSON payload containing a meeting transcript.
    """
    transcript = request.transcript
    if not transcript or not transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Transcript is empty. Please paste a meeting transcript.",
        )
    return await meeting_service.analyze_meeting(transcript)


@router.post(
    "/upload",
    response_model=MeetingAnalysis,
    summary="Upload a .txt transcript file",
)
async def upload(
    file: UploadFile = File(...)
):
    path = await file_service.save(file)
    with open(path, "r", encoding="utf-8") as f:
        transcript = f.read()
    return await meeting_service.analyze_meeting(transcript)
