import re

from app.agent.meeting_agent import MeetingAgent
from app.models.response_models import MeetingAnalysis
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService


class MeetingService:

    _DIRECT_ASSIGNMENT_PATTERN = re.compile(
        r"^\s*(?:\[[^\]]+\]\s*)?(?P<speaker>[A-Za-z][A-Za-z .'\-]{0,40})"
        r"(?:\s*\([^)]+\))?\s*:\s*(?P<assignee>[A-Za-z][A-Za-z .'\-]{0,40}),\s*"
        r"(?P<task>.+)$",
        re.MULTILINE,
    )

    _DEADLINE_PATTERN = re.compile(
        r"\b(?:by|before|due(?:\s+by)?|on)\s+"
        r"((?:(?:next|this)\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"(?:\s+(?:morning|afternoon|evening))?|today|tomorrow|end\s+of\s+day|eod|"
        r"this\s+week|next\s+week|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b",
        re.IGNORECASE,
    )

    # Common words that are NEVER a department name
    _DEPARTMENT_BLOCKLIST = {
        "the", "a", "an", "and", "or", "meeting", "call", "team",
        "everyone", "all", "guys", "folks", "people", "room",
        "this", "that", "today", "now", "here", "there",
    }

    # Heuristics for department detection
    _DEPARTMENT_PATTERNS = [
        re.compile(r"\b(department\s*[:\-]\s*([A-Za-z &/]+))", re.IGNORECASE),
        re.compile(r"\b(team\s*[:\-]\s*([A-Za-z &/]+))", re.IGNORECASE),
        re.compile(r"\b(division\s*[:\-]\s*([A-Za-z &/]+))", re.IGNORECASE),
    ]

    # Heuristics for date detection
    _DATE_PATTERNS = [
        # 24/07/2026, 24-07-2026, 2026-07-24
        re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
        re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
        # July 24, 2026 / Jul 24 2026
        re.compile(
            r"\b((?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December|Jan|Feb|Mar|Apr|Jun|"
            r"Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}(?:,)?\s+\d{4})\b",
            re.IGNORECASE
        ),
        # 24 July 2026
        re.compile(
            r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)\s+\d{4})\b",
            re.IGNORECASE
        ),
    ]

    def __init__(self):

        self.meeting_agent = MeetingAgent()

    # ---------- deterministic fallbacks ----------

    def _fallback_meeting_date(self, transcript: str) -> str | None:
        # Prefer "Meeting Date: ..." style header if present
        header = re.search(
            r"meeting\s*date\s*[:\-]\s*([^\n\r]+)",
            transcript,
            re.IGNORECASE
        )
        if header:
            value = header.group(1).strip()
            if value:
                return value.rstrip(" .;,")

        for pattern in self._DATE_PATTERNS:
            match = pattern.search(transcript)
            if match:
                return match.group(1).strip()
        return None

    def _fallback_department(self, transcript: str) -> str | None:
        for pattern in self._DEPARTMENT_PATTERNS:
            match = pattern.search(transcript)
            if not match:
                continue
            value = match.group(2).strip().rstrip(" .;,")
            tokens = value.lower().split()
            if not tokens:
                continue
            if any(t in self._DEPARTMENT_BLOCKLIST for t in tokens):
                continue
            if len(value) > 60:
                continue
            return value
        return None

    def _fallback_deadline(self, transcript: str, assignee: str, task: str) -> str | None:
        """Find an explicitly stated deadline near an action item's wording."""
        keywords = [word.lower() for word in re.findall(r"[A-Za-z]{4,}", task)]
        candidates = transcript.splitlines() or [transcript]

        for line in candidates:
            normalized = line.lower()
            matches_task = bool(keywords) and any(word in normalized for word in keywords)
            if assignee.lower() not in normalized and not matches_task:
                continue
            match = self._DEADLINE_PATTERN.search(line)
            if match:
                return match.group(1).strip()

        return None

    def _correct_direct_assignees(self, transcript: str, analysis: MeetingAnalysis) -> None:
        """Correct the common speaker-versus-recipient assignment ambiguity."""
        assignments = list(self._DIRECT_ASSIGNMENT_PATTERN.finditer(transcript))
        for item in analysis.action_items:
            task_words = set(re.findall(r"[a-z]{4,}", item.task.lower()))
            for match in assignments:
                speaker = match.group("speaker").strip()
                assignee = match.group("assignee").strip()
                line_words = set(re.findall(r"[a-z]{4,}", match.group("task").lower()))
                if item.assignee.strip().lower() == speaker.lower() and task_words & line_words:
                    item.assignee = assignee
                    break

    # ---------- main entry point ----------

    async def analyze_meeting(
        self,
        transcript: str
    ) -> MeetingAnalysis:

        transcript = transcript.strip()

        analysis = await self.meeting_agent.analyze_transcript(
            transcript
        )

        self._correct_direct_assignees(transcript, analysis)

        for item in analysis.action_items:
            if item.deadline.strip().lower() in {"", "not mentioned", "n/a", "none", "unknown"}:
                fallback = self._fallback_deadline(transcript, item.assignee, item.task)
                if fallback:
                    item.deadline = fallback

        # Stash for follow-up chat
        ChatService.latest_transcript = transcript
        MemoryService.latest_transcript = transcript

        # ---- Fallback: meeting_date ----
        if not analysis.meeting_date or analysis.meeting_date.strip().lower() in {
            "", "not mentioned", "n/a", "none", "unknown"
        }:
            fallback = self._fallback_meeting_date(transcript)
            if fallback:
                analysis.meeting_date = fallback

        # ---- Fallback: department ----
        if not analysis.department or analysis.department.strip().lower() in {
            "", "not mentioned", "n/a", "none", "unknown"
        }:
            fallback = self._fallback_department(transcript)
            if fallback:
                analysis.department = fallback

        return analysis
