FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# システム依存パッケージのインストール (pyopenjtalkのビルド用と音声変換用のffmpeg/curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Piperバイナリのダウンロードと配置
RUN arch=$(dpkg --print-architecture) && \
    if [ "$arch" = "amd64" ]; then \
        curl -L https://github.com/rhasspy/piper/releases/download/v1.0.0/piper_amd64.tar.gz -o piper.tar.gz; \
    elif [ "$arch" = "arm64" ]; then \
        curl -L https://github.com/rhasspy/piper/releases/download/v1.0.0/piper_arm64.tar.gz -o piper.tar.gz; \
    fi && \
    tar -xzf piper.tar.gz && \
    rm piper.tar.gz && \
    mv piper/piper /usr/local/bin/piper && \
    mv piper/lib* /usr/local/lib/ && \
    ldconfig

# Piper日本語モデルのダウンロード
RUN mkdir -p /app/models && \
    curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ja/ja_JP/kokoro/medium/ja_JP-kokoro-medium.onnx -o /app/models/ja_JP-kokoro-medium.onnx && \
    curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ja/ja_JP/kokoro/medium/ja_JP-kokoro-medium.onnx.json -o /app/models/ja_JP-kokoro-medium.onnx.json

COPY tts_api/pyproject.toml tts_api/uv.lock ./
RUN uv sync --frozen --no-install-project --no-cache

COPY tts_api/ .

# 新しいエントリーポイントを指定
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
