from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str
    GATEWAY_HOST: str
    GATEWAY_PORT: int

    ASR_URL: str
    TTS_WS_URL: str

    HTTP_TIMEOUT: float
    WS_TIMEOUT: float


settings = Settings()
