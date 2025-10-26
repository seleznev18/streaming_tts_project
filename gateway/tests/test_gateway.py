
import aiohttp
import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_gateway_asr_unavailable(monkeypatch):
    """Если ASR-сервис недоступен — должно быть исключение"""
    import app.clients as clients

    async def fake_post(*args, **kwargs):
        raise aiohttp.ClientConnectorError(None, OSError("Connection refused"))

    monkeypatch.setattr(clients.aiohttp.ClientSession, "post", fake_post)

    from app.http import tts_from_audio
    from starlette.requests import Request

    # создаем поддельный запрос с аудио
    req = Request({"type": "http", "method": "POST"})
    with pytest.raises(Exception):
        await tts_from_audio(req, sr=16000, ch=1, lang="en")





@pytest.mark.asyncio
async def test_gateway_invalid_audio():
    """Отправка пустого файла должна вызывать ошибку 400"""
    client = TestClient(app)  # локальный клиент FastAPI
    response = client.post(
        "/api/gateway/tts-from-audio",
        files={"file": ("", b"")}  # пустой файл
    )
    assert response.status_code >= 400
