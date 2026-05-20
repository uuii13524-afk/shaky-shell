---
title: 'GitのブランチをCLIで作成・切り替える基本コマンド'
date: '2026-05-08'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## 基本コマンド

```bash
git branch                    # ブランチ一覧
git switch -c ブランチ名       # 作成して切り替え
git switch ブランチ名          # 切り替え
git merge ブランチ名           # マージ
git branch -d ブランチ名       # 削除
```

## よくある使い方

```bash
git switch -c feature/new-function
git add .
git commit -m "add new function"
git switch main
git merge feature/new-function
git branch -d feature/new-function
```

## ハマったポイント

- 古いGitでは `git checkout`。新しいGitでは `git switch` が推奨
- マージ前に必ずmainに切り替える

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
