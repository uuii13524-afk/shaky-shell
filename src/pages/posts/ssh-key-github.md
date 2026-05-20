---
title: 'SSHキーを生成してGitHubに登録する方法'
date: '2026-05-11'
category: 'Git'
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
