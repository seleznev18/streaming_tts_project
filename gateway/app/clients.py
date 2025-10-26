import logging

import aiohttp
import websockets
from app.settings import settings

logger = logging.getLogger(__name__)

class ASRClient:
    async def transcribe_bytes(self, pcm_bytes: bytes, sr: int = 16000, ch: int = 1, lang: str = "en") -> str:
        params = {"sr": sr, "ch": ch, "lang": lang}
        data = aiohttp.FormData()
        data.add_field("file", pcm_bytes, filename="audio.pcm", content_type="application/octet-stream")

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.HTTP_TIMEOUT)) as session:
            async with session.post(settings.ASR_URL, data=data, params=params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"ASR request failed: {resp.status} {text}")
                js = await resp.json()
                return js.get("text", "")


class TTSClient:
    async def synthesize(self, text: str) -> bytes:
        pcm = bytearray()
        async with websockets.connect(settings.TTS_WS_URL, max_size=None) as ws:
            await ws.send(f'{{"text": "{text}"}}')
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    pcm.extend(msg)
                    continue
                if '"type": "end"' in msg:
                    break
        return bytes(pcm)
