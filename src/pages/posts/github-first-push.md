---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでリポジトリを新規作成してローカルの既存プロジェクトを初めてpushするまでの手順をステップごとに解説します。'
---

## やりたかったこと

ローカルで作っていたAstroのプロジェクトをGitHubにpushしようとした。Gitはローカルで使っていたが、GitHubへのpushは初めてで認証周りでエラーが出て詰まった。「パスワードを入力してください」と言われてGitHubのログインパスワードを入力したらエラーになった。パスワードが合っているのになぜ弾かれるのかが最初わからなかった。

何度パスワードを入れ直してもエラーが出続けて、「GitHubのアカウントが制限されているのかも」と思って設定画面を確認しに行ったりと、30分以上迷走した。

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

とりあえずPATを試した。GitHubのどこでPATを発行するのか最初わからなかった。Settingsに行ったが「Personal access tokens」という項目が見当たらなかった。実は「Settings」→「Developer settings」→「Personal access tokens」という3段階の階層にあって、「Developer settings」はSettingsページの一番下の小さいリンクにある。ここを見つけるまで10分くらいかかった。

PATを発行してパスワード欄に貼り付けたら通ったが、毎回長いトークンをコピペするのが面倒だった。Windowsの場合は資格情報マネージャーに保存されるので2回目以降は入力不要だが、それを知らなくてPATを何度も貼り直していた。

また、リポジトリ作成時にREADMEを追加するチェックを入れてしまっていたので、最初のpushでこんなエラーが出た。

```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
hint: Integrate the remote changes (e.g. hint: 'git pull ...') before pushing again.
```

ローカルとリモートで別々のコミット履歴が存在していて競合していた。「pushに失敗した」というエラーで焦ったが、単純にリモートにREADMEのコミットがあっただけだった。

PATを発行する時に「Fine-grained tokens」と「Tokens (classic)」の2種類があって、どちらを選べばよいかわからなかった。「Fine-grained」の方が権限を細かく設定できると書いてあったが、設定項目が多くて迷った。コードをpushするだけなら「Tokens (classic)」の方がシンプルで、`repo`スコープだけ選べばよかった。

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

```bash
# .gitignoreに書いておくもの（最低限）
node_modules/
.env
dist/
.DS_Store
```

`.gitignore`がない場合は`git add .`の前に作成する。後から追加しても既に追跡中のファイルは対象外になるので、最初に設定する方がトラブルが少ない。

`git status`でどのファイルが追加されるか確認してからコミットするとうっかりミスが防げる。

```bash
git status  # 追加されるファイルを確認
git add .
git commit -m "first commit"
```

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

Windowsの場合、一度認証が通ると「Windows 資格情報マネージャー」に保存される。次回以降は入力不要になるので、PATは発行したら安全な場所に保管しておく。

PATの有効期限が切れると次の pushで認証エラーになる。その場合はWindowsの「資格情報マネージャー」→「Windows 資格情報」→GitHubのエントリを削除してから新しいPATで再認証する。「突然pushできなくなった」という時はPATの期限切れを疑う。

**SSH鍵を使う場合（長期的には推奨）：**

SSH鍵を使うと毎回トークンを入力しなくて済む。設定手順は[SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)を参照。SSH接続に切り替えた後はremoteのURLをSSH形式に変更する。

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
```

変更後に`git remote -v`で確認する。

```
origin  git@github.com:ユーザー名/リポジトリ名.git (fetch)
origin  git@github.com:ユーザー名/リポジトリ名.git (push)
```

### 5. READMEチェックありで作ってしまった場合

ローカルとリモートで別々のコミット履歴がある場合は、pullして統合してからpushする。

```bash
git pull origin main --allow-unrelated-histories
# コンフリクトが出た場合は解消してコミット
git push -u origin main
```

`--allow-unrelated-histories`オプションを付けないとpullが拒否される。コンフリクトが発生した場合はファイルを開いて`<<<<<<<`マークを探し、どちらの変更を残すか選択してから`git add`と`git commit`を実行する。

### 6. pushが成功したか確認する

```bash
git log --oneline -5  # ローカルのコミット履歴
git status  # 変更の状態
```

GitHubのリポジトリをブラウザで開いて、コミットが反映されているか確認する。リポジトリのトップページのコミット数とローカルの`git log`のコミット数が一致していればOK。

ブラウザで確認する際、「Insights」→「Network」グラフでコミット履歴を視覚的に確認できる。初回pushが成功していれば、グラフにコミットが表示される。

## ハマったポイント

- リポジトリ作成時に「Add a README file」を有効にするとリモートにコミットが作られる。ローカルとリモートで別々の履歴が生まれて最初のpushが失敗する。空のリポジトリから始める方が圧倒的にトラブルが少ない
- GitHubはパスワード認証を2021年8月に廃止している。ログインパスワードをそのまま入力しても絶対に通らない。「認証に失敗した」と思ってパスワードを何度も入力し直す時間が無駄だった。エラーメッセージをよく読めば原因が書いてある
- PATを発行する「Developer settings」はSettingsページの一番下の小さいリンクにある。上のメニューをいくら探しても見つからない。Settings → ページ最下部 → Developer settings という手順
- SSH鍵の設定を試みた時、HTTPSでcloneしたリポジトリにSSH鍵を設定してもremoteのURLがHTTPSのままでは機能しない。`git remote set-url`でSSH形式（`git@github.com:...`）のURLに変更するのが必要だった
- `git branch -M main`を実行するまで、ローカルのブランチが`master`になっていてGitHubの`main`と名前が合わずにpushが失敗した。最近のGitHubはデフォルトブランチが`main`なので、ローカルとブランチ名を合わせる必要がある
- PATのスコープで「repo」だけでなく全部チェックしてしまうと権限が広すぎる。コードのpushだけなら「repo」のみで十分。必要最小限のスコープにしておくのが安全
- Windowsの場合、PATを一度使って認証が通ると「資格情報マネージャー」に保存される。次回からは入力不要になるが、PATの有効期限が切れた後は再入力が必要になる。期限切れのトークンが保存されていると「認証エラー」が出るので、その場合は資格情報マネージャーからGitHubのエントリを削除して再認証する
- `git status`でコミット前にどのファイルがステージされているか確認しないと、意図しないファイルがコミットに含まれることがある。`.env`や`node_modules`が含まれていないか必ず確認してからコミットする癖が大事だった

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
