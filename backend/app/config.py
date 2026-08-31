from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    groq_tts_model: str = "canopylabs/orpheus-v1-english"
    groq_tts_voice: str = "tara"
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_stt_model: str = "gpt-4o-mini-transcribe"
    database_url: str = "postgresql://postgres:password@localhost:5432/financial_advisor"

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
