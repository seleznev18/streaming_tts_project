import logging

from app.http import router as http_router
from app.logging_conf import setup_logging
from app.settings import settings
from app.ws import handle_ws_connection
from fastapi import FastAPI, WebSocket

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gateway Service", version="1.0.0")
app.include_router(http_router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.websocket("/ws/gateway")
async def ws_gateway(ws: WebSocket):
    await handle_ws_connection(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",
                host=settings.GATEWAY_HOST,
                port=settings.GATEWAY_PORT,
                log_level=settings.LOG_LEVEL.lower(),
                reload=True)
