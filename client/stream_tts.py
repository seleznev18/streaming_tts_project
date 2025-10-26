import asyncio
import json
import os
import time
import wave
from pathlib import Path

import websockets
from dotenv import load_dotenv

# === Загрузка .env ===
base_dir = Path(__file__).parent.parent
dotenv_path = base_dir / ".env"
load_dotenv(dotenv_path)

TTS_WS_URL = os.getenv("TTS_WS_URL")
OUT_WAV = Path(__file__).parent / "out.wav"
SAMPLE_RATE = int(os.getenv("TTS_SAMPLE_RATE", 22050))

async def stream_tts(text: str):
    print(f"Connecting to {TTS_WS_URL}")
    start_time = time.time()
    pcm_data = bytearray()
    chunk_count = 0

    async with websockets.connect(TTS_WS_URL, max_size=None) as ws:
        await ws.send(json.dumps({"text": text}))
        print(f"Sent text: {text!r}")

        while True:
            msg = await ws.recv()
            if isinstance(msg, bytes):
                if chunk_count == 0:
                    first_chunk_time = time.time() - start_time
                chunk_count += 1
                pcm_data.extend(msg)
                print(f"Received chunk #{chunk_count} ({len(msg)} bytes)")
                continue

            data = json.loads(msg)
            if data.get("type") == "end":
                print("Stream ended normally")
                break
            if "error" in data:
                raise RuntimeError(f"TTS error: {data['error']}")

    total_time = time.time() - start_time
    print(f"Received {chunk_count} chunks in {total_time:.2f}s (first chunk latency {first_chunk_time:.2f}s)")

    with wave.open(str(OUT_WAV), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)

    print(f"Saved synthesized audio to {OUT_WAV} ({len(pcm_data)} bytes, {SAMPLE_RATE} Hz)")

if __name__ == "__main__":
    text = input("Enter text to synthesize: ") or "Hello from streaming TTS!"
    asyncio.run(stream_tts(text))
