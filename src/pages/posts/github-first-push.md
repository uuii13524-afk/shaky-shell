---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
---

## やりたかったこと

ローカルで作ったプロジェクトをGitHubにpushしたかった。

## 手順

### 1. GitHubでリポジトリを作成

1. github.com にログイン
2. 右上「+」→「New repository」
3. Repository nameを入力→「Create repository」

### 2. ローカルでGitを初期化

```
git init
git add .
git commit -m "first commit"
```

### 3. GitHubと接続してpush

```
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

## ハマったポイント

- リポジトリ作成時にREADMEを追加するとpushで競合が起きる
- パスワード認証は廃止。Personal Access Token（PAT）またはSSH鍵が必要

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
