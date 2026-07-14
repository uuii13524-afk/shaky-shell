# CLAUDE.md — errsolved.com 記事作成ルール

## 1. プロジェクト基本情報

- サイト: https://errsolved.com（アフィリエイトブログ）
- 技術スタック: Astro + GitHub + Cloudflare Pages
- リポジトリ: uuii13524-afk/shaky-shell
- 目標: アフィリエイト収益で月50万円
- 現フェーズ: 品質回復フェーズ（リライト優先・新規は品質基準クリアが条件）

## 2. 記事ファイルのフォーマット

### 配置場所
- 日本語: `src/pages/posts/[slug].md`
- 英語: `src/pages/en/[slug].md`
- JA/ENペアはslugを共通にする

### frontmatter（必須6項目）

```yaml
---
title: '記事タイトル'
date: 'YYYY-MM-DD'
category: 'カテゴリ名'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['タグ1', 'タグ2', 'タグ3']
en_tags: ['tag1', 'tag2', 'tag3']
---
```

- カテゴリ: Git / Linux / Docker / Node.js / Cloudflare / Astro / Windows / nginx / GitHub Actions
- 内部リンクは必ず末尾スラッシュなしの `/posts/slug` 形式（astro.config.mjsの trailingSlash: 'always' がビルド時に処理する）

## 3. 記事品質基準（新規・リライト共通、全項目必須）

1. **一人称の体験談で書く。** 「やりたかったこと」から始め、実際に遭遇した状況として書く
2. **エラーメッセージ・コマンド出力を実物で載せる。** 抽象的な説明で済ませない
3. **失敗談を最低1つ含める。** 「最初〜を試したが直らなかった」という試行錯誤の過程
4. **「なぜそうなるのか」の理由説明を含める。** 手順の羅列だけの記事は禁止
5. **文字数: 日本語記事は本文2,000字以上**（コードブロック除く）。既存の薄い記事の1.5倍以上が目安
6. **構成テンプレート:**
   - やりたかったこと / 症状
   - 環境
   - 試したこと（失敗含む）
   - 原因
   - 解決方法（コマンド・コード付き）
   - ハマったポイント
   - 関連記事（4〜5本、実在するslugのみ）
7. **コードブロックは必ずバッククォート3つ + 言語指定**（```bash など）
8. **関連記事リンクは実在確認必須。** src/pages/posts/ に存在しないslugへのリンク禁止

## 4. アフィリエイトリンク

**記事内には手動で貼らない。** `.github/scripts/add_affiliate_links.py` が
slugのキーワードに基づき自動挿入する（優先順位: DOMAIN → VPS → LEARNING → DEFAULT）。

- 記事本文はアフィリエイトセクションなしで書き終える
- スクリプトが対象外と判断した場合のみ、DEFAULTブロック（VPS 3社）を手動で追加

## 5. Git運用

```bash
cd C:\Users\acia\shaky-shell
git pull origin main --rebase
git add .
git commit -m "add: [slug] (JA+EN)"
git push origin main
```

- push前に必ず `git pull origin main --rebase`（Routinesとの競合防止）
- 新規記事作成後、`index_progress.md` の「残り（次回以降）」の**最後尾**にURLを追記する（末尾スラッシュ付き形式: `https://errsolved.com/posts/slug/`）

## 6. GSCインデックス申請

- 1日5件まで（Google割当上限）
- **申請優先順位: リライト済み記事 → 既存未申請記事 → 新規記事**
- 申請URLは末尾スラッシュ付き
- index_progress.md の「申請済み」への移動は、GSCで登録確認できたもののみ

## 7. 出力言語・トーン

- 回答は日本語
- 日本語記事: です・ます調ベース、体験談部分は「〜だった」も可
- 英語記事: 直訳ではなく英語圏の検索者向けに自然な文章で書く
