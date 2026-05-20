---
title: 'Astroで新しいページを追加する基本的な方法'
date: '2026-05-20'
category: 'Astro'
---

## やりたかったこと

Astroで新しいページを追加したかった。
Astroはファイルベースのルーティングなので、ファイルを置くだけでページが増える。

## 環境

- Astro 5

## 基本的なページの追加方法

### 1. src/pages/ にファイルを作成

`src/pages/about.astro` を作成すると `https://ドメイン/about` でアクセスできる。

```
src/
  pages/
    index.astro    → https://ドメイン/
    about.astro    → https://ドメイン/about
    contact.astro  → https://ドメイン/contact
```

### 2. .astroファイルの基本構成

```astro
---
// JavaScriptはここに書く
const title = "About";
---
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <p>ページの内容</p>
  </body>
</html>
```

### 3. サブディレクトリのページ

```
src/
  pages/
    posts/
      first-post.astro  → https://ドメイン/posts/first-post
```

### 4. Markdownファイルでページを作成

`.md` ファイルも自動的にページになる。

```
src/
  pages/
    posts/
      first-post.md  → https://ドメイン/posts/first-post
```

Markdownファイルの先頭にfrontmatterを書く。

```markdown
---
title: '記事タイトル'
date: '2026-05-20'
---

## 見出し

本文をここに書く。
```

## ハマったポイント

- `src/pages/` 以外に置いてもページにならない
- ファイル名がそのままURLになる（スペースは使えない）
- `.astro` と `.md` の両方でページを作れる
- `index.astro` はそのディレクトリのトップページになる

## 動的ルーティング

ページ数が多い場合は動的ルーティングを使う。

```
src/
  pages/
    posts/
      [slug].astro  → https://ドメイン/posts/任意の文字列
```

これで1つのファイルで複数のページを生成できる。
