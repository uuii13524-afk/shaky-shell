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

誤って `.env` などをcommitしてしまった場合は、[Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)で対処できる。

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
