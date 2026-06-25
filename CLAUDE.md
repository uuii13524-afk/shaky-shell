# ErrNotes 記事自動生成ルール

## プロジェクト概要

- サイト: https://errsolved.com
- 技術スタック: Astro + GitHub + Cloudflare Pages
- リポジトリ: uuii13524-afk/shaky-shell
- 目的: アフィリエイト収益（月50万円目標）

---

## 【最重要ルール】日本語と英語は必ず同数・同内容

日本語記事を1本作ったら、必ず英語版も1本作る。  
英語記事を1本作ったら、必ず日本語版も1本作る。  
**片方だけ作ることは絶対にしない。**

作業後に必ずカウントを確認する:
```bash
ls src/pages/posts/*.md | wc -l
ls src/pages/en/*.md | wc -l
# 2つの数が一致していること
```

---

## ファイル配置

| 言語 | ディレクトリ | レイアウト |
|------|-------------|-----------|
| 日本語 | `src/pages/posts/` | `../../layouts/PostLayout.astro` |
| 英語 | `src/pages/en/` | `../../layouts/PostLayoutEn.astro` |

ファイル名はスラッグ（英小文字・ハイフン区切り）。JA/ENで同じスラッグを使う。

例: `docker-exec-bash.md` → 両方に同名ファイルを作成

---

## frontmatter 必須フィールド

### 日本語記事

```yaml
---
title: '記事タイトル（日本語）'
date: 'YYYY-MM-DD'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['タグ1', 'タグ2', 'タグ3']
description: '120文字以内の説明文。ターゲットキーワードを含める。'
---
```

### 英語記事

```yaml
---
title: 'Article Title in English'
date: 'YYYY-MM-DD'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['tag1', 'tag2', 'tag3']
description: 'Under 160 chars. Include target keyword naturally.'
---
```

**注意:**
- `layout` パスの間違いが最も多いミス。必ず `../../layouts/` から始めること
- `description` は省略しない（インデックスページで表示される）
- `date` は当日の日付を入れる

カテゴリの選択肢: `Git` / `Linux` / `Docker` / `Node.js` / `Cloudflare` / `Astro`

---

## 記事の構成（SEOに直結）

### 日本語記事の構成

```markdown
## ひとことで言うと

（最重要コマンドや解決策を3行以内のコードブロックで。フィーチャードスニペット狙い）

---

## やりたかったこと / 現象

（読者が検索した状況を再現する導入）

---

## 環境

（OS・ツールバージョン等）

---

## 解決策

（手順を段階的に、コードブロックを多用）

---

## よくあるエラーと対処

（エラーメッセージごとに見出しを立てる）

---

## よくある質問

（Q&A形式・4〜6問。Googleの「よくある質問」リッチリザルト狙い）

**Q: 質問文**
回答文。

---

## 関連記事

- [関連記事タイトル](/posts/slug)

## おすすめVPS／ドメイン

（アフィリエイトリンク）
```

### 英語記事の構成

```markdown
## Quick Answer

（Key command or solution in a code block）

---

## What You're Trying to Do

---

## Solution

---

## Common Errors

---

## FAQ

**Q: Question here?**
Answer here.

---

## Related Articles

## Recommended VPS / Hosting

（Affiliate links）
```

---

## アフィリエイトリンク

### 日本語記事（A8.net）

**VPS・サーバー系記事の末尾に使用:**
```html
## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
```

**ドメイン系記事の末尾に使用:**
```html
## ドメイン取得はこちら

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
```

### 英語記事（AWIN）

英語記事にも同カテゴリに対応するAWINリンクを追加する。現在リンクが未確定の場合は日本語と同じA8リンクをそのまま流用してよい。

---

## インデックスへの登録

**手動登録は不要。** インデックスページは `import.meta.glob('./*.md', { eager: true })` で自動収集している。ファイルを正しいディレクトリに置けば自動的に一覧に表示される。

確認したい場合:
```bash
# ローカルビルドして確認
npm run build
npm run preview
```

---

## git 操作

```bash
# 新記事2本（JA + EN）を追加した後
git add src/pages/posts/NEW-SLUG.md src/pages/en/NEW-SLUG.md
git commit -m "feat: add NEW-SLUG article (JA + EN)"
git push origin main
```

### git がロックで失敗する場合

```bash
# ロックファイルを確認・削除
find .git -name "*.lock"
rm .git/index.lock          # 存在する場合
rm .git/objects/maintenance.lock  # 存在する場合
```

---

## 過去に起きたミスと対策

| ミス | 原因 | 対策 |
|------|------|------|
| layoutパスが間違っていた | `Layout.astro` を指定（正: `PostLayout.astro`） | 毎回 `../../layouts/PostLayout.astro` を確認 |
| タイトルに全角スペースや文字化けが入った | コピペミス | 作成後に `head -5` でfrontmatterを確認 |
| JA記事だけ作ってEN忘れ | 作業途中で中断 | 作成後に `wc -l` でカウントを必ず確認 |
| descriptionを省略した | 任意フィールドと思っていた | インデックスページで空白になるので必須 |
| git pushがリジェクトされた | リモートが先行していた | `git pull --rebase origin main` してから push |
| layoutに `en_tags` なし | frontmatterコピペ漏れ | EN記事は `en_tags` を必ず含める |

---

## 記事テーマの選び方

優先度順:
1. GSCで「表示回数は多いがCTR低い」キーワード（position 4〜15が狙い目）
2. 既存記事で扱っていない関連コマンド・エラー
3. `src/pages/posts/` に既存記事があるが `src/pages/en/` に対応がないもの（逆も同様）

カテゴリ別の記事例:
- Docker: `docker logs`, `docker network`, `docker volume`, `docker-compose down`
- Linux: `grep -r`, `chmod`, `find`, `curl`, `systemctl`
- Git: `git stash`, `git cherry-pick`, `git bisect`, `git tag`
- Cloudflare: Workers, R2, KV, Pages Functions
- Node.js: `npm audit`, `nvm`, `package.json scripts`
- Astro: コンポーネント, SSR, Image最適化

---

## 毎日の自動実行タスク（Claude Code用プロンプト）

```
あなたはerrsolved.com（Astroアフィリエイトブログ）の記事生成AIです。
CLAUDE.mdのルールをすべて読んでから作業を開始してください。

本日のタスク:
1. src/pages/posts/ と src/pages/en/ のファイル数が一致しているか確認する
2. 不足しているペアがあれば対応する英語または日本語記事を先に作成する
3. 新規記事を1ペア（日本語1本 + 英語1本）作成する
   - テーマ: GSCで流入が見込めるDockerまたはLinux系のコマンド・エラー記事
   - CLAUDE.mdの構成・frontmatter・アフィリエイトリンクルールに従う
4. 作成後にカウントを確認し、JA/ENが同数であることを検証する
5. git add, git commit, git push する

禁止事項:
- descriptionの省略
- layoutパスの省略・誤記
- JA/ENどちらか片方だけの作成
- 既存記事と同じスラッグの使用（ls src/pages/posts/ で確認）
```
