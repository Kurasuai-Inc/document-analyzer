# DocumentAnalyzer 📊

Markdownドキュメント間のリンク関係を分析して、孤立したドキュメントを見つけるためのツールです。

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Powered by uv](https://img.shields.io/badge/Powered%20by-uv-brightgreen)](https://github.com/astral-sh/uv)

</div>

## 機能

- ワークスペース内のすべてのMarkdownファイルをスキャン
- ドキュメント間のリンク関係を抽出・分析
- 孤立したドキュメントの検出
- 統計情報の表示（総ドキュメント数、総リンク数など）
- 各ドキュメントの入力・出力リンク数の表示

## インストール

このツールはuv環境で動作します：

```bash
cd tools/doc-analyzer
uv venv
uv add click rich pathlib
```

## 使い方

### 直接実行

```bash
uv run python doc_analyzer.py --path /path/to/workspace
```

### tools.sh経由（推奨）

ワークスペースのルートから：

```bash
./tools.sh analyze-docs         # デフォルトでワークスペース全体を分析
./tools.sh analyze-docs -v       # 詳細情報付き
./tools.sh analyze-docs -p docs/ # 特定のディレクトリを分析
```

## 出力例

```
分析対象: /home/herring/agent-workspace/workspaces/neby

27個のドキュメントを発見

      ドキュメント統計       
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━┓
┃ 項目                 ┃ 数 ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━┩
│ 総ドキュメント数     │ 27 │
│ 総リンク数           │ 31 │
│ 孤立したドキュメント │  4 │
│ 入力リンクなし       │  6 │
│ 出力リンクなし       │ 20 │
└──────────────────────┴────┘

孤立したドキュメント:
  • docs/neby-character/communication.md
  • docs/project/investigation-plan.md
  • kurasu_ai_investigation_strategy.md
  • tools/doc-analyzer/README.md
```

## 技術詳細

- **言語**: Python 3.12+
- **依存関係**: Click (CLI), Rich (出力フォーマット)
- **パターンマッチング**: Markdownリンクパターン `[text](path.md)` を検出
- **除外**: 外部リンク、アンカーリンク、node_modules、.venvディレクトリ

## 今後の拡張予定

- [ ] グラフ形式でのリンク関係の可視化
- [ ] 双方向リンクのチェック
- [ ] 壊れたリンクの検出
- [ ] リンク密度の分析
- [ ] マークダウン以外のファイル形式対応

## 貢献

バグ報告や機能提案は、GitHubのIssuesまでお願いします。
プルリクエストも歓迎です！

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。
詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 作者

- 暮らすAI - セイラ（@seira_kurasuai）

## 謝辞

このツールは、ネビィのEvergreenNote方式に触発されて作成されました。
ドキュメント管理の重要性を教えてくれたチームメンバーに感謝します！