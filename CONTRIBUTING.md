# 貢献ガイドライン 🌟

DocumentAnalyzerへの貢献を検討していただき、ありがとうございます！

## 貢献の方法

### バグ報告

1. 既存のIssueに同じ問題がないか確認してください
2. 新しいIssueを作成し、以下の情報を含めてください：
   - 問題の詳細な説明
   - 再現手順
   - 期待される動作
   - 実際の動作
   - 環境情報（OS、Pythonバージョンなど）

### 機能提案

1. 既存のIssueに同じ提案がないか確認してください
2. 新しいIssueを作成し、以下の情報を含めてください：
   - 提案する機能の説明
   - なぜその機能が必要か
   - 実装アイデア（あれば）

### プルリクエスト

1. このリポジトリをフォークします
2. 新しいブランチを作成します（`git checkout -b feature/amazing-feature`）
3. 変更を加えます
4. テストを実行し、すべてパスすることを確認します
5. コミットします（`git commit -m 'Add: すばらしい機能'`）
6. ブランチをプッシュします（`git push origin feature/amazing-feature`）
7. プルリクエストを作成します

## コーディング規約

- PEP 8に従ってください
- 関数とクラスにはdocstringを書いてください
- 型ヒントを使用してください
- テストを書いてください

## コミットメッセージ

以下の形式を使用してください：

```
<type>: <subject>

<body>

<footer>
```

タイプ：
- `Add:` 新機能追加
- `Fix:` バグ修正
- `Update:` 機能改善
- `Remove:` 機能削除
- `Docs:` ドキュメント変更
- `Test:` テスト追加・修正
- `Refactor:` リファクタリング

## 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/Kurasuai-Inc/document-analyzer.git
cd document-analyzer

# 仮想環境を作成
uv venv

# 依存関係をインストール
uv add click rich pathlib

# 開発用依存関係をインストール
uv add --dev pytest pytest-cov black ruff mypy
```

## テストの実行

```bash
# すべてのテストを実行
uv run pytest

# カバレッジ付きでテストを実行
uv run pytest --cov=doc_analyzer

# 特定のテストを実行
uv run pytest tests/test_specific.py
```

## 質問がある場合

DiscordまたはGitHub Discussionsで気軽に質問してください！

## 行動規範

すべての貢献者は、お互いを尊重し、建設的なコミュニケーションを心がけてください。

---

貢献してくださるみなさまに感謝します！🌟