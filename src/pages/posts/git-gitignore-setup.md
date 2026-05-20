---
title: 'Gitで.gitignoreを設定してファイルを管理対象から外す方法'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

node_modulesや環境変数ファイルなど、GitHubにpushしたくないファイルを管理対象から外したかった。

## 環境

- Git

## .gitignoreの基本

### .gitignoreとは

Gitの管理対象から除外するファイルやフォルダを指定するファイル。
プロジェクトのルートに `.gitignore` というファイル名で作成する。

### 基本的な書き方

```
# コメント

# ファイルを除外
secret.txt

# フォルダを除外
node_modules/

# 特定の拡張子を除外
*.log
*.env

# 特定のフォルダ内のファイルだけ除外
dist/
.cache/
```

## よく使う.gitignoreの設定

### Node.jsプロジェクト向け

```
node_modules/
dist/
.env
.env.local
*.log
.DS_Store
.cache/
```

### Astroプロジェクト向け

```
node_modules/
dist/
.env
.env.local
.astro/
*.log
.DS_Store
```

## .gitignoreが効かない時の対処法

すでにGitの管理下に入っているファイルは `.gitignore` に追加しても無視されない。

### 解決方法

```
git rm -r --cached ファイル名またはフォルダ名
git add .
git commit -m "remove from tracking"
```

`--cached` をつけることでファイル自体は削除せず、Gitの管理対象からだけ外せる。

## テンプレートを使う方法

https://www.toptal.com/developers/gitignore にアクセスして
使用している技術（Node、Astro、Windowsなど）を入力すると
自動で.gitignoreを生成してくれる。

## ハマったポイント

- `.gitignore` はプロジェクトのルートに置く
- すでにcommitしたファイルは `git rm --cached` で管理対象から外す
- `node_modules/` のスラッシュは「フォルダを除外」という意味
- `.env` ファイルには絶対に秘密のキーや認証情報を書かない
