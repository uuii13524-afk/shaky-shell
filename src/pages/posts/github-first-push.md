---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでリポジトリを新規作成してローカルの既存プロジェクトを初めてpushするまでの手順をステップごとに解説します。'
---

## やりたかったこと

ローカルで作っていたAstroのプロジェクトをGitHubにpushしようとした。Gitはローカルで使っていたが、GitHubへのpushは初めてで認証周りでエラーが出て詰まった。「パスワードを入力してください」と言われてGitHubのログインパスワードを入力したらエラーになった。パスワードが合っているのになぜ弾かれるのかが最初わからなかった。

## 環境

- Git 2.44.0
- Windows 11
- GitHub（アカウント作成済み）
- Astro 5.2.3（対象プロジェクト）

## 試したこと・うまくいかなかったこと

GitHubにリポジトリを作って、表示された「…or push an existing repository from the command line」のコマンドをそのまま実行した。`git push -u origin main`まで進んだが、ユーザー名とパスワードを求められた。GitHubのログインに使っているパスワードを入力したら以下のエラーになった。

```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
fatal: Authentication failed for 'https://github.com/ユーザー名/リポジトリ名.git'
```

2021年にパスワード認証が廃止されていたとは知らなかった。「じゃあどうやって認証するんだ」とGitHubのドキュメントを読んだが、Personal Access Token（PAT）とSSH鍵の2種類があってどちらを使えばいいか迷った。

とりあえずPATを試した。GitHubのどこでPATを発行するのか最初わからなかった。Settingsに行ったが「Personal access tokens」という項目が見当たらなかった。実は「Settings」→「Developer settings」→「Personal access tokens」という3段階の階層にあって、「Developer settings」はSettingsページの一番下のリンクにある。ここを見つけるまで10分くらいかかった。

PATを発行してパスワード欄に貼り付けたら通ったが、毎回長いトークンをコピペするのが面倒だった。

また、リポジトリ作成時にREADMEを追加するチェックを入れてしまっていたので、最初のpushでこんなエラーが出た。

```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
hint: Integrate the remote changes (e.g. hint: 'git pull ...') before pushing again.
```

ローカルとリモートで別々のコミット履歴が存在していて競合していた。

## 解決策

### 1. GitHubでリポジトリを作成する

1. `github.com` にログイン
2. 右上「+」→「New repository」
3. Repository nameを入力
4. **「Add a README file」のチェックは外す**（ここをオンにすると最初のpushで競合が起きる）
5. 「Create repository」

空のリポジトリが作られると「Quick setup」画面が表示される。ここに表示されているコマンドを次の手順で使う。

### 2. ローカルでGitを初期化してコミット

```bash
git init
git add .
git commit -m "first commit"
```

`git add .`でプロジェクト全体を追加するが、`.env`など機密ファイルは先に`.gitignore`に追加しておく。

### 3. GitHubと接続してpushする

GitHubの「Quick setup」画面に表示されているコマンドをそのまま実行する。

```bash
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

### 4. 認証を求められたらPATで認証する

GitHubはパスワード認証が廃止されているのでPersonal Access Token（PAT）を使う。

1. GitHubの右上アイコン → 「Settings」
2. 左サイドバーを一番下までスクロール → 「Developer settings」
3. 「Personal access tokens」→「Tokens (classic)」→「Generate new token」
4. 「Note」に用途を書く（例：「local development」）
5. Expirationは適切な期間を選ぶ（90 daysなど）
6. 「repo」スコープにチェックを入れる
7. 「Generate token」でトークンを発行

発行されたトークンをコピーしてパスワード入力欄に貼り付けると認証が通る。トークンは一度しか表示されないので、コピーしてパスワードマネージャーなどに保存しておく。

**SSH鍵を使う場合（長期的には推奨）：**

SSH鍵を使うと毎回トークンを入力しなくて済む。設定手順は[SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)を参照。SSH接続に切り替えた後はremoteのURLをSSH形式に変更する。

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
```

### 5. READMEチェックありで作ってしまった場合

ローカルとリモートで別々のコミット履歴がある場合は、pullして統合してからpushする。

```bash
git pull origin main --allow-unrelated-histories
# コンフリクトが出た場合は解消してコミット
git push -u origin main
```

`--allow-unrelated-histories`オプションを付けないとpullが拒否される。

## ハマったポイント

- リポジトリ作成時に「Add a README file」を有効にするとリモートにコミットが作られる。ローカルとリモートで別々の履歴が生まれて最初のpushが失敗する。空のリポジトリから始める方が圧倒的にトラブルが少ない
- GitHubはパスワード認証を2021年8月に廃止している。ログインパスワードをそのまま入力しても絶対に通らない。「認証に失敗した」と思ってパスワードを何度も入力し直す時間が無駄だった
- PATを発行する「Developer settings」はSettingsページの一番下の小さいリンクにある。上のメニューをいくら探しても見つからない。Settings → ページ最下部 → Developer settings という手順
- SSH鍵の設定を試みた時、HTTPSでcloneしたリポジトリにSSH鍵を設定してもremoteのURLがHTTPSのままでは機能しない。`git remote set-url`でSSH形式（`git@github.com:...`）のURLに変更するのが必要だった
- `git branch -M main`を実行するまで、ローカルのブランチが`master`になっていてGitHubの`main`と名前が合わずにpushが失敗した。最近のGitHubはデフォルトブランチが`main`なので、ローカルとブランチ名を合わせる必要がある
- PATのスコープで「repo」だけでなく全部チェックしてしまうと権限が広すぎる。コードのpushだけなら「repo」のみで十分。必要最小限のスコープにしておくのが安全

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
