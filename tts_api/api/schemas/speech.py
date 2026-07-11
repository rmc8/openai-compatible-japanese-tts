from pydantic import BaseModel


class SpeechRequest(BaseModel):
    """
    OpenAI TTS API互換のリクエストモデル

    Attributes:
        model: 使用するモデル（"voicevox-v1", "openjtalk-v1", "piper-v1"）
        input: 読み上げるテキスト
        voice: 音声指定
               - voicevox-v1: 音声名（"alloy", "ash" など）またはスピーカーID（例: "4"）
               - openjtalk-v1: "default"
               - piper-v1: "kokoro"
        response_format: 出力フォーマット（"mp3" または "wav"。デフォルトは "mp3"）
        speed: 読み上げ速度（デフォルト: 1.0）
    """

    model: str
    input: str
    voice: str
    response_format: str = "mp3"
    speed: float = 1.0
