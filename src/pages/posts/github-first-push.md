---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでリポジトリを新規作成してローカルの既存プロジェクトを初めてpushするまでの手順をステップごとに解説します。'
---

## やりたかったこと

ローカルで作っていたAstroのプロジェクトをGitHubにpushしようとした。Gitは使っていたがGitHubへのpushは初めてで、認証周りでエラーが出て詰まった。「パスワードを入力してください」と言われてGitHubのログインパスワードを入れたら弾かれた。

## 環境

- Git 2.44.0
- Windows 11
- GitHub（アカウント作成済み）
- Astro 5.2.3（対象プロジェクト）

## 試したこと・うまくいかなかったこと

GitHubにリポジトリを作って、表示されたコマンドをそのまま実行した。`git push -u origin main`まで進んだが、認証を求められてGitHubのログインパスワードを入力したら以下のエラーになった。

```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
fatal: Authentication failed for 'https://github.com/...'
```

2021年からパスワード認証が廃止されていたとは知らなかった。「じゃあどうやって認証するんだ」とGitHubのドキュメントを読んだが、Personal Access Token（PAT）とSSH鍵の2種類があって最初どちらを使えばいいか迷った。

PATを発行してパスワード欄に貼り付けたら通ったが、毎回長いトークンをコピペするのは面倒だった。そのためSSH鍵での認証を後から設定し直した。

リポジトリ作成時にREADMEを追加する設定にしてしまったので、最初のpushでこんなエラーが出た。

```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

ローカルとリモートの両方にコミットがあってコンフリクトしていた。

## 解決策

### 1. GitHubでリポジトリを作成する

1. `github.com` にログイン
2. 右上「+」→「New repository」
3. Repository nameを入力
4. **「Add a README file」のチェックは外す**（ここをオンにすると最初のpushで競合が起きる）
5. 「Create repository」

### 2. ローカルでGitを初期化してコミット

```bash
git init
git add .
git commit -m "first commit"
```

### 3. GitHubと接続してpushする

GitHubのリポジトリ作成後に表示されるコマンドをそのまま実行する。

```bash
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

### 4. 認証を求められたらPATまたはSSH鍵で認証する

**PATを使う場合：**

GitHubの Settings → Developer settings → Personal access tokens → Tokens (classic) → 「Generate new token」でトークンを発行する。スコープは`repo`にチェックを入れる。

パスワード入力欄に発行されたトークンを貼り付けると認証が通る。

**SSH鍵を使う場合（推奨）：**

SSH鍵を使うと毎回トークンを入力しなくて済む。設定手順は[SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)を参照。SSH接続に切り替えた後は`origin`のURLを変更する。

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
```

### 5. READMEチェックありで作ってしまった場合

リモートとローカルで別々のコミットが存在している場合は、先にリモートをpullして統合する。

```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## ハマったポイント

- リポジトリ作成時に「Add a README file」を有効にするとリモートにコミットが作られる。ローカルとリモートで別々のコミット履歴が生まれて最初のpushが失敗する。空のリポジトリから始める方がトラブルが少ない
- GitHubはパスワード認証を2021年に廃止している。ログインパスワードをそのまま入力しても絶対に通らない。PATかSSH鍵の設定が必要
- PATはGitHubのどこから作るか最初わからなかった。「Settings」→「Developer settings」という場所にある。「Developer settings」はSettings画面の一番下のリンクにある
- SSH鍵とPATの違いがわかっていなかった。HTTPSでcloneしたリポジトリにSSH鍵を設定しようとしてもremoteのURLがHTTPSのままなので意味がない。SSH接続にするにはremoteのURLをSSH形式（`git@github.com:...`）に変える必要があった
- `git branch -M main`を実行するまで、ローカルのブランチが`master`になっていてGitHubの`main`と名前が合わなかった。このコマンドでローカルのブランチ名を`main`に変更できる

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
