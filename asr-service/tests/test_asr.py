import io

import pytest
from app.asr import ASRModel


@pytest.fixture(scope="module")
def asr_model():
    return ASRModel(model_size="small.en")


def test_asr_empty_audio(asr_model):
    """Проверка: пустой вход должен вернуть пустую строку и список сегментов"""
    empty_audio = io.BytesIO(b"")
    text, segments = asr_model.transcribe(empty_audio, sample_rate=16000, language="en")
    assert text == ""
    assert segments == []


def test_asr_invalid_audio(asr_model):
    """Проверка: битые данные должны вызвать исключение"""
    with pytest.raises(Exception):
        # имитируем поврежденный WAV (байты вместо float)
        asr_model.transcribe(io.BytesIO(b"\x00\x11\x22\x33"), sample_rate=16000, language="en")
