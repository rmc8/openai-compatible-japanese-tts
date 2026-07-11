
from pathlib import Path
from loguru import logger
from openai import OpenAI


def main():
    """
    マルチエンジン（Open JTalk / Piper / VOICEVOX）の OpenAI TTS API フォーマットを使用した
    シンプルな音声合成のサンプルスクリプト
    """
    # 出力ディレクトリの自動作成
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # カスタムベースURLを持つOpenAIクライアントを作成
    client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-1234")

    # 音声合成のリクエストパラメータを設定（デフォルトは軽量で内蔵されている Piper）
    text = "こんにちは。マルチエンジン対応のOpenAI TTSフォーマットのテストです。"
    model = "piper-v1"
    voice_id = "kokoro"

    logger.info("音声合成を開始します")
    logger.debug(f"モデル: {model}")
    logger.debug(f"テキスト: {text}")
    logger.debug(f"話者: {voice_id}")

    try:
        # 音声を生成
        response = client.audio.speech.create(
            model=model, voice=voice_id, input=text
        )

        # 音声ファイルを保存
        output_file = output_dir / "simple_test.mp3"
        with open(output_file, "wb") as file:
            file.write(response.content)

        logger.success(f"音声ファイルを保存しました: {output_file}")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    main()
