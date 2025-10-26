import json
import logging

from app.clients import ASRClient, TTSClient
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

async def handle_ws_connection(ws: WebSocket):
    """
    WebSocket duplex pipeline:
    - Client sends binary PCM chunks
    - Gateway feeds them to ASR (end of phrase -> result)
    - Gateway streams synthesized TTS PCM back
    """
    await ws.accept()
    buffer = bytearray()
    asr = ASRClient()
    tts = TTSClient()

    try:
        while True:
            msg = await ws.receive()
            if "bytes" in msg and msg["bytes"]:
                buffer.extend(msg["bytes"])
                continue
            if "text" in msg:
                data = msg["text"].strip()
                if data == "__flush__":
                    # flush buffer: send to ASR, then TTS, then stream result
                    text = await asr.transcribe_bytes(bytes(buffer))
                    logger.info(f"ASR result: {text!r}")
                    await ws.send_text(json.dumps({"asr_text": text}))

                    pcm_out = await tts.synthesize(text)
                    await ws.send_bytes(pcm_out)
                    await ws.send_text(json.dumps({"type": "end"}))
                    buffer.clear()
                elif data == "__close__":
                    break
                else:
                    await ws.send_text(json.dumps({"error": "unknown command"}))
    except WebSocketDisconnect:
        logger.info("Client disconnected.")
