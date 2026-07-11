from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI

from .auth import verify_api_key
from .routers import chat, models, speech


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create an HTTPX AsyncClient that will be shared across requests
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield


def create_app() -> FastAPI:
    """
    FastAPIアプリケーションを作成し、ルーターを設定します。
    """
    app = FastAPI(
        title="OpenAI-Compatible Japanese TTS API",
        description="VOICEVOX / Open JTalk / Piper をOpenAIの音声合成APIフォーマットで利用するためのAPI",
        version="0.2.0",
        lifespan=lifespan,
        dependencies=[Depends(verify_api_key)],
    )

    # ルーターの登録
    app.include_router(models.router)
    app.include_router(chat.router)
    app.include_router(speech.router)

    return app
