import logging

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class ASRModel:
    def __init__(self, model_size: str = "small.en"):
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            download_root="/app/models", 
        )

    def transcribe(self, audio, sample_rate: int, language: str):
        """Выполняет распознавание речи, устойчиво обрабатывая разные типы входа."""

        # Безопасное определение длины входных данных
        if isinstance(audio, (bytes, bytearray)):
            input_len = len(audio)
        elif hasattr(audio, "getbuffer"):
            try:
                input_len = len(audio.getbuffer())
            except Exception:
                input_len = -1
        elif hasattr(audio, "__len__"):
            try:
                input_len = len(audio)
            except Exception:
                input_len = -1
        else:
            input_len = -1

        logger.info("Running inference... (input length=%d)", input_len)

        # Если аудио пустое — сразу возвращает пустой результат
        if input_len == 0:
            logger.warning("Empty audio input received. Returning empty result.")
            return "", []

        try:
            segments, info = self.model.transcribe(
                audio,
                beam_size=1,
                language=language,
            )
        except Exception as e:
            logger.error("ASR inference failed: %s", e)
            raise

        all_segments = []
        text_full = ""
        for seg in segments:
            text_full += seg.text.strip() + " "
            all_segments.append(
                {
                    "start_ms": int(seg.start * 1000),
                    "end_ms": int(seg.end * 1000),
                    "text": seg.text.strip(),
                }
            )

        text_full = text_full.strip()
        logger.info("ASR done: %s", text_full)
        return text_full, all_segments
