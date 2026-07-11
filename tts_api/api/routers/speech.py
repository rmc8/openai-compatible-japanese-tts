import io
import json
import logging
import os
import subprocess
import wave

import httpx
import numpy as np
import pyopenjtalk
from fastapi import APIRouter, HTTPException, Request, Response

from ..schemas.speech import SpeechRequest

# ロガーの設定
logger = logging.getLogger("tts_api.speech")

router = APIRouter()

# voice_mappings.jsonの読み込み
VOICE_MAPPINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "voice_mappings.json"
)

# VOICEVOXエンジンのURL設定（環境変数から取得、デフォルトは docker-compose でのサービス名）
VOICEVOX_ENGINE_URL = os.getenv("VOICEVOX_ENGINE_URL", "http://voicevox_engine:50021")

# Piperの音声モデルパス（環境変数から取得、デフォルトは同梱パス）
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "/app/models/ja_JP-kokoro-medium.onnx")


def load_voice_mappings():
    """音声IDマッピングを読み込む"""
    try:
        with open(VOICE_MAPPINGS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load voice mappings: {e}")
        return {}


def get_speaker_id(voice: str) -> int:
    """
    音声名またはIDからスピーカーIDを取得

    Args:
        voice: 音声名または音声ID

    Returns:
        int: スピーカーID
    """
    mappings = load_voice_mappings()

    # マッピングに存在する場合はマッピングされたIDを返す
    if voice in mappings:
        return int(mappings[voice])

    # 直接数値が指定された場合はそのまま返す
    try:
        return int(voice)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice: {voice}. Available voices: {', '.join(mappings.keys())}",
        )


def generate_openjtalk_wav(text: str) -> bytes:
    """Open JTalkを用いた日本語音声合成（WAV出力）"""
    try:
        # pyopenjtalk.ttsの戻り値は float64 で、値の範囲は -32768.0〜32767.0
        data, sr = pyopenjtalk.tts(text)
        data = data.astype(np.int16)
    except Exception as e:
        logger.error(f"Open JTalk synthesis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Open JTalkでの音声合成に失敗しました: {str(e)}"
        )

    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sr)
        wav_file.writeframes(data.tobytes())

    return wav_io.getvalue()


def generate_piper_wav(text: str, speed: float = 1.0) -> bytes:
    """Piper CLIを用いた日本語音声合成（WAV出力）"""
    # 速度を安全な範囲（0.5〜2.0）に制限
    speed = max(0.5, min(2.0, speed))
    # Piperの--length_scaleは速度の逆数（1.0より小さいと早く、大きいと遅くなる）
    length_scale = 1.0 / speed

    if not os.path.exists(PIPER_MODEL_PATH):
        logger.error(f"Piper model not found at {PIPER_MODEL_PATH}")
        raise HTTPException(
            status_code=500, detail="Piper音声モデルがサーバー上に見つかりません。"
        )

    cmd = [
        "piper",
        "--model",
        PIPER_MODEL_PATH,
        "--output_file",
        "-",
        "--length_scale",
        str(length_scale),
    ]

    try:
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=text.encode("utf-8"), timeout=30.0)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise HTTPException(
            status_code=504, detail="Piper音声合成がタイムアウトしました。"
        )
    except Exception as e:
        logger.error(f"Failed to start Piper process: {e}")
        raise HTTPException(
            status_code=500, detail=f"Piperプロセスの起動に失敗しました: {str(e)}"
        )

    if process.returncode != 0:
        err_msg = stderr.decode("utf-8", errors="ignore")
        logger.error(
            f"Piper synthesis failed with code {process.returncode}: {err_msg}"
        )
        raise HTTPException(
            status_code=500, detail=f"Piper音声合成に失敗しました: {err_msg}"
        )

    return stdout


def convert_wav_to_mp3(wav_bytes: bytes) -> bytes:
    """ffmpegを使用したWAVからMP3への変換"""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "pipe:0",  # 標準入力からWAVを読み込む
        "-f",
        "mp3",  # 出力フォーマットはMP3
        "-acodec",
        "libmp3lame",  # MP3用エンコーダ
        "-ab",
        "128k",  # ビットレート 128kbps
        "pipe:1",  # 標準出力へ出力
    ]
    try:
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=wav_bytes, timeout=15.0)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise HTTPException(
            status_code=504, detail="音声のMP3変換処理がタイムアウトしました。"
        )
    except Exception as e:
        logger.error(f"Failed to start ffmpeg: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ffmpegの起動に失敗しました。サーバー環境を確認してください: {str(e)}",
        )

    if process.returncode != 0:
        err_msg = stderr.decode("utf-8", errors="ignore")
        logger.error(f"ffmpeg conversion failed: {err_msg}")
        raise HTTPException(
            status_code=500, detail=f"MP3フォーマットへの変換に失敗しました: {err_msg}"
        )

    return stdout


@router.post("/v1/audio/speech", summary="テキストを音声に変換")
async def create_speech(request: SpeechRequest, fastapi_request: Request):
    """
    テキストを音声に変換するエンドポイント（OpenAI TTS API互換）

    Args:
        request: 音声合成リクエスト
        fastapi_request: FastAPIリクエストオブジェクト

    Returns:
        Response: 音声データ（MP3またはWAV）
    """
    model_lower = request.model.lower()

    # 1. 各エンジンに応じたWAVデータの生成
    if "voicevox" in model_lower:
        audio_query_url = f"{VOICEVOX_ENGINE_URL}/audio_query"
        synthesis_url = f"{VOICEVOX_ENGINE_URL}/synthesis"
        speaker_id = get_speaker_id(request.voice)
        client = fastapi_request.app.state.http_client

        try:
            query_response = await client.post(
                audio_query_url,
                params={"text": request.input, "speaker": speaker_id},
                timeout=30.0,
            )
            query_response.raise_for_status()
            query_data = query_response.json()

            # VOICEVOX速度設定
            query_data["speedScale"] = request.speed

            synthesis_response = await client.post(
                synthesis_url,
                params={"speaker": speaker_id},
                json=query_data,
                timeout=60.0,
            )
            synthesis_response.raise_for_status()
            wav_data = synthesis_response.content

        except httpx.HTTPStatusError as e:
            logger.error(
                f"VOICEVOX engine returned error status: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"VOICEVOXエンジンがエラーを返しました: {e.response.text}",
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to communicate with VOICEVOX engine: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}",
            )

    elif "openjtalk" in model_lower:
        wav_data = generate_openjtalk_wav(request.input)

    elif "piper" in model_lower:
        wav_data = generate_piper_wav(request.input, request.speed)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"サポートされていないモデルです: {request.model}. 利用可能: voicevox-v1, openjtalk-v1, piper-v1",
        )

    # 2. フォーマット変換とレスポンス返却
    format_lower = request.response_format.lower()

    if format_lower == "mp3":
        mp3_data = convert_wav_to_mp3(wav_data)
        return Response(content=mp3_data, media_type="audio/mpeg")
    elif format_lower == "wav":
        return Response(content=wav_data, media_type="audio/wav")
    else:
        # デフォルトはMP3にフォールバック
        logger.warning(
            f"Unsupported format '{request.response_format}'. Falling back to MP3."
        )
        mp3_data = convert_wav_to_mp3(wav_data)
        return Response(content=mp3_data, media_type="audio/mpeg")
