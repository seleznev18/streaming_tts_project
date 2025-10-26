import base64
import logging

from app.clients import ASRClient, TTSClient
from app.schemas import GatewayResponse
from fastapi import APIRouter, File, Query, UploadFile

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/gateway/tts-from-audio", response_model=GatewayResponse)
async def tts_from_audio(
    file: UploadFile = File(...),
    sr: int = Query(16000),
    ch: int = Query(1),
    lang: str = Query("en")
):
    """
    Accept PCM bytes -> send to ASR -> TTS synthesize recognized text -> return JSON with text and base64 audio.
    """
    pcm_bytes = await file.read()
    asr = ASRClient()
    tts = TTSClient()

    asr_text = await asr.transcribe_bytes(pcm_bytes, sr=sr, ch=ch, lang=lang)
    logger.info(f"ASR text: {asr_text!r}")

    pcm_out = await tts.synthesize(asr_text)
    b64_audio = base64.b64encode(pcm_out).decode("utf-8")

    return GatewayResponse(asr_text=asr_text, tts_audio_b64=b64_audio)
