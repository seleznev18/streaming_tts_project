from pydantic import BaseModel


class ASRResponse(BaseModel):
    text: str

class TTSPayload(BaseModel):
    text: str

class GatewayResponse(BaseModel):
    asr_text: str
    tts_audio_b64: str | None = None
