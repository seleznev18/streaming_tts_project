import pytest
from app.tts import TTSModel


@pytest.fixture(scope="module")
def tts_model():
    return TTSModel(models_dir="/app/models", voice="en-us-lessac-medium.onnx")


def test_tts_empty_text(tts_model):
    """Проверка: пустой текст должен вернуть пустое аудио"""
    pcm = tts_model.synthesize("")
    assert pcm == b"" or pcm is None


def test_tts_normal_text(tts_model):
    """Проверка: обычный текст возвращает непустой PCM"""
    pcm = tts_model.synthesize("Hello world")
    assert isinstance(pcm, (bytes, bytearray))
    assert len(pcm) > 1000
