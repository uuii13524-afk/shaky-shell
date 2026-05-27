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

ブランチの操作に慣れたら、[git rebaseで履歴を整理する方法](/posts/git-rebase-basics)も覚えておくと便利だ。

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
