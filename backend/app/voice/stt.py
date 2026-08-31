from pathlib import Path
from openai import OpenAI
from app.config import get_settings

_settings = get_settings()
_client = OpenAI(api_key=_settings.openai_api_key)


def transcribe(audio_path: str | Path) -> str:
    """Transcribe an audio file to text using OpenAI's transcription API."""
    audio_path = Path(audio_path)
    with open(audio_path, "rb") as f:
        result = _client.audio.transcriptions.create(
            file=(audio_path.name, f),
            model=_settings.openai_stt_model,
            response_format="text",
        )
    return result  # type: ignore[return-value]
