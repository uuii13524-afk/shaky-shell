---
title: 'Astroのfrontmatterでコロンを含む値がbad indentation of a mapping entryでbuild失敗する原因と解決手順'
date: '2026-08-31'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroの記事ページでdescriptionやtitleにコロン(:)を含む値をクォートせずに書くと、npm run buildがbad indentation of a mapping entryというYAML解析エラーで失敗する症状を解説。原因と、値をシングルクォートで囲んで解決する手順を紹介します。'
ja_tags: ['Astro', 'YAML', 'frontmatter', 'ビルドエラー']
en_tags: ['Astro', 'YAML', 'frontmatter', 'build error']
---

## やりたかったこと（症状）

このブログ自体がAstro製で、記事は`src/pages/posts/*.md`のMarkdownファイルとしてfrontmatterに`title`や`description`を書く形式になっている。新しい記事を書いていて、`description`にエラーメッセージをそのまま説明として書こうとした。

```yaml
---
title: 'Docker: permission denied エラーの対処法'
date: '2026-08-31'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: テスト用の説明文です。コロンを含む: これがエラーの原因になります。
ja_tags: ['Docker']
en_tags: ['Docker']
---
```

`description`の値をクォートで囲まずに書いたまま`npm run build`を実行したところ、ビルドが失敗した。

```text
00:11:33 [build] Building static entrypoints...
00:11:41 [ERROR] [vite] ✗ Build failed in 7.99s
[astro:markdown] Could not load /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md (imported by src/pages/rss.xml.js): bad indentation of a mapping entry
file: /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md:5:30
  Location:
    /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md:5:30
  Stack trace:
    at generateError (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:1289:10)
    at readBlockMapping (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2278:7)
    at readDocument (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2721:3)
    at load$1 (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2810:19)
    at safeParseFrontmatter (file:///home/user/errsolved/node_modules/astro/dist/content/utils.js:328:12)
```

その記事1本だけが原因でサイト全体のビルドが止まる。エラーメッセージの`file:`行にファイル名と行・列番号（`:5:30`）まで出ているので、原因箇所の特定自体は難しくなかったが、「なぜコロンがあるだけでYAMLが壊れるのか」がすぐには分からず、最初はfrontmatterの他の項目（`ja_tags`の配列表記など）を疑って触ってしまった。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: 6.3.5（`npx astro --version`で確認）
- ビルドコマンド: `npm run build`（内部で`astro build && npx pagefind --site dist`を実行）
- 記事はMarkdown（`.md`）frontmatter方式。Content Collections（`.mdx`のschema定義）は未使用

## 試したこと

最初は`ja_tags: ['Docker']`のような配列表記を疑い、クォートの種類（シングル/ダブル）を変えて試したが変化はなかった。

次に、エラーメッセージの`file:`行が示す行番号（5行目）を素直に見てみた。5行目は`description`の行だった。

```yaml
description: テスト用の説明文です。コロンを含む: これがエラーの原因になります。
```

この時点で「値の途中に`:`（コロン）がある」ことに気づいたが、日本語の文章中の句読点的な使い方だったので、最初はYAMLの構文とは関係ないだろうと考えて見送ってしまった。

試しに、`description`の文の途中にあるコロン以降を削って短くしてビルドし直したところ、エラーが出なくなった。

```yaml
description: テスト用の説明文です。
```

```text
00:15:02 [build] 267 page(s) built in 10.9s
00:15:02 [build] Complete!
```

これで「コロンが原因である」ことが確定した。あとはコロンを消さずに直す方法を探した。

## 原因

YAMLの仕様では、`key: value`という行のうち、クォートで囲んでいない値（プレーンスカラー）の中に`:`（コロンの直後にスペースまたは改行が続く形）が現れると、それが新しいマッピングエントリ（`key: value`のペア）の開始とみなされてしまう。

今回の`description: テスト用の説明文です。コロンを含む: これがエラーの原因になります。`は、YAMLパーサーからは以下のように解釈されようとする。

- `description`キーの値が`テスト用の説明文です。コロンを含む`まで
- その後に続く`: これがエラーの原因になります。`が、インデントの合っていない別のマッピングエントリとして開始される

しかし後半はインデントの位置がキーとして成立しない位置にあるため、パーサーは「ブロックマッピングのエントリとしてのインデントがおかしい」と判断し、`bad indentation of a mapping entry`というエラーになる。Astroのビルドログに出ていたスタックトレースも、`js-yaml`の`readBlockMapping`（ブロックマッピングを読む処理）で例外が発生していることを示しており、この解釈と一致する。

Astro側の処理としては、`astro/dist/content/utils.js`の`safeParseFrontmatter`がMarkdownの`---`で囲まれた部分を`js-yaml`に渡してパースしている。ここで例外が投げられると、そのファイル単体のロードが失敗し、`rss.xml.js`のようにフィード生成のために全記事を横断的に読み込む処理からもエラーが波及して、ビルド全体が失敗する。

言い換えると、原因は「日本語の文章にコロンを含めたこと」自体ではなく、「クォートしていないYAMLのプレーンスカラー値の中にコロン（+スペースまたは行末）が含まれていたこと」にある。半角コロンでも全角コロン（：）ならこの問題は起きない（全角コロンはYAMLの構文上のセパレータとして扱われないため）。

## 解決手順

### 1. 問題の値をシングルクォートで囲む

`description`の値全体をシングルクォート`'...'`で囲む。シングルクォートで囲まれた文字列はYAMLのプレーンスカラーの規則を受けず、コロンをそのまま含められる。

```yaml
description: 'テスト用の説明文です。コロンを含む: これがエラーの原因になります。'
```

### 2. ビルドし直して確認する

```bash
npx astro build
```

```text
00:11:58 [build] 267 page(s) built in 10.83s
00:11:58 [@astrojs/sitemap] `sitemap-index.xml` created at `dist`
00:11:58 [build] Complete!
```

エラーなくビルドが完了した。

### 3. 他の記事も同じパターンがないか横断チェックする

このリポジトリでは`title`や`description`のfrontmatter値は既にシングルクォートで統一する運用になっているため、今回のように途中でクォートを外して書いてしまった箇所がないか、コミット前に目視で確認した。機械的に洗い出すなら、クォートなしでコロンを含む行を`grep`で拾う方法が使える。

```bash
grep -nE "^(title|description): [^'\"].*:" src/pages/posts/*.md src/pages/en/*.md
```

このリポジトリでは該当なし（0件）だったため、今回のテストファイル1件のみが原因だったと確認できた。

## 動作確認

修正後、対象記事だけでなくサイト全体のビルドが最後まで通ることを再確認した。

```bash
npm run build
```

```text
[build] 267 page(s) built in 11.14s
[build] Complete!
```

`dist/`配下に該当記事のHTMLが生成されていることも確認した。

```bash
ls dist/posts/ | grep astro-frontmatter-colon-yaml-error
```

```text
astro-frontmatter-colon-yaml-error
```

frontmatterの`description`がページの`<meta name="description">`に正しく出力され、途中で文字列が切れていないことも合わせて確認した。

## まとめ

- Astroのfrontmatter（Markdown方式）はYAMLとしてパースされるため、クォートしていない値の中に半角コロン`:`（直後にスペースまたは改行）があると、新しいマッピングエントリの開始と誤認識されて`bad indentation of a mapping entry`でビルドが失敗する。
- 対処はシンプルで、コロンを含む値はシングルクォート（またはダブルクォート）で囲めばよい。このリポジトリでは`title`・`description`をすべてシングルクォートで統一しているため、今回のように途中だけクォートを外すと事故になる。
- 同種のエラーは`title`や`description`に限らず、frontmatterのどの値でも起こり得る。エラーメッセージの`file:パス:行:列`を見れば発生箇所はすぐ特定できるので、まず該当行を見て「クォートなしでコロンを含んでいないか」を疑うのが早い。

## よくある質問

**Q: 全角コロン（：）でも同じエラーになりますか？**
なりません。YAMLの構文上のセパレータとして扱われるのは半角コロン`:`（かつ直後にスペースまたは改行が続く場合）のみです。全角コロンを使う、またはコロンの直後にスペースを入れずに書く（例: `コロン:直後`）ことでも回避できますが、意図しない表記になりやすいため、素直にクォートで囲む方が安全です。

**Q: ダブルクォートとシングルクォート、どちらを使うべきですか？**
このリポジトリでは既存のfrontmatterがシングルクォートで統一されているため、それに合わせている。YAMLとしてはどちらでも有効だが、ダブルクォートは`\`によるエスケープの扱いがシングルクォートと異なるため、混在させると別の落とし穴になりやすい。1つのリポジトリ内では表記を統一するのが安全。

**Q: MarkdownではなくMDX（Content Collections）でも同じ問題は起きますか？**
起きる。Content CollectionsでZodスキーマを定義していても、frontmatter自体のYAMLパースは同じ`js-yaml`が行うため、パースの時点でエラーになればスキーマ検証以前に失敗する。エラーメッセージの形はほぼ同じになる。

## 関連記事

- [AstroでMarkdownのスタイルを設定する方法](/posts/astro-markdown-styles)
- [AstroのSEO用metaタグ設定方法](/posts/astro-seo-meta-tags)
- [Astroで新しいページを追加する方法](/posts/astro-add-page)
- [Astro+Cloudflare Pagesでsitemap.xmlとrobots.txtを設定する方法](/posts/astro-sitemap-robots)
