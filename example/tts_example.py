import sys
from pathlib import Path

from loguru import logger
from openai import OpenAI

# ログの設定
logger.remove()  # デフォルトのハンドラを削除
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "issue_creator.log",
    rotation="500 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

# カスタムベースURLを持つOpenAIクライアントを作成（OpenAI SDK v1では末尾の/v1が必要です）
client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-1234")


def main():
    # 音声ファイルの保存パス
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    logger.info(f"出力ディレクトリを確認: {output_dir}")

    # 各エンジンのテストケース
    test_cases = [
        {
            "model": "piper-v1",
            "voice": "kokoro",
            "text": "こんにちは。パイパーでの音声合成テストです。",
            "description": "Piper (軽量・高品質)",
        },
        {
            "model": "openjtalk-v1",
            "voice": "default",
            "text": "こんにちは。オープンジェイトークでの音声合成テストです。",
            "description": "Open JTalk (超軽量・スタンドアロン)",
        },
        {
            "model": "voicevox-v1",
            "voice": "alloy",
            "text": "こんにちは。ボイスボックスでの音声合成テストです。",
            "description": "VOICEVOX (高品質キャラクター音声 - 要コンテナ)",
        },
        {
            "model": "piper-v1",
            "voice": "kokoro",
            "text": "スピードを変えて話すテストです。",
            "speed": 1.5,
            "description": "Piperでの高速読み上げ",
        },
    ]

    logger.info("OpenAI TTS互換マルチエンジンテストを開始")
    logger.debug("テストケース数: {}", len(test_cases))

    for i, test in enumerate(test_cases, 1):
        logger.info("テストケース {}: {}", i, test["description"])
        logger.debug(
            "テストパラメータ - モデル: {}, 話者: {}, テキスト: {}", 
            test["model"], test["voice"], test["text"]
        )
        if "speed" in test:
            logger.debug("速度パラメータ: {}", test["speed"])

        try:
            # 音声を生成
            response = client.audio.speech.create(
                model=test["model"],
                voice=test["voice"],
                input=test["text"],
                speed=test.get("speed", 1.0),
            )

            # ファイル名を生成
            speech_file_path = output_dir / f"test_{test['model']}_{i}.mp3"

            # 音声ファイルを保存
            with open(speech_file_path, "wb") as file:
                file.write(response.content)
            logger.success("音声ファイルを保存しました: {}", speech_file_path)

        except Exception as e:
            logger.error(
                "音声生成中にエラーが発生: {} - テストケース: {}", str(e), test
            )
            continue

    logger.info("全てのテストケースの処理が完了しました")


if __name__ == "__main__":
    main()
