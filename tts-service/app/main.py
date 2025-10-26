import json
import logging

from app.logging_conf import setup_logging
from app.settings import settings
from app.tts import TTSModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Service (Piper)", version="1.0.0")

tts_model = None

@app.on_event("startup")
async def startup_event():
    global tts_model
    logger.info("Loading Piper TTS model...")
    tts_model = TTSModel(
        models_dir=settings.TTS_MODELS_DIR,
        voice=settings.TTS_VOICE,
        sample_rate=settings.TTS_SAMPLE_RATE,
        chunk_ms=settings.TTS_CHUNK_MS,
    )
    logger.info("Piper TTS ready.")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.websocket("/ws/tts")
async def ws_tts_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            try:
                payload = json.loads(data)
                text = payload.get("text", "").strip()
            except Exception:
                await ws.send_text(json.dumps({"error": "invalid json"}))
                continue

            if not text:
                await ws.send_text(json.dumps({"error": "empty text"}))
                continue

            logger.info("Generating speech for text len=%d", len(text))
            try:
                for chunk in tts_model.stream_text(text):
                    await ws.send_bytes(chunk)
                await ws.send_text(json.dumps({"type": "end"}))
            except Exception as e:
                logger.exception("TTS streaming error")
                await ws.send_text(json.dumps({"error": str(e)}))
    except WebSocketDisconnect:
        logger.info("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.TTS_HOST,
        port=settings.TTS_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=True,
    )
