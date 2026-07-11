"""
APIキー認証モジュール

環境変数 API_KEY が設定されている場合、全リクエストに対して
Authorization: Bearer <key> ヘッダーを検証します。
設定されていない場合は認証をスキップします（開発・ローカル用）。
"""

import os
import secrets

from fastapi import HTTPException, Request

# 環境変数からAPIキーを取得（未設定ならNone）
_API_KEY = os.getenv("API_KEY")


async def verify_api_key(request: Request) -> None:
    """
    APIキーを検証するFastAPI Dependency。

    - ``API_KEY`` 環境変数が **未設定** の場合は認証をスキップします（ローカル開発向け）。
    - 設定されている場合は ``Authorization: Bearer <API_KEY>`` ヘッダーを検証し、
      一致しない場合は **401 Unauthorized** を返します。
    - ヘルスチェック・ドキュメント系のパスは認証をスキップします。
    """
    # ヘルスチェック・OpenAPI ドキュメント系パスは認証不要
    if request.url.path in {"/", "/docs", "/redoc", "/openapi.json"}:
        return

    if _API_KEY is None:
        # APIキー未設定時は認証なし（ローカル開発モード）
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing or invalid. Expected: 'Bearer <API_KEY>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    provided_key = auth_header[len("Bearer "):]
    if not secrets.compare_digest(provided_key, _API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

