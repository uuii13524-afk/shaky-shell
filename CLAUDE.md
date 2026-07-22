# SEO改善ルーティン指示（errsolved.com）

> Claude Code 用ルーティン。GSC「検索パフォーマンス（過去3か月・ウェブ）2026-07-22」の実データに基づく。
> 配置先の推奨: `.github/routines/seo-improvement-routine.md`
> 実行言語: 日本語（です・ます調）。コードは必ずバッククォート3つで囲む。

---

## 0. このルーティンの前提（現状スナップショット）

Claude Code はタスク開始時にこの数字を「解決すべき現状」として認識すること。

| 指標 | 値 | 意味 |
|---|---|---|
| 総表示 / 総クリック | 963 / 2（CTR 0.2%） | 見られているがクリックされない |
| 表示トレンド | 6月243 → 7月720 | インデックスは回復中 |
| 英語 `/en/` の表示シェア | 95.7% | 流入はほぼ海外・英語 |
| 日本語を含むクエリ | 247件中1件 | 日本語需要はほぼ未獲得 |
| 順位51位以下の表示 | 638 / 963 | 大半が6ページ目以降 |
| 上位10位のページ | 11（表示合計20） | 低価値ページ中心 |
| 重複URLを持つスラッグ | 約16 | 評価分散・低品質シグナル |

**根本課題**: ①流入言語（英語）と収益（日本語VPSアフィリエイト）の不一致、②URL正規化崩れ、③順位低迷、④ビッグワードでの正面衝突。

**実行順序は必ず Phase 0 → 4 の順**。Phase 0（技術）を放置したまま記事改善（Phase 2以降）をやっても効果が出ない。

---

## Phase 0.【最優先・ブロッカー】URL正規化を1本化する

同一コンテンツが `/en/slug`・`/en/slug/`・`/posts/slug/` の最大3URLでインデックスされている。1コンテンツ=1URLに統一する。

### 0-1. 正規URLルールを固定
- **正規形は「末尾スラッシュあり」**（errsolved.com は末尾スラッシュURLを配信）。
- 英語記事の正規は `/en/<slug>/`。旧 `/posts/<slug>/` は英語版へ301。
- GSC送信URLは必ず末尾スラッシュ付き（スラッシュ無しはリダイレクトエラーになる）。

### 0-2. Astro 設定で末尾スラッシュを強制
`astro.config.mjs` を確認し、無ければ追記する。

```js
export default defineConfig({
  site: 'https://errsolved.com',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
```

### 0-3. Cloudflare Pages の `_redirects` で旧パス・非正規を301
`public/_redirects` に追記（存在するスラッグのみ。存在しないパスのルールは作らない）。

```
# 旧 /posts/ を英語版へ集約（実在スラッグのみ列挙）
/posts/docker-exec-bash/            /en/docker-exec-bash/            301
/posts/docker-image-cleanup/        /en/docker-image-cleanup/        301
/posts/cloudflare-github-disconnect/ /en/cloudflare-github-disconnect/ 301
/posts/cloudflare-redirect-rules/   /en/cloudflare-redirect-rules/   301
/posts/node-version-management-nvm/ /en/node-version-management-nvm/ 301
/posts/github-issue-pullrequest     /en/github-issue-pullrequest/    301
/posts/xserver-cloudflare-full-setup/ /en/xserver-cloudflare-full-setup/ 301

# 末尾スラッシュ無し → あり（Astro/Pages側で吸収できない場合のみ）
/en/*  /en/:splat/  301
```

> 注意: `_redirects` のワイルドカードは既存の正しいURLをループさせないこと。デプロイ後に必ず 0-5 で検証する。

### 0-4. 自己参照canonicalを全ページに付与
共通レイアウト（`src/layouts/*.astro`）の `<head>` に、末尾スラッシュ付き絶対URLの canonical を出力する。

```astro
---
const canonical = new URL(Astro.url.pathname.replace(/\/?$/, '/'), Astro.site).href;
---
<link rel="canonical" href={canonical} />
```

### 0-5. デプロイ後の正規化監査（毎回実行）
以下を回し、旧URL・非スラッシュが 301 で正規URLへ飛ぶことを確認する。

```bash
cd C:\Users\acia\shaky-shell
# 例: 主要スラッグの応答コードを確認
for u in \
  https://errsolved.com/en/docker-exec-bash \
  https://errsolved.com/posts/docker-exec-bash/ \
  https://errsolved.com/en/docker-image-cleanup ; do
  echo "$u"; curl -sI "$u" | grep -Ei "^HTTP|^location"
done
```

**完了条件**: 非正規URLがすべて `301` で正規URL（末尾スラッシュ付き `/en/<slug>/`）へ集約され、`200` を返すのは正規URLのみ。

---

## Phase 1. 収益導線を「ページ言語」で分岐させる

**英語ページに日本語VPSアフィリエイトを貼らない。** 流入の96%は海外英語ユーザーで、ConoHa等は成約しない。むしろCTRを下げる。

### 1-1. `add_affiliate_links.py` に言語分岐を追加
`.github/scripts/add_affiliate_links.py` の注入ロジックを、対象ファイルのパスで分岐する。

- パスに `/en/` を含む → **グローバル案件ブロック**（AWIN: Cloudways / Cherry Servers）＋（承認後）AdSense枠。
- それ以外（日本語ページ）→ 従来の DOMAIN → VPS → LEARNING 優先順の日本語ブロック。

疑似ロジック:

```python
def pick_block(md_path: str, slug_type: str) -> str:
    if "/en/" in md_path.replace("\\", "/"):
        return EN_GLOBAL_BLOCK   # Cloudways / Cherry Servers (AWIN)
    return jp_block_by_priority(slug_type)  # DOMAIN > VPS > LEARNING > DEFAULT
```

> 既存の日本語ブロック（プロライター思考力講座 `4B3VRB+6M5ER6+4XF8+5ZEMQ` / Winスクール `4B3VRB+7N2A9E+529E+5YJRM` 等）は**日本語ページ専用**として維持。英語ページからは除外する。

### 1-2. AdSense枠の準備（承認回復後に有効化）
インデックス回復後の再申請を見据え、英語ページ側に広告枠のプレースホルダのみ用意しておく（承認前は非表示）。実装は承認後にコメントアウト解除する方針。

### 1-3. 収益ページの棚卸し
英語ページの末尾アフィリエイト差し替え後、`affiliate_links.md` に「言語別・案件別」の一覧を更新する。

**完了条件**: 英語ページに日本語VPSリンクが1件も残っていない。`grep` で確認する。

```bash
cd C:\Users\acia\shaky-shell
grep -rl "a8.net" src/pages/en/ || echo "OK: 英語ページに日本語A8リンクなし"
```

---

## Phase 2. 「勝てるクエリ」に集中する（コンテンツ方針）

ビッグワード（`docker build` 順位80 等）は捨て、**具体的エラー・具体的手順の長尾**に振り切る。実データで上位に来ているのはこの型。

### 2-1. 狙う型（GOOD）
- 具体的なエラーメッセージ全文（例: `error grabbing logs: invalid character 'l' after object key:value pair`）
- 「A × B の組み合わせ手順」（例: `xserver-cloudflare-full-setup` 順位10.8）
- サービス固有の詰まりどころ（例: `cloudflare-github-disconnect` 順位13.8＝唯一クリック獲得）
- 自作ツール系（`cron-checker` 順位6.6 等）

### 2-2. 避ける型（BAD）
- 単体ビッグワード（`docker build` / `docker exec` / `permission denied` / `nginx location`）を主題にしない。既存記事のタイトルがこれらのままなら、より具体的なエラー主題へリライトする。

### 2-3. 既存記事の優先リライト順（表示があり惜しい順）
表示が付いているのに沈んでいるページから着手する。上位候補:

1. `/en/docker-image-cleanup/`（表示81・順位76）
2. `/en/cloudflare-redirect-rules/`（表示69・順位55）
3. `/en/node-version-management-nvm/`（表示57・順位79）
4. `/en/windows-git-install/`（表示56・順位70）
5. `/en/nginx-location-directives/`（表示52・順位60）

各記事はより具体的なエラー・失敗シナリオへ寄せ、タイトルH1もそれに合わせて書き換える。

> 補足: 日本語での収益を本気で取りにいくなら、別軸で「日本語の具体的エラー記事」を新規に育てる必要があります（現状の日本語流入はほぼゼロ）。ただし新規は**インデックス回復が確認できるまで着手しない**（品質回復フェーズの原則を維持）。

---

## Phase 3. タイトル・メタでCTRを取り切る

順位が2ページ目以内に入ったページから、CTR最適化を行う（順位が来る前のメタ改善は効果が薄いので後回し）。

- **title**: `<具体的エラー/症状> の原因と解決手順` の形。数字・年・環境を含める（例: `2026` / `Ubuntu 24.04` / `Docker Compose`）。
- **description**: 120〜160字。1文目で「何が起きているか」、2文目で「本記事で解決できること」を明示。
- H1とtitleを一致させる。クリックされない汎用タイトルは廃止。

### frontmatter（SEO項目）
既存必須4項目 `title / date / category / layout` に加え、**SEO上は `description` と（自己参照）`canonical` を持たせることを強く推奨**します。

```yaml
---
title: "<具体的なエラー主題>"
date: 2026-07-22
category: Docker        # Git / Linux / Docker / Node.js / Cloudflare / Astro
layout: ../../layouts/Post.astro
description: "<120-160字。症状→解決の要約>"   # SEO推奨
---
```

> メモとの差分メモ: 今回いただいた仕様では必須frontmatterは4項目ですが、過去の作業では6項目版も存在していました。**どちらを正とするかを確定**し、`CLAUDE.md` に一本化してください（混在はビルド事故のもと）。

---

## Phase 4. 内部リンクと計測

- 関連記事同士を最低3本、文中リンクで相互接続（孤立ページを作らない）。
- `sitemap.xml` に正規URL（末尾スラッシュ付き）のみが載っているか確認。旧 `/posts/` を除外。
- リライト・正規化の効果は**GSCの「表示回数」ではなく「平均順位の改善」で判定**する（クリックは順位が上がってから遅れて付く）。

---

## 記事リライト時 SEOセルフチェック（10項目）

リライト完了後、以下を全て満たすまで納品しない。

1. 正規URLは `/en/<slug>/`（末尾スラッシュ）で、canonicalが自己参照になっている。
2. title・H1・descriptionが具体的エラー主題で一致している。
3. ビッグワード単体をタイトル主題にしていない。
4. 英語ページに日本語VPSアフィリエイトが混入していない。
5. 収益ブロックが言語に応じて正しく分岐している。
6. エラーメッセージ・コマンドを捏造していない（検証済み・実体験ベースのみ）。
7. 関連内部リンクが3本以上ある。
8. コードブロックはバッククォート3つで囲まれている。
9. frontmatterの項目順・必須項目が `CLAUDE.md` 準拠。
10. アフィリエイトセクションとfrontmatterを破壊していない。

---

## GSC運用ルール

- 送信は **1日5件まで**。送信URLは必ず**末尾スラッシュ付きの正規URL**。
- 送信前に `index_progress.md` を照合し、重複送信を避ける。
- 送信優先順: **正規化・リライト済みの既存記事 > 新規記事**。
- 「インデックス登録済み(17)／未登録」の区分移動は、Acia が登録を明示確認したときのみ行う。
- 効果測定は**リライトから2〜4週間後**の平均順位で判定。

---

## 禁止事項

- Phase 0（正規化）未完了のまま新規記事を公開しない。
- エラーメッセージ・コマンド・ログの捏造。
- `git add .`（ファイル単位で明示ステージング）。
- push前の `git pull origin main --rebase` 省略（Routinesと競合するため必須）。
- 英語ページへの日本語VPSアフィリエイト再混入。
- インデックス回復未確認での AdSense 再申請・新規大量投入。

---

## 今日から着手する具体手順（コピペ用）

```bash
cd C:\Users\acia\shaky-shell
git pull origin main --rebase

# 1) 正規化: astro.config.mjs に trailingSlash: 'always' を確認/追記
# 2) public/_redirects に旧 /posts/ の301を追記（実在スラッグのみ）
# 3) レイアウトへ自己参照canonicalを追加
# 4) add_affiliate_links.py に /en/ 言語分岐を追加

git add astro.config.mjs public/_redirects src/layouts/Post.astro .github/scripts/add_affiliate_links.py
git commit -m "seo: canonicalize URLs (trailing-slash), 301 legacy /posts/, split affiliate blocks by language"
git pull origin main --rebase
git push origin main
```

デプロイ完了後、Phase 0-5 の正規化監査 `curl -sI` を実行し、301集約を確認して完了とする。
