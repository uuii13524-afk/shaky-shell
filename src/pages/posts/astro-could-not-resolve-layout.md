---
title: 'Astro 6でmarkdown記事のlayoutパスを1階層間違えて出た「Could not resolve」エラーの原因と解決手順'
date: '2026-09-20'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'src/pages/posts配下のMarkdown記事でfrontmatterのlayoutパスを1階層浅く書くと、astro buildが「Could not resolve」で失敗する症状を解説します。相対パスの階層の数え方と、記事を量産する際に同じミスを再発させないための確認手順を紹介します。'
ja_tags: ['Astro', 'ビルドエラー', 'Could not resolve']
en_tags: ['Astro', 'build error', 'Could not resolve']
---

## やりたかったこと（症状）

このサイト（errsolved.com）はAstroのMarkdownページで記事を管理しており、新しい記事は既存の記事ファイルをコピーしてfrontmatterを書き換える形で作っている。この日もいつも通り`src/pages/posts/`配下に新しい`.md`ファイルを作り、既存記事のfrontmatterを流用して書き換えた上で、`npm run build`を実行した。

```bash
npm run build
```

ところが、いつもは数百ページがずらずらとビルドされていくはずのログが途中で止まり、以下のエラーで終了した。

```text
00:04:06 [types] Generated 148ms
00:04:06 [build] output: "static"
00:04:06 [build] mode: "static"
00:04:06 [build] directory: /home/user/shaky-shell/dist/
00:04:06 [build] Collecting build info...
00:04:06 [build] ✓ Completed in 228ms.
00:04:06 [build] Building static entrypoints...
00:04:11 [ERROR] [vite] ✗ Build failed in 4.87s
Could not resolve "../layouts/PostLayout.astro" from "src/pages/posts/zzz-test-layout-error.md"
file: /home/user/shaky-shell/src/pages/posts/zzz-test-layout-error.md
  Stack trace:
    at getRollupError (file:///home/user/shaky-shell/node_modules/rollup/dist/es/shared/parseAst.js:406:41)
    at ModuleLoader.handleInvalidResolvedId (file:///home/user/shaky-shell/node_modules/rollup/dist/es/shared/node-entry.js:22127:24)
```

`file:`の行に、まさに自分がいま編集していたファイルのパスが出ている。他の127記事は問題なくビルドできていたので、新規追加したファイルのどこかに原因があるのは明らかだった。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: v6.3.5（`package.json`の`astro: ^6.3.5`をそのままインストール）
- ビルドコマンド: `npm run build`（内部で`astro build && npx pagefind --site dist`を実行）
- 記事の配置: `src/pages/posts/<slug>.md`（日本語版）、`src/pages/en/<slug>.md`（英語版）、共通レイアウトは`src/layouts/PostLayout.astro`と`src/layouts/PostLayoutEn.astro`

## 試したこと

最初はエラーメッセージの`Could not resolve "../layouts/PostLayout.astro"`だけを見て、「レイアウトファイル自体が壊れているのでは」と疑い、`src/layouts/PostLayout.astro`の中身を開いて確認した。しかしファイルは存在しており、他の記事からは正常に読み込まれている。ここでレイアウト側ではなく、参照元である新規記事のfrontmatterを見直すべきだと気づいた。

新規記事のfrontmatterを確認すると、以下のようになっていた。

```yaml
---
title: 'test'
date: '2026-09-20'
category: 'Astro'
layout: '../layouts/PostLayout.astro'
description: 'test'
ja_tags: ['Astro']
en_tags: ['Astro']
---
```

`layout`の値が`../layouts/PostLayout.astro`になっている。一方、既存記事を`cat`で確認すると、こちらは`../../layouts/PostLayout.astro`と`../`が2つ連続していた。

```bash
grep "^layout:" src/pages/posts/docker-permission-denied.md
```

```text
layout: '../../layouts/PostLayout.astro'
```

見比べて初めて、コピー元にしたテキストの階層と、実際に保存したファイルの階層がずれていたことに気づいた。急いで手作業でコピー＆ペーストした際に、途中で`../`を1つ削ってしまっていたようだった。

## 原因

Astroのmarkdownページの`layout` frontmatterは、そのMarkdownファイル自身の場所を起点にした相対パスとして解決される。このサイトの記事ファイルは`src/pages/posts/<slug>.md`に置かれており、レイアウトは`src/layouts/PostLayout.astro`にある。ディレクトリを1段ずつ数えると次のようになる。

- `src/pages/posts/<slug>.md`から見て、1つ上の`../`は`src/pages/`
- さらにもう1つ上の`../../`で初めて`src/`に到達する
- そこから`layouts/PostLayout.astro`を辿って`src/layouts/PostLayout.astro`に届く

つまり`src/pages/posts/`から`src/layouts/`までは2階層上がる必要があり、正しい相対パスは`../../layouts/PostLayout.astro`になる。今回のミスは`../`を1つしか書いていなかったため、Viteが解決しようとした先は存在しない`src/pages/layouts/PostLayout.astro`になっていた。ファイルが存在しないパスを指しているため、ビルド時にRollup（Astroが内部で使っているバンドラ）が`Could not resolve`エラーを出して停止する。

厄介なのは、このエラーが**該当ファイルの構文チェックの時点では検出されない**という点だった。frontmatterのYAML自体は文法的に正しいため、`astro check`のような型チェックは通ってしまう場合がある。実際にエラーとして表面化するのは、Viteがそのページを実際にビルドしようとして`layout`のインポートを解決しにいくタイミングであり、`npm run build`を最後まで走らせて初めて気づく形になる。

## 解決手順

### 1. エラーメッセージの`file:`行で対象ファイルを特定する

```text
file: /home/user/shaky-shell/src/pages/posts/zzz-test-layout-error.md
```

Astroのビルドエラーには対象ファイルの絶対パスが必ず出力される。まずここで「どのファイルが悪いか」を確定させる。

### 2. 該当ファイルのfrontmatterの`layout`を確認する

```bash
grep "^layout:" src/pages/posts/zzz-test-layout-error.md
```

```text
layout: '../layouts/PostLayout.astro'
```

### 3. 正しい記事から相対パスをコピーする

自分で階層を数え直すより、既存の同じ深さの記事から`layout`の行をそのままコピーするほうが確実だった。

```bash
grep "^layout:" src/pages/posts/docker-permission-denied.md
```

```text
layout: '../../layouts/PostLayout.astro'
```

### 4. 誤ったパスを修正する

```yaml
layout: '../../layouts/PostLayout.astro'
```

### 5. ビルドし直す

```bash
npm run build
```

```text
00:04:22   ├─ /posts/xserver-cloudflare-full-setup/index.html (+3ms) 
00:04:22   ├─ /posts/xserver-cloudflare-nameserver/index.html (+2ms) 
00:04:22   ├─ /posts/zzz-test-layout-error/index.html (+2ms) 
00:04:22   ├─ /privacy/index.html (+1ms) 
00:04:22   ├─ /rss.xml (+30ms) 
00:04:22   ├─ /index.html (+6ms) 
00:04:22 ✓ Completed in 748ms.

00:04:22 [build] ✓ Completed in 6.35s.
00:04:22 [@astrojs/sitemap] `sitemap-index.xml` created at `dist`
00:04:22 [build] 268 page(s) built in 6.51s
00:04:22 [build] Complete!
```

エラーが消え、対象ページを含む全ページが最後までビルドされた。

## 動作確認

`dist/posts/`配下に対象記事の`index.html`が生成されていることと、`npm run preview`でローカルにプレビューして実際にレイアウト（ヘッダー・カテゴリ表示・言語切り替えリンクなど）が正しく表示されることを確認した。

```bash
ls dist/posts/ | grep zzz-test-layout-error
```

```text
zzz-test-layout-error
```

ディレクトリが生成されており、`trailingSlash: 'always'`と`build: { format: 'directory' }`の設定通り、`index.html`を含むディレクトリ形式で出力されていることも合わせて確認できた。

## まとめ

- Markdownの`layout` frontmatterは、そのファイル自身の場所からの相対パスとして解決される。`src/pages/posts/<slug>.md`から`src/layouts/`までは2階層（`../../`）上がる必要がある。
- `../`の数を1つ間違えるだけで、存在しないパスを参照することになり、`astro build`実行時にRollupの`Could not resolve`で失敗する。frontmatterのYAML構文自体は正しいため、目視だけでは気づきにくい。
- 手作業でfrontmatterをコピー＆ペーストするより、同じディレクトリ階層にある既存記事から`layout`の行をそのままコピーするほうが安全。JP/EN記事を並行して量産する運用では、このパス階層のミスが最後の`npm run build`まで検出されないため、記事を追加するたびにローカルで一度ビルドを通してから`git push`する習慣が事故防止になる。

## よくある質問

**Q: `astro dev`（開発サーバー）では気づけませんか？**
`astro dev`でも該当ページにアクセスした際に同様のエラーが表示されるが、対象ページを開かない限り気づけない。記事数が100本を超えるサイトでは、1ページずつ手動で確認するより`npm run build`を通して全ページを一括検証するほうが確実。

**Q: `layout`のパスをfrontmatterに書かず、共通化する方法はありますか？**
Astroのcontent collections機能を使えばschemaでlayoutを一元管理できるが、このサイトはMarkdownページ（`src/pages/`配下）方式を採用しているため、記事ごとにfrontmatterで`layout`を指定する必要がある。パスの数え間違いを防ぐ簡易策としては、新規記事作成時に必ず同階層の既存記事をコピー元にし、`title`や`description`などの中身だけを書き換える運用が有効。

**Q: 英語版記事（`src/pages/en/`）でも同じ階層数になりますか？**
なる。`src/pages/en/<slug>.md`も`src/pages/posts/<slug>.md`と同じ深さ（`src/pages/`の直下の1階層）にあるため、`layout`は同様に`../../layouts/PostLayoutEn.astro`のように`../`を2つ書く必要がある。

## 関連記事

- [Astroで新しいページを追加する方法](/posts/astro-add-page)
- [AstroのMarkdownでスタイルを当てる方法](/posts/astro-markdown-styles)
- [AstroでSEO用のmetaタグを設定する方法](/posts/astro-seo-meta-tags)
- [Cloudflare Pagesのビルドログを確認する方法](/posts/cloudflare-pages-build-log)
