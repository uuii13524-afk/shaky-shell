---
title: 'SSHキーを生成してGitHubに登録する方法'
date: '2026-05-11'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'SSH鍵ペアを生成してGitHubアカウントに公開鍵を登録する手順を解説。~/.ssh/configの設定方法とSSH接続の確認コマンドも紹介します。'
---

## 手順

### 1. SSHキーを生成

```bash
ssh-keygen -t ed25519 -C "GitHubのメールアドレス"
```

### 2. 公開鍵を確認

```bash
cat ~/.ssh/id_ed25519.pub
```

### 3. GitHubに公開鍵を登録

1. GitHub→Settings→「SSH and GPG keys」
2. 「New SSH key」→公開鍵を貼り付け

### 4. 接続確認

```bash
ssh -T git@github.com
```

### 5. リポジトリのURLをSSHに変更

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
```

## ハマったポイント

- 公開鍵（.pub）をGitHubに登録する。秘密鍵は共有しない
- 既存リポジトリのURLをSSHに変えないとHTTPSのままになる

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [Gitのリモートリポジトリ操作まとめ](/posts/git-remote-operations)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
