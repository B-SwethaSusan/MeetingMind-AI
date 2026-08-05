import httpx

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.output import NativeOutput
from pydantic_ai.providers.ollama import OllamaProvider

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from app.models.response_models import ChatAnswer


class ChatService:

    latest_transcript = ""

    def __init__(self):

        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(OLLAMA_TIMEOUT_SECONDS)
        )
        provider = OllamaProvider(
            base_url=OLLAMA_BASE_URL,
            http_client=self.http_client,
        )
        model = OllamaModel(model_name=OLLAMA_MODEL, provider=provider)

        self.agent = Agent(
            model,
            output_type=NativeOutput(ChatAnswer),
            system_prompt="""Answer questions only from the supplied meeting transcript.
Return JSON with `answer` and `evidence`. Evidence must be an exact consecutive
quote copied from the transcript that directly supports the answer. Do not infer,
guess, or use outside knowledge. If the answer is not directly supported, return
answer exactly `Not mentioned in the transcript.` and evidence as an empty string.""",
        )

    @staticmethod
    def _normalise(text: str) -> str:
        return " ".join(text.casefold().split())

    async def ask_question(self, question: str):

        prompt = f"""Meeting Transcript:
{ChatService.latest_transcript}

Question: {question}

Answer briefly and factually."""

        result = await self.agent.run(prompt)
        output = result.output
        evidence = output.evidence.strip()

        # Do not expose a model claim unless its quoted evidence is actually in
        # the transcript. This keeps Q&A grounded even with a small local model.
        if evidence and self._normalise(evidence) in self._normalise(ChatService.latest_transcript):
            return {"answer": output.answer.strip(), "evidence": evidence}

        return {
            "answer": "Not mentioned in the transcript.",
            "evidence": "",
        }
