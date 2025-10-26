from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str
    TTS_HOST: str
    TTS_PORT: int

    TTS_VOICE: str
    TTS_SAMPLE_RATE: int
    TTS_CHUNK_MS: int
    TTS_MODELS_DIR: str


settings = Settings()
