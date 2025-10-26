from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str
    ASR_MODEL_SIZE: str
    ASR_SAMPLE_RATE: int
    ASR_MODELS_DIR: str
    ASR_HOST: str
    ASR_PORT: int


settings = Settings()
