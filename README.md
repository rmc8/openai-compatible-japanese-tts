<div align="center">

![Image](https://github.com/user-attachments/assets/e47df212-9f09-4c43-8a66-ced8e1b1fb7c)

# 🎤 VOICEVOX / Open JTalk / Piper OpenAI TTS API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)

VOICEVOX、Open JTalk、および Piper の各音声合成エンジンを OpenAI の音声合成 API フォーマットで利用するための API サーバーです。

</div>

## 🌟 特徴

- **OpenAI 互換**: OpenAI の TTS API と同じフォーマットでリクエストを受け付けます。
- **マルチエンジン対応**: 
  - **VOICEVOX**: 高品質で多様なキャラクター音声（外部エンジンの呼び出し）
  - **Open JTalk**: 軽量かつスタンドアロンで動作するローカル日本語音声合成
  - **Piper**: VITSベースの非常に高速かつ自然なローカル日本語音声合成（`ja_JP-kokoro-medium` モデル同梱）
- **リアルタイム音声変換**: 生成された WAV 音声を、`ffmpeg` によりリアルタイムで MP3 にエンコードして返却可能。
- **モダンなパッケージ管理**: `uv` に完全対応し、コンテナイメージのビルドと起動が最適化されています。

## 🚀 使用方法

### 🐳 起動方法

```bash
docker compose build
docker compose up -d
```

### 📝 APIエンドポイント

```bash
POST http://localhost:8000/v1/audio/speech
```

### リクエスト形式（OpenAI互換）

```json
{
  "model": "piper-v1",
  "input": "こんにちは、音声合成のテストです。",
  "voice": "kokoro",
  "response_format": "mp3",
  "speed": 1.0
}
```

### パラメータ説明

- `model`: 使用する音声合成エンジン
  - `voicevox-v1` (または `voicevox`)
  - `openjtalk-v1` (または `openjtalk`)
  - `piper-v1` (または `piper`)
- `input`: 読み上げるテキスト（日本語）
- `voice`: 各モデルに合わせた音声の指定
  - `voicevox-v1`: 音声名（`alloy`, `ash`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`）またはスピーカーID（数値）
  - `openjtalk-v1`: `default`
  - `piper-v1`: `kokoro` (デフォルト)
- `response_format`: 出力フォーマット（`mp3` または `wav`。デフォルトは `mp3`）
- `speed`: 読み上げ速度（`0.5` 〜 `2.0`。デフォルトは `1.0`）

### レスポンス形式

- Content-Type: `audio/mpeg` (MP3時) または `audio/wav` (WAV時)
- Body: 各フォーマットの音声データ（バイナリ）

### Pythonでの使用例 (OpenAI SDK)

```python
from openai import OpenAI

# カスタムベースURLを持つOpenAIクライアントを作成
client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-1234")

# Piperエンジンを使って音声を生成
response = client.audio.speech.create(
    model="piper-v1",
    voice="kokoro",
    input="こんにちは、音声合成のテストです。",
    speed=1.0
)

# 音声ファイルを保存（ストリーミングレスポンスを使用）
with response.with_streaming_response.stream_to_file("output.mp3"):
    pass
```

## 📁 プロジェクト構造

```
.
├── docker-compose.yml       # Docker構成ファイル (CPU)
├── docker-compose.gpu.yml   # Docker構成ファイル (GPU)
├── Dockerfile               # APIサーバーのビルド設定 (uv/Piper/ffmpegビルド)
├── LICENSE                  # MIT ライセンスファイル
├── README.md                # 本ドキュメント
├── tts_api/                 # OpenAI互換APIの実装
│   ├── pyproject.toml       # uv依存パッケージ管理定義
│   ├── uv.lock              # uvパッケージロックファイル
│   ├── main.py              # アプリケーションのエントリーポイント
│   ├── voice_mappings.json  # VOICEVOX音声名とIDのマッピング
│   └── api/                 # APIルーターとスキーマ定義
│       ├── __init__.py      # アプリ初期化＆共有 AsyncClient 管理 (lifespan)
│       ├── routers/         # APIルーティング (chat, models, speech)
│       └── schemas/         # リクエスト・レスポンススキーマ
└── example/                 # 使用例とテストスクリプト
```

## 🔧 システム要件

- Docker
- Docker Compose

## 🔑 APIキー認証

サーバーレス・公開環境へのデプロイ時は、APIキー認証を設定することを強く推奨します。

環境変数 `API_KEY` を設定すると、すべてのリクエストで `Authorization: Bearer <APIキー>` ヘッダーの検証を行います。
設定しない場合は認証なし（ローカル開発モード）で動作します。

```bash
# docker-compose.yml に環境変数を追加する例
environment:
  - API_KEY=your_secret_api_key_here
```

クライアント側からは OpenAI SDK の `api_key` パラメータにそのまま設定できます：

```python
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your_secret_api_key_here",
)
```

設定例は [.env.example](.env.example) を参照してください。

## 🔒 ライセンス

### 1. プログラム本体のライセンス
本プロジェクト（APIサーバーのラッパーコード部分）は、**MITライセンス**の下で公開されています。詳細は [LICENSE](LICENSE) を参照してください。

### 2. 同梱および利用エンジン・音声モデルのライセンス
本プロジェクトで利用される各種エンジンおよび音声モデルは、それぞれ独自のライセンスに従って動作しています。利用の際はそれぞれの規約に留意してください。

- **VOICEVOX**: 
  - VOICEVOXエンジン本体は **LGPL v3** です。
  - 生成された音声の利用規約（キャラクターごとのクレジット表記など）は、VOICEVOXの公式利用規約に準拠します。
- **Open JTalk / pyopenjtalk**:
  - Open JTalkおよび `hts_engine API` は、**改変BSDライセンス (Modified BSD License)** です。
- **Piper**:
  - Piperエンジン本体は **GPL-3.0** (最新版) または **MIT License** でライセンスされています。本プロジェクトでは Piper を別プロセス（CLI）として呼び出しています。
  - 同梱されている日本語音声モデル `ja_JP-kokoro-medium` は、ライセンスの条件に従って利用する必要があります。

## 📝 変更履歴

これまでのすべての重要な変更履歴は、[CHANGELOG.md](CHANGELOG.md) を確認してください。

