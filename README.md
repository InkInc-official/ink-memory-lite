# 🖋️ Ink Memory Lite

**Ink Inc. presents**

> AI Creation, Human Care. The Future Drawn Together.

---

## これは何？

**Ink Memory Lite** は、配信者・ライバー個人向けの **活動ログ管理ツール**です。

日々の配信活動を記録し、CSVとして書き出して外部AI（Claude・ChatGPT・Gemini）に分析を依頼できます。

Ink Inc. が内部運用する「Ink Memory（Pro版）」の個人向け公開版として設計されています。

---

## 特徴

- **活動ログの記録** — 日付・タグ・本文でシンプルに記録
- **キーワード・タグ・日付によるフィルタ閲覧**
- **名鑑機能** — 配信者情報を1名登録（誕生日・記念日カウントダウン）
- **CSVエクスポート** — 期間指定でログを書き出し
- **外部AI向けプロンプト例文集** — ダウンロードしたCSVをAIに投げるための例文を収録
- **ダッシュボード** — 活動日数・記念日・ログ数をサイドバーに常時表示
- **AI機能なし** — APIキー不要・完全ローカル動作

---

## AIを搭載しない理由

本ツールはAI機能を持ちません。

かわりに、ユーザー自身がログをCSVで書き出し、  
Claude・ChatGPT・Gemini など使い慣れたAIに投げる運用を推奨します。

```
Ink Memory Lite でログを記録
    ↓
CSVエクスポート
    ↓
好きなAIにプロンプトごと貼り付けて分析
```

これにより、APIキー不要・LLM環境不要で、最高のAI分析が得られます。

---

## セットアップ

```bash
git clone <repository-url>
cd ink_memory_lite
pip install streamlit pandas
streamlit run main.py
```

### フォントについて

`fonts/ZenOldMincho-Regular.ttf` を配置することで明朝体で表示されます。  
フォントがない場合はシステムフォントで動作します。

[Google Fonts - Zen Old Mincho](https://fonts.google.com/specimen/Zen+Old+Mincho) からダウンロードしてください。

---

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python |
| フレームワーク | Streamlit |
| DB | SQLite（`~/.local/share/ink_memory_lite/`） |
| フォント | Zen Old Mincho |
| 外部API依存 | なし |

---

## Ink Memory Pro について

本ツールは **Ink Memory Lite**（個人向け・公開版）です。

Ink Inc. では複数ライバーの統合管理・AI分析を搭載した **Pro版**を内部運用しています。

👉 [Ink Inc. 公式サイト](https://inkinc-hp.vercel.app/)

---

## ライセンス

MIT License

© 2025-2026 Ink Inc.  
[https://inkinc-hp.vercel.app/](https://inkinc-hp.vercel.app/)
