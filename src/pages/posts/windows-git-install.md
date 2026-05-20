---
title: 'WindowsにGitをインストールして初期設定する方法'
date: '2026-05-07'
category: 'Git'
---

## やりたかったこと

WindowsにGitをインストールして使えるようにしたかった。

## 手順

### 1. Gitをダウンロード

https://git-scm.com から「Download for Windows」。

### 2. インストール

注意点：
- デフォルトブランチ名を `main` に変更する
- 「Git from the command line and also from 3rd-party software」を選ぶ

### 3. インストール確認

```
git --version
```

### 4. 初期設定

```
git config --global user.name "自分の名前"
git config --global user.email "メールアドレス"
```

## ハマったポイント

- インストール後にターミナルを再起動する
- user.nameとuser.emailを設定しないとcommit時にエラーになる
- デフォルトブランチ名を `main` にする

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
