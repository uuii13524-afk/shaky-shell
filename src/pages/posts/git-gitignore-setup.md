---
title: 'Gitで.gitignoreを設定してファイルを管理対象から外す方法'
date: '2026-05-09'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## .gitignoreとは

Gitの管理対象から除外するファイルやフォルダを指定するファイル。

## Astroプロジェクト向け設定

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

```bash
git rm -r --cached ファイル名
git add .
git commit -m "remove from tracking"
```

## テンプレートを使う

https://www.toptal.com/developers/gitignore で自動生成できる。

## ハマったポイント

- `.env` ファイルには絶対に秘密のキーを書かない
- すでにcommitしたファイルは `git rm --cached` で外す

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
