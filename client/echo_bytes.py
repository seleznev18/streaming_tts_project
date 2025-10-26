import base64
import os
import subprocess
import sys
import wave
from pathlib import Path

import requests
from dotenv import load_dotenv

# === Загрузка .env ===
base_dir = Path(__file__).parent.parent
dotenv_path = base_dir / ".env"
load_dotenv(dotenv_path)

GATEWAY_URL = os.getenv("GATEWAY_URL")
INPUT_DIR = Path(__file__).resolve().parents[1] / "my_audio"
OUTPUT_DIR = Path(__file__).resolve().parent
PCM_PATH = OUTPUT_DIR / "converted.pcm"
OUT_WAV = OUTPUT_DIR / "out_echo.wav"

def find_audio_file() -> Path:
    for ext in ("*.mp3", "*.wav", "*.m4a"):
        files = list(INPUT_DIR.glob(ext))
        if files:
            return files[0]
    print(f"В {INPUT_DIR} нет аудио файлов (.mp3/.wav/.m4a)")
    sys.exit(1)

def convert_to_pcm(input_path: Path):
    print(f"Конвертирую {input_path.name} → {PCM_PATH.name}")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-ac", "1",
        "-ar", "16000",
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        str(PCM_PATH),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Конвертация завершена.")

def send_to_gateway(pcm_path: Path):
    params = {"sr": 16000, "ch": 1, "lang": "en"}
    with open(pcm_path, "rb") as f:
        files = {"file": (pcm_path.name, f, "application/octet-stream")}
        print(f"POST → {GATEWAY_URL}")
        r = requests.post(GATEWAY_URL, params=params, files=files)

    if r.status_code != 200:
        print(f"Ошибка {r.status_code}: {r.text}")
        sys.exit(1)

    data = r.json()
    print(f"Распознанный текст: {data['asr_text']!r}")

    if not data.get("tts_audio_b64"):
        print("Нет синтезированного аудио в ответе")
        return

    pcm_bytes = base64.b64decode(data["tts_audio_b64"])
    with wave.open(str(OUT_WAV), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(pcm_bytes)

    print(f"Сохранено озвученное аудио → {OUT_WAV}")

def main():
    input_file = find_audio_file()
    convert_to_pcm(input_file)
    send_to_gateway(PCM_PATH)

if __name__ == "__main__":
    main()
