# CHANGELOG

本プロジェクトのすべての重要な変更履歴は、このファイルに記録されます。

---

## [0.2.1] - 2026-07-12

### 追加
- **APIキー認証 (`API_KEY`)**:
  - 環境変数 `API_KEY` を設定した場合、すべてのエンドポイントで `Authorization: Bearer <APIキー>` ヘッダーを検証するミドルウェアを追加。
  - 設定しない場合は認証なしのローカル開発モードとして動作する。
  - OpenAI SDK の `api_key` パラメータとそのまま互換性があるため、クライアント側の変更は不要。
- **`.env.example`**:
  - 環境変数の設定例ファイルを追加。

### 変更
- **サンプルスクリプトのマルチエンジン対応**:
  - `example/simple_tts_example.py` および `example/tts_example.py` のデフォルトモデルを `piper-v1` / `openjtalk-v1` に変更し、マルチエンジンテストに対応。
  - OpenAI SDK (v1+) が必要とするベースURL (`/v1` サフィックス) を修正。
  - `output/` ディレクトリの自動作成を追加。
- **アプリ名・バージョンの更新**:
  - FastAPI の `title` を `OpenAI-Compatible Japanese TTS API` に変更し、バージョンを `0.2.0` に同期。

---

## [0.2.0] - 2026-07-12

### 追加
- **マルチエンジン対応**:
  - `Open JTalk` エンジン（ローカル動作）を統合し、モデル `openjtalk-v1` として提供。
  - `Piper` エンジン（ローカルONNX動作）を統合し、モデル `piper-v1` として提供。日本語音声モデル `ja_JP-kokoro-medium` を同梱。
- **リアルタイム音声変換 (ffmpeg)**:
  - 生成された WAV 音声を、`ffmpeg` を使用してリアルタイムで MP3 にエンコードして返却する機能を追加。
  - リクエストパラメータ `response_format`（`mp3` / `wav`）へ正しく追従するように拡張。
- **ライセンス定義**:
  - リポジトリのルートに [LICENSE](LICENSE) (MIT License) ファイルを新規設定。

### 変更・最適化
- **パッケージ管理の移行 (`uv`)**:
  - `requirements.txt` を廃止し、`pyproject.toml` と `uv.lock` を用いた `uv` での依存関係管理へ全面移行。
  - プロジェクト名を `japanese-tts-api` とし、アプリケーションパッケージ (`package = false`) として定義。
- **Python環境のアップグレード**:
  - Docker および `uv` で動作する Python 実行環境のバージョンを `3.9` から **`3.12`** へアップグレード。
  - `pyproject.toml` の Python 要求条件を `requires-python = ">=3.12"` に引き上げ。
- **非同期I/Oリファクタリング**:
  - 同期通信ライブラリ `requests` の依存を排除し、非同期の `httpx` (`httpx.AsyncClient`) に置き換え。
  - アプリケーション起動時に `lifespan` イベントで HTTPX クライアントを1つ初期化し、リクエスト間でコネクションプールを共有するように最適化。
- **ディレクトリ構成のリネーム**:
  - 複数エンジン対応に伴い、ソースコードディレクトリ名を `voicevox_tts_api` から `tts_api` へ変更。
  - Dockerfile、docker-compose、ドキュメント類のパス指定も同期して変更。
- **コード品質 (Lint) 改善**:
  - `ruff check` で指摘された未使用インポート（`sys`, `os`）をクリーンアップ。
  - `__init__.py` におけるスキーマとルーターのインポートについて、明示的なリエクスポート (`as` 記法および `__all__` の定義) を導入。

---

## [0.1.0] - 2026-07-11

### 追加
- **初期フォーク版のリリース**:
  - VOICEVOX エンジンを OpenAI 互換の API フォーマットで動作させる API サーバーの初期実装。
  - FastAPI を用いたシンプルなルーティングと、Pydantic v1 を用いたリクエスト・レスポンススキーマの定義。
  - `voice_mappings.json` による OpenAI 標準の音声名から VOICEVOX スピーカーIDへのマッピング。
  - Docker / Docker Compose による起動設定のサポート。
