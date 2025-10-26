import logging

import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from starlette.requests import Request

from app.asr import ASRModel
from app.logging_conf import setup_logging
from app.schemas import STTResponse
from app.settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="ASR Service", version="1.0.0")
setup_logging(settings.LOG_LEVEL)

asr_model = None


@app.on_event("startup")
async def load_model():
    global asr_model
    logger.info("Loading ASR model: faster-whisper %s", settings.ASR_MODEL_SIZE)
    asr_model = ASRModel(model_size=settings.ASR_MODEL_SIZE)
    logger.info("ASR model loaded.")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/stt/bytes", response_model=STTResponse)
async def stt_bytes(
    request: Request,
    sr: int = Query(default=16000, ge=8000, le=48000),
    ch: int = Query(default=1, ge=1, le=2),
    lang: str = Query(default="en"),
    file: UploadFile = File(...),
):
    if not asr_model:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    try:
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        if ch == 2:
            audio_np = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)

        duration_sec = len(audio_np) / sr
        if duration_sec > 15:
            raise HTTPException(
                status_code=413, detail=f"Audio too long ({duration_sec:.2f}s > 15s)"
            )

        audio_float = audio_np.astype(np.float32) / 32768.0

        text, segments = asr_model.transcribe(audio_float, sr, lang)
        return STTResponse(text=text, segments=segments)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during STT processing")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.ASR_HOST,
        port=settings.ASR_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=True,
    )
