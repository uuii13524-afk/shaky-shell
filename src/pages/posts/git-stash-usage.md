---
title: 'git stashで作業を一時退避する方法'
date: '2026-05-20'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git stashで作業中の変更を一時退避する方法を解説。stash保存・復元・一覧確認・削除コマンドの基本的な使い方をまとめて紹介します。'
---

## 基本的な使い方

```bash
git stash              # 変更を退避
git stash list         # 退避一覧を確認
git stash pop          # 最新の退避を復元して削除
git stash apply        # 最新の退避を復元（削除しない）
git stash drop         # 最新の退避を削除
git stash clear        # 全ての退避を削除
```

## よくある使い方

```bash
# 作業中に緊急対応が必要になった場合
git stash
git switch hotfix
# 緊急対応してコミット
git switch main
git stash pop
```

## ハマったポイント

- `git stash pop` はコンフリクトが起きることがある
- 新規ファイルは `-u` オプションが必要
- `git stash clear` は元に戻せないので注意

stash後にブランチを切り替えて作業する場合は[GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)と組み合わせて使うとよい。

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
