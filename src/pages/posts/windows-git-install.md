---
title: 'WindowsにGitをインストールして初期設定する方法'
date: '2026-05-07'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'WindowsにGit for Windowsをインストールしてgit config・SSH設定まで行う初期設定手順をステップごとに解説します。'
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

GitをインストールしたらGitHubにSSH鍵を登録しておくと毎回パスワードを入力しなくて済む。[SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)で設定しておくと便利だ。

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
