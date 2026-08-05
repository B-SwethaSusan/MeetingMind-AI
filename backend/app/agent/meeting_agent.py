import httpx

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.output import NativeOutput
from pydantic_ai.providers.ollama import OllamaProvider

from app.agent.prompt import SYSTEM_PROMPT
from app.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS,
)
from app.models.response_models import MeetingAnalysis


class MeetingAgent:

    def __init__(self):

        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                OLLAMA_TIMEOUT_SECONDS
            )
        )

        provider = OllamaProvider(
            base_url=OLLAMA_BASE_URL,
            http_client=self.http_client
        )

        model = OllamaModel(
            model_name=OLLAMA_MODEL,
            provider=provider
        )

        self.agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            output_type=NativeOutput(MeetingAnalysis),
            retries=2
        )

    async def analyze_transcript(
        self,
        transcript: str
    ) -> MeetingAnalysis:

        transcript = transcript.strip()

        result = await self.agent.run(transcript)

        return result.output

    async def close(self):

        await self.http_client.aclose()