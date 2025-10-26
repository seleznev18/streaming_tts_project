import logging
import subprocess
import threading
import time
from pathlib import Path
from shutil import which
from typing import Iterator

logger = logging.getLogger(__name__)


def looks_like_text(b: bytes, threshold: float = 0.6) -> bool:
    """
    Return True if `b` contains a high fraction of printable ASCII characters.
    Helps detect when stdout contains text logs instead of raw PCM.
    """
    if not b:
        return False
    s = b[:200]
    printable = sum(1 for ch in s if 32 <= ch <= 126)
    ratio = printable / len(s)
    return ratio >= threshold


class TTSModel:
    """
    Piper streaming wrapper.

    """

    def __init__(
        self,
        models_dir: str = "/app/models",
        voice: str = "en-us-lessac-medium.onnx",
        sample_rate: int = 22050,
        chunk_ms: int = 80,
    ):
        self.models_dir = str(models_dir)
        self.voice = voice
        self.sample_rate = int(sample_rate)
        self.chunk_ms = int(chunk_ms)
        self.chunk_bytes = int(self.sample_rate * 2 * self.chunk_ms / 1000)  # 16-bit mono

        # Check for piper presence — raise clear error if missing
        if not which("piper"):
            raise RuntimeError(
                "Piper binary not found in PATH. Install Piper or add it to PATH before using TTSModel."
            )

        self.model_path = Path(self.models_dir) / self.voice
        if not self.model_path.exists():
            raise FileNotFoundError(f"Piper model not found at {self.model_path}")

        logger.info(
            "Initialized Piper TTSModel: model=%s sample_rate=%d chunk_ms=%d",
            self.model_path,
            self.sample_rate,
            self.chunk_ms,
        )

    def stream_text(self, text: str) -> Iterator[bytes]:
        """
        Stream raw PCM from Piper stdout while Piper synthesizes.

        """
        cmd = [
            "piper",
            "--model",
            str(self.model_path),
            "--output_raw",
        ]

        logger.debug("Starting Piper process: %s", " ".join(cmd))

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        # feed text (with newline) in background thread
        def feed():
            try:
                inp = (text + "\n").encode("utf-8")
                proc.stdin.write(inp)
                proc.stdin.flush()
                proc.stdin.close()
            except Exception:
                logger.exception("Failed to feed text to Piper stdin")

        threading.Thread(target=feed, daemon=True).start()

        try:
            while True:
                chunk = proc.stdout.read(self.chunk_bytes)
                if not chunk:
                    break

                if looks_like_text(chunk):
                    stderr = b""
                    try:
                        stderr = proc.stderr.read() or b""
                    except Exception:
                        pass
                    logger.error(
                        "Detected non-audio data in Piper stdout. stderr: %s",
                        stderr.decode("utf-8", errors="ignore"),
                    )
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    raise RuntimeError("Piper stdout contained text instead of PCM.")

                yield chunk
                time.sleep(self.chunk_ms / 1000.0)
        finally:
            # cleanup
            try:
                proc.stdin.close()
            except Exception:
                pass
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except Exception:
                    pass

    def synthesize_stream(self, text: str) -> Iterator[bytes]:
        return self.stream_text(text)

    def synthesize(self, text: str) -> bytes:
        """
        Collect all PCM chunks for given text and return single bytes object.

        """
        collected = bytearray()
        for chunk in self.stream_text(text):
            collected.extend(chunk)
        return bytes(collected)
