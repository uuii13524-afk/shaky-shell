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
secret.txt
node_modules/
*.log
*.env
dist/
.cache/
```

## よく使う.gitignoreの設定

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

```
git rm -r --cached ファイル名またはフォルダ名
git add .
git commit -m "remove from tracking"
```

## テンプレートを使う方法

https://www.toptal.com/developers/gitignore でNode・Astro・Windowsなどを入力すると自動生成できる。

## ハマったポイント

- `.gitignore` はプロジェクトのルートに置く
- すでにcommitしたファイルは `git rm --cached` で管理対象から外す
- `.env` ファイルには絶対に秘密のキーや認証情報を書かない

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
