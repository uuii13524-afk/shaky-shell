---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでリポジトリを新規作成してローカルの既存プロジェクトを初めてpushするまでの手順をステップごとに解説します。'
---

## ひとことで言うと

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
# ↑ パスワード欄にはGitHubのパスワードではなくPersonal Access Token（PAT）を貼り付ける
```

2021年8月以降、GitHubはパスワード認証を廃止している。パスワードを何度入れても `Authentication failed` になる。PATを発行して貼り付けるのが正解。

---

## やりたかったこと

ローカルで作っていたAstroのプロジェクトをGitHubにpushしようとしたら、認証でエラーが出て詰まった。YouTubeで「GitHubにpushする方法」という動画を見つけて、その通りにコマンドを打って、パスワードを入力する画面が出たのでGitHubのアカウントパスワードを入れた。そしたら以下のエラーが出た。

```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
fatal: Authentication failed for 'https://github.com/ユーザー名/my-astro-blog.git'
```

見ていたYouTube動画は2020年に録画されたものだった。2021年8月にGitHubはパスワード認証を廃止しており、動画の手順はそのまま使えなくなっていた。エラーメッセージの1行目「Support for password authentication was removed」にそのまま書いてあったが英文を読み飛ばして、「パスワードが違うのかも」と思ってブラウザでGitHubにログインして確認するという無駄な行動を取った。ログインできるのにgitではエラーになる理由が全くわからなかった。

正しい手順さえわかれば初回pushは5分で終わる作業だった。

## 環境

- Git 2.44.0
- Windows 11
- GitHub（アカウント作成済み）
- Astro 5.2.3（対象プロジェクト）

## 試したこと・うまくいかなかったこと

**何度パスワードを入れ直してもエラーが続いた**

GitHubでリポジトリを作って「Quick setup」に表示されたコマンドをそのままコピーして実行した。`git push -u origin main`まで進んだがパスワードエラーになった。「パスワードを間違えた」と思ってもう一度試したが、3回試しても同じエラーだった。エラーメッセージの1行目を読み飛ばして原因が全くわからなかった。後から気づいたのは、参考にした動画が2020年録画のもので、2021年8月以降のGitHub仕様変更に対応していなかったことだった。

**PATを発行しようとしたが「Developer settings」が見つからなかった**

パスワード認証が廃止されていたとわかり、代替手段としてPersonal Access Token（PAT）を発行しようとした。GitHubのSettingsページを開いてもどこにも「Personal access tokens」という項目が見当たらなかった。「Emails」「Password and authentication」「SSH and GPG keys」などのメニューを全部見たが見つからなかった。

実は「Settings」→「Developer settings」→「Personal access tokens」という3段階の階層にあって、「Developer settings」はSettingsページの一番下のスクロールしないと見えない場所にある小さいリンクだった。ここを見つけるまで10分かかった。

```
Settings
  └── （一番下までスクロール）
       └── Developer settings
            └── Personal access tokens
                 └── Tokens (classic)
```

**「Add a README file」チェックありで作ってしまい最初のpushが失敗した**

PATを発行してパスワード欄に貼り付けたら認証は通ったが、pushでエラーになった。

```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

リポジトリ作成時に「Add a README file」のチェックを入れてしまっていたため、リモートにREADMEのコミットが作られていてローカルとリモートで別々のコミット履歴が存在していた。`git pull origin main --allow-unrelated-histories`で解決できたが、このオプションは普通のpullでは使わないので調べるのに時間がかかった。

## 解決策

### 1. GitHubでリポジトリを作成する

1. `github.com` にログイン
2. 右上「+」→「New repository」
3. Repository nameを入力
4. **「Add a README file」のチェックは外す**（ここをオンにすると最初のpushで競合が起きる）
5. 「Create repository」

空のリポジトリが作られると「Quick setup」画面が表示される。READMEのチェックを外し忘れた場合でも後から解決できるが、最初から外しておくのが圧倒的にトラブルが少ない。

### 2. ローカルでGitを初期化してコミット

```bash
git init
git add .
git commit -m "first commit"
```

`git add .`でプロジェクト全体を追加するが、`.env`など機密ファイルは先に`.gitignore`に追加しておく。`git status`でどのファイルが追加されるか確認してから`git add .`をするとうっかりミスが防げる。

```bash
# .gitignoreに書いておくもの（最低限）
node_modules/
.env
dist/
.DS_Store
```

### 3. GitHubと接続してpushする

GitHubの「Quick setup」画面に表示されているコマンドをそのまま実行する。

```bash
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

実行前に`git remote -v`でoriginのURLが正しいか確認しておく。URLのタイポは発見しにくいので、GitHubの「Quick setup」画面のコピーボタンを使うのが確実。

`git branch -M main`はローカルのブランチ名を`main`に変更するコマンド。Git 2.28以前のデフォルトブランチは`master`なので、GitHubの`main`と名前を合わせるために必要。

### 4. 認証を求められたらPATで認証する

GitHubはパスワード認証が廃止されているのでPersonal Access Token（PAT）を使う。

1. GitHubの右上アイコン → 「Settings」
2. 左サイドバーを**一番下までスクロール** → 「Developer settings」
3. 「Personal access tokens」→「Tokens (classic)」→「Generate new token」
4. 「Note」に用途を書く（例：「local development」）
5. Expirationは適切な期間を選ぶ（90 daysなど）
6. 「repo」スコープにチェックを入れる
7. 「Generate token」でトークンを発行

発行されたトークンをコピーしてパスワード入力欄に貼り付けると認証が通る。トークンは一度しか表示されないので、コピーしてパスワードマネージャーなどに保存しておく。

Windowsの場合、一度認証が通ると「Windows 資格情報マネージャー」に保存される。PATの有効期限が切れた場合、スタートメニューで「資格情報マネージャー」を開いて「Windows資格情報」タブを選び、`git:https://github.com`のエントリを削除してから新しいトークンを発行し直す。

### 5. READMEチェックありで作ってしまった場合

ローカルとリモートで別々のコミット履歴がある場合は、pullして統合してからpushする。

```bash
git pull origin main --allow-unrelated-histories
# コンフリクトが出た場合は解消してコミット
git push -u origin main
```

### 6. 2回目以降のpushの流れ

初回pushの設定が完了すれば、以降は以下の3コマンドだけで変更を反映できる。

```bash
git add 変更したファイル
git commit -m "変更内容"
git push
```

`-u origin main`は初回のみ必要で、2回目以降は`git push`だけで動く。

### 7. GitHub CLIを使った方法（代替手段）

PATの発行・管理が面倒に感じる場合は、GitHub CLI（`gh`コマンド）を使った認証が便利だった。

```bash
# インストール（Windowsの場合）
winget install --id GitHub.cli
# 認証
gh auth login
```

`gh auth login`を実行するとブラウザ経由でGitHubアカウントと連携できる。PATの発行・スコープ設定・トークンの保管という手間が一切不要だった。認証後は普通に`git push`が使えるようになる。

### 8. SSHで認証する方法（もう一つの代替手段）

HTTPSのPAT認証が複雑に感じる場合、SSH認証に切り替える方法もある。

```bash
# SSHキーを生成
ssh-keygen -t ed25519 -C "GitHubに登録しているメールアドレス"
# 生成されたキーをクリップボードにコピー（Windows）
type C:\Users\ユーザー名\.ssh\id_ed25519.pub | clip
```

コピーしたキーをGitHub → Settings → SSH and GPG keys → New SSH key に貼り付けて保存。
その後リモートのURLをSSH形式に変更する。

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
git push -u origin main
```

一度設定すれば期限切れがないのでSSHの方が長期的には便利だった。ただし初回設定のステップが多いので、最初のpushを早く済ませたい場合はPATかGitHub CLIの方が簡単だった。

## ハマったポイント

- GitHubはパスワード認証が2021年8月に廃止されていた。エラーメッセージの1行目「Support for password authentication was removed」にそのまま書いてあったが英文を読み飛ばして何度もパスワードを入れ直した。エラーメッセージを最初に読む習慣があれば5分で解決できた。参考にした動画が2020年録画で仕様変更前の手順だったことも原因で、動画の公開日を確認してから参考にする必要があった
- 「Developer settings」はSettingsページの一番下の小さいリンクにあるだけで、上のメニューをいくら探しても見つからなかった。「Settings → ページ最下部 → Developer settings → Personal access tokens」という経路を知らないと辿り着けない。Settingsの左サイドバーに見つからなくても一番下までスクロールすれば出てくる
- リポジトリ作成時に「Add a README file」を有効にするとREADMEのコミットが入った状態になり、最初のpushで「remote contains work that you do not have locally」と弾かれる。空のリポジトリから始める方が圧倒的にトラブルが少なかった。「初期ファイルを作ってくれるから便利」と思って入れたのが裏目に出た
- Windowsで一度PATを使って認証が通ると「資格情報マネージャー」に保存されるが、PATの有効期限が切れると古いトークンが保存されたまま毎回認証エラーになり続ける。新しいPATを発行しても資格情報マネージャーの古いエントリが使われてしまう。「資格情報マネージャーからエントリを削除してから再発行」という手順を知るまで30分かかった
- ローカルのブランチ名が`master`のままだとGitHubの`main`と名前が合わずに`git push -u origin main`が「src refspec main does not match any」で失敗する。`git branch -M main`でブランチ名を変更してから再度pushする。そもそも`git remote -v`でoriginのURLが正しく設定されているか確認する手順を最初に踏んでいれば余分な時間を省けた

## よくある質問

**Q: GitHubにpushする時にパスワードを入力しても「Authentication failed」と出ます。**
2021年8月以降、GitHubはパスワード認証を廃止している。パスワード欄にはGitHubのアカウントパスワードではなくPersonal Access Token（PAT）を貼り付ける。PATはGitHub → Settings → ページ最下部「Developer settings」→ Personal access tokens から発行できる。

**Q: PATの有効期限が切れたら毎回再発行が必要ですか？**
Windowsの場合、期限切れのPATが資格情報マネージャーに保存されたままになる。「コントロールパネル → 資格情報マネージャー → Windows資格情報 → `git:https://github.com` のエントリを削除」してから新しいPATを発行して認証すればリセットできる。GitHub CLIを使うと期限切れの問題が起きにくい。

**Q: `git push`で「src refspec main does not match any」と出ます。**
ローカルのブランチ名が`master`のままGitHubのデフォルトブランチ`main`にpushしようとして失敗している。`git branch -M main` でブランチ名を変えてからpushする。`git branch` でカレントブランチを確認してから操作するのが安全。

**Q: 「remote contains work that you do not have locally」と出てpushできません。**
リポジトリ作成時に「Add a README file」を有効にしたため、リモートにコミットが存在してローカルと履歴が食い違っている状態。`git pull origin main --allow-unrelated-histories` で統合してからpushする。次からリポジトリを作る時はREADMEのチェックを外す。

---

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
