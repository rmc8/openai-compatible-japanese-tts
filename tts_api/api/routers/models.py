from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Model(BaseModel):
    id: str
    object: str = "model"
    owned_by: str
    permission: List[dict] = []


@router.get("/v1/models", summary="利用可能なモデル一覧を取得")
async def list_models():
    """
    利用可能なモデルの一覧を返します。
    VOICEVOX, Open JTalk, Piper の各音声合成エンジンに対応しています。
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "voicevox-v1",
                "object": "model",
                "owned_by": "VOICEVOX",
                "permission": [],
            },
            {
                "id": "openjtalk-v1",
                "object": "model",
                "owned_by": "Open JTalk",
                "permission": [],
            },
            {
                "id": "piper-v1",
                "object": "model",
                "owned_by": "Piper",
                "permission": [],
            },
        ],
    }


@router.get("/", summary="APIのルートエンドポイント")
async def root():
    """
    APIのルートエンドポイント。
    基本的な情報とドキュメントへのリンクを提供します。
    """
    return {
        "name": "VOICEVOX OpenAI TTS API",
        "version": "1.0.0",
        "description": "VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
        "documentation": "/docs",
        "status": "running",
    }
