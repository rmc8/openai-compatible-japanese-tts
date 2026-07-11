<div align="center">

![Image](https://github.com/user-attachments/assets/ff44711a-aa35-4d77-9ebb-e43216bda82f)

# 🎤 OpenAI TTS API フォーマットのマルチエンジンテスト例

</div>

このディレクトリには、VOICEVOX、Open JTalk、および Piper を OpenAI TTS フォーマットで利用するためのサンプルスクリプトが含まれています。

## 🚀 セットアップ

1. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

2. サービスの起動 (VOICEVOXを利用する場合のみ):
プロジェクトのルートディレクトリで以下のコマンドを実行：
```bash
docker compose up -d
```
※ Open JTalk および Piper は API サーバー単体（コンテナ内）でスタンドアロン動作するため、VOICEVOX コンテナを立ち上げなくてもテストが可能です。

## 📝 使用方法

### 🔍 シンプルな実装
基本的な機能を試す場合：
```bash
python simple_tts_example.py
```

このスクリプトは Piper を使った基本的な音声合成を実行し、`output/simple_test.mp3` に保存します。

### 🧪 詳細な実装
複数のテストケースを実行する場合：
```bash
python tts_example.py
```

このスクリプトは以下のテストケースを実行します：
1. 📢 Piper による標準設定での音声生成
2. 📢 Open JTalk による標準設定での音声生成
3. 📢 VOICEVOX による標準設定での音声生成（※VOICEVOXコンテナが起動している必要があります）
4. ⏩ Piper による高速読み上げテスト

生成された音声ファイルは `output` ディレクトリに保存されます。

## 🎯 カスタマイズ

### ⚙️ シンプルな実装（simple_tts_example.py）
以下の変数を編集することで、基本的な設定を変更できます：
- `model`: 使用するエンジン（`piper-v1`, `openjtalk-v1`, `voicevox-v1`）
- `text`: 読み上げるテキスト
- `voice_id`: 話者名またはID

### 🔧 詳細な実装（tts_example.py）
`test_cases` 配列を編集することで、異なるテキストや設定でテストを行うことができます。

設定可能なパラメータ：
- `model`: 使用するエンジン（`piper-v1`, `openjtalk-v1`, `voicevox-v1`）
- `text`: 読み上げるテキスト
- `voice`: 話者ID（例: `kokoro`, `default`, `alloy` など）
- `speed`: 読み上げ速度（1.0が標準）

## 📊 結果の確認

生成された音声ファイルは以下の場所に保存されます：

```
example/output/
├── simple_test.mp3              # simple_tts_example.pyの出力
├── test_piper-v1_1.mp3          # Piperでの標準テスト
├── test_openjtalk-v1_2.mp3      # Open JTalkでの標準テスト
├── test_voicevox-v1_3.mp3       # VOICEVOXでの標準テスト
└── test_piper-v1_4.mp3          # Piperでの高速読み上げテスト
```

## 🔍 トラブルシューティング

### ❓ 音声が生成されない場合
- エンドポイントURLが `http://localhost:8000/v1` に設定されているか確認してください（OpenAI SDK v1以降では末尾の `/v1` が必要です）。
- VOICEVOXモデル（`voicevox-v1`）を呼び出す場合は、VOICEVOXサービスが正常に起動しているか確認してください。
- ログおよびコンソールの出力、`issue_creator.log` を確認してください。

## 📚 参考リンク

- [VOICEVOXプロジェクト](https://voicevox.hiroshiba.jp/)
- [OpenAI TTS API ドキュメント](https://platform.openai.com/docs/api-reference/audio/createSpeech)

