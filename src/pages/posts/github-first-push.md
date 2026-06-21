---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでリポジトリを新規作成してローカルの既存プロジェクトを初めてpushするまでの手順をステップごとに解説します。'
---

## やりたかったこと

ローカルで作っていたAstroのプロジェクトをGitHubにpushしようとしたら、認証でエラーが出て詰まった。YouTubeで「GitHubにpushする方法」という動画を見つけて、その通りに操作していた。動画の通りにコマンドを打って、パスワードを入力する画面が出たのでGitHubのアカウントパスワードを入れた。そしたら以下のエラーが出た。

```
remote: Support for password authentication was removed on August 13, 2021.
remote: Please see https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
fatal: Authentication failed for 'https://github.com/ユーザー名/my-astro-blog.git'
```

後で気づいたことだが、見ていたYouTube動画は2020年に録画されたものだった。動画の中ではパスワードを入力してpushが通る様子が映っていた。だが2021年8月にGitHubはパスワード認証を廃止しており、2020年の動画の手順はそのまま使えなくなっていた。動画の公開日を確認する習慣がなかったので、「なぜ動画通りにやってるのに動かないのか」と30分以上迷走した。

「パスワードが違う」というエラーではなく「パスワード認証は削除された」という内容だった。エラーメッセージを読んでいなかったので、最初は「アカウントのパスワードを間違えているのかも」と思ってブラウザでGitHubにログインして確認した。ログインできるので、パスワードは合っている。それなのにgitではエラーになる理由が全くわからなかった。

何度パスワードを入れ直してもエラーが出続けて、「GitHubのアカウントに何か制限がかかっているのかも」と思って設定画面を確認しに行ったりと、30分以上迷走した。

最終的にわかったのは、GitHubは2021年8月にパスワード認証を廃止していたということ。エラーメッセージにそのまま書いてあった。英文のエラーを読み飛ばしてしまったのが最初のミスだった。正しい手順さえわかれば初回pushは5分で終わる作業だった。

## 環境

- Git 2.44.0
- Windows 11
- GitHub（アカウント作成済み）
- Astro 5.2.3（対象プロジェクト）

## 試したこと・うまくいかなかったこと

最初、GitHubでリポジトリを作って「…or push an existing repository from the command line」に表示されたコマンドをそのままコピーして実行した。`git push -u origin main`まで進んだがパスワードエラーになった。「パスワードを間違えた」と思ってもう一度試したが、3回試しても同じエラーだった。エラーメッセージの1行目「password authentication was removed」を最初は読んでいなかったので、原因が全くわからなかった。

CLIでの認証がうまくいかないので、試しにGitHub Desktopをインストールして同じリポジトリをpushしてみた。GitHub Desktopはブラウザ経由でGitHubアカウントにログインする形式なので、パスワード認証の問題が一切なく、あっさりpushが通った。「あれ、GitHubへのpushはできてる。じゃあCLIの問題なんだ」とわかって、問題の切り分けができた。

ただGitHub Desktopを使い続けようとは思わなかった。CLIでコマンドを打ってpushできるようになりたかったし、「デスクトップアプリに頼るのは逃げている気がする」という気持ちがあった。それにVSCodeのターミナルやサーバーのSSH越しでは当然デスクトップアプリは使えない。GitHub Desktopで一回動作確認できたのは良かったが、「なぜCLIで動かないか」を理解するための調査に戻った。

パスワード認証が廃止されていたとわかった後、代替手段としてPersonal Access Token（PAT）を試した。「GitHubの設定でPATを発行する」とわかったが、GitHubのSettingsページを開いてもどこにもそれらしいメニューが見当たらなかった。「Emails」「Password and authentication」「SSH and GPG keys」などのメニューを全部見たが「Personal access tokens」という項目はなかった。

実は「Settings」→「Developer settings」→「Personal access tokens」という3段階の階層にあって、「Developer settings」はSettingsページの一番下のスクロールしないと見えない場所にある小さいリンクだった。ここを見つけるまで10分かかった。

```
Settings
  └── （一番下までスクロール）
       └── Developer settings
            └── Personal access tokens
                 └── Tokens (classic)
```

PATを発行してパスワード欄に貼り付けたら通ったが、次の問題が起きた。リポジトリ作成時に「Add a README file」のチェックを入れてしまっていたため、最初のpushでエラーになった。

```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
hint: Integrate the remote changes (e.g. hint: 'git pull ...') before pushing again.
```

「pushが失敗した」とだけ読み取ってしまい、原因がわからなかった。実際にはリモートにREADMEのコミットが作られていて、ローカルとリモートで別々のコミット履歴が存在していたから弾かれていただけだった。`git pull origin main --allow-unrelated-histories`で解決できたが、この`--allow-unrelated-histories`オプションは普通のpullでは使わないオプションで、調べるのに時間がかかった。

さらに詰まったのが、`git push -u origin main`を実行した時に「src refspec main does not match any」というエラーが出たケース。別のタイミングで試した時に起きた問題で、ローカルのデフォルトブランチが`master`のままで、GitHubのデフォルトが`main`になっていたため名前が合わなかった。

```
error: src refspec main does not match any
error: failed to push some refs to 'https://github.com/...'
```

`git branch`で確認したらブランチ名が`master`だったので`git branch -M main`でブランチ名を変更してから再度pushしたら通った。

## 解決策

### 1. GitHubでリポジトリを作成する

1. `github.com` にログイン
2. 右上「+」→「New repository」
3. Repository nameを入力
4. **「Add a README file」のチェックは外す**（ここをオンにすると最初のpushで競合が起きる）
5. 「Create repository」

空のリポジトリが作られると「Quick setup」画面が表示される。ここに表示されているコマンドを次の手順で使う。READMEのチェックを外し忘れた場合でも後から解決できるが（後述）、最初から外しておくのが圧倒的にトラブルが少ない。

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

`git status`の出力で「Untracked files」の中に`.env`や`node_modules`が含まれていないことを確認してからコミットする。含まれていた場合は`.gitignore`に追加してから`git add .`をやり直す。

### 3. GitHubと接続してpushする

GitHubの「Quick setup」画面に表示されているコマンドをそのまま実行する。

```bash
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

実行前に`git remote -v`でoriginのURLが正しいか確認しておくと安心だった。URLのタイポは発見しにくいので、GitHubの「Quick setup」画面のコピーボタンを使うのが確実。

`git branch -M main`はローカルのブランチ名を`main`に変更するコマンド。Git 2.28以前のデフォルトブランチは`master`なので、GitHubの`main`と名前を合わせるために必要。`git branch`で確認して既に`main`になっていれば実行不要。

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

スコープの「repo」は全プライベートリポジトリへのアクセス権を含む。パブリックリポジトリのみへのpushであれば「public_repo」だけで足りる。「とりあえず`repo`を入れておけばいい」と全部チェックしていた時期があったが、セキュリティの観点から必要最小限のスコープにしておくのが正しかった。

GitHubには「Tokens (classic)」と「Fine-grained tokens」の2種類がある。Fine-grained tokensはリポジトリ単位や権限単位で細かく制御できる。個人プロジェクトで使い始める場合はclassicのほうがシンプルで扱いやすかった。

Windowsの場合、一度認証が通ると「Windows 資格情報マネージャー」に保存される。次回以降は入力不要になるので、PATは発行したら安全な場所に保管しておく。

PATの有効期限が切れた場合、`git push`で`Authentication failed`が出る。Windows資格情報マネージャーに古いトークンが残っているとそれが使われて毎回失敗する。スタートメニューで「資格情報マネージャー」を開いて「Windows資格情報」タブを選び、`git:https://github.com`のエントリを削除してから新しいトークンを発行し直す。Macの場合はキーチェーンアクセスに保存されるので、「キーチェーンアクセス」でgithub.comを検索して該当エントリを削除してから再認証する。

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

SSH鍵を設定しておくと、PAT期限切れによる再認証の手間がなくなる。開発環境が複数ある場合は各環境で別々のSSH鍵を作ってGitHubに登録しておくとセキュリティ上も好ましかった。

### 5. READMEチェックありで作ってしまった場合

ローカルとリモートで別々のコミット履歴がある場合は、pullして統合してからpushする。

```bash
git pull origin main --allow-unrelated-histories
# コンフリクトが出た場合は解消してコミット
git push -u origin main
```

`--allow-unrelated-histories`オプションを付けないとpullが拒否される。コンフリクトが発生した場合はファイルを開いて`<<<<<<<`マークを探し、どちらの変更を残すか選択してから`git add`と`git commit`を実行する。

コンフリクトが発生したファイルをエディタで開くと、以下のような形で両方の変更が表示される。

```
<<<<<<< HEAD
ローカルの変更
=======
リモートの変更（READMEの内容など）
>>>>>>> origin/main
```

`<<<<<<<`から`>>>>>>>`までの間を、残したい内容に書き換えて保存する。その後`git add`と`git commit`でコンフリクトを解消する。

### 6. pushが成功したか確認する

```bash
git log --oneline -5  # ローカルのコミット履歴
git status  # 変更の状態
```

GitHubのリポジトリをブラウザで開いて、コミットが反映されているか確認する。リポジトリのトップページのコミット数とローカルの`git log`のコミット数が一致していればOK。

ブラウザで確認する際、「Insights」→「Network」グラフでコミット履歴を視覚的に確認できる。初回pushが成功していれば、グラフにコミットが表示される。

### 7. 2回目以降のpushの流れ

初回pushの設定が完了すれば、以降は以下の3コマンドだけで変更を反映できる。

```bash
git add 変更したファイル
git commit -m "変更内容"
git push
```

`-u origin main`は初回のみ必要で、2回目以降は`git push`だけで動く。`-u`オプションがローカルブランチとリモートブランチの追跡関係を設定するため、一度設定すれば以降は不要になる。

### 8. GitHub CLIを使った方法（代替手段）

PATの発行・管理が面倒に感じる場合は、GitHub CLI（`gh`コマンド）を使った認証が便利だった。インストール後に`gh auth login`を実行するだけでブラウザ経由でGitHubアカウントと連携できる。

```bash
# GitHub CLIのインストール（Windowsの場合）
winget install --id GitHub.cli

# macOSの場合
brew install gh

# 認証
gh auth login
```

`gh auth login`を実行するとインタラクティブな選択肢が出てくる。

```
? What account do you want to log into? GitHub.com
? What is your preferred protocol for Git operations? HTTPS
? Authenticate Git with your GitHub credentials? Yes
? How would you like to authenticate GitHub CLI? Login with a web browser

! First copy your one-time code: XXXX-XXXX
Press Enter to open github.com in your browser...
```

ブラウザが開いてワンタイムコードを入力するだけで認証が完了する。PATの発行・スコープ設定・トークンの保管という手間が一切不要で、「CLIでpushしたいだけなのにPATの説明が長い」と感じた時はこちらが早かった。

認証後は普通に`git push`が使えるようになる。`gh auth status`で認証状態を確認できる。

```bash
gh auth status
# github.com
#   ✓ Logged in to github.com as yourname
#   ✓ Git operations for github.com configured to use https protocol.
```

GitHub CLIはリポジトリの作成やIssueの管理など他の操作もCLIからできるので、入れておくと便利な場面が多かった。

## ハマったポイント

- リポジトリ作成時に「Add a README file」を有効にしないと問題ないと思っていたが、チェックをつけると空のリポジトリではなくREADMEのコミットが入った状態になる。ローカルとリモートで別々の履歴が生まれて最初のpushが失敗する。空のリポジトリから始める方が圧倒的にトラブルが少かった。「初期ファイルを作ってくれるから便利」と思って入れたのが裏目に出た
- GitHubはパスワード認証でpushできると思っていたが、2021年8月に廃止されていた。エラーメッセージの1行目「Support for password authentication was removed」にそのまま書いてあったが、英文を読み飛ばして何度もパスワードを入れ直すという無駄をした。エラーメッセージをちゃんと読む習慣が大事だった
- PATを発行する「Developer settings」はSettingsページの一番下の小さいリンクにあるだけで、上のメニューをいくら探しても見つからなかった。「Developer settings」という名前と「Personal access tokens」という名前が全然結びつかなかった。Settings → ページ最下部 → Developer settings という経路を知らないと辿り着けない
- SSH鍵を設定すればHTTPS+PATより便利だと思ってSSH鍵の設定を試みたが、HTTPSでcloneしたリポジトリにSSH鍵を設定してもremoteのURLがHTTPSのままでは機能しなかった。`git remote set-url`でSSH形式（`git@github.com:...`）のURLに変更する必要があって、鍵の設定とURL変更は別の操作だということを知らなかった
- ローカルのブランチ名が`master`のままだとGitHubの`main`と名前が合わずにpushが失敗するのはわかったが、`git branch -M main`を実行した後もうまくいかないことがあった。原因は`git remote add origin`でリモートを登録したURL自体を間違えていたこと。`git remote -v`でURLを確認する手順を最初に踏んでいれば20分省けた
- PATのスコープで「repo」だけでなく全部チェックすれば確実に動くと思っていたが、権限を広くするほどセキュリティリスクが上がる。コードのpushだけなら「repo」スコープのみで十分だった。「とりあえず全部チェック」でトークンを発行していたのは悪い習慣だった
- Windowsで一度PATを使って認証が通ると「資格情報マネージャー」に保存されて次回は入力不要になると思っていたが、PATの有効期限が切れると古いトークンが保存されたまま毎回認証エラーになり続けた。新しいPATを発行しても資格情報マネージャーに古いトークンが残っている限り使われてしまう。「資格情報マネージャーからエントリを削除してから再発行」という手順を知るまで30分かかった
- `git commit`せずに`git push`しようとすると「nothing to commit」や「Everything up-to-date」と出てpushが実行されないと思っていたが、実際には`git init`直後にコミットなしで`git push`を試みると「fatal: The current branch main has no upstream branch」というエラーになることがあった。「コミットしていない」と「upstreamが設定されていない」は別のエラーで、混同してしまった
- `git remote add origin`のURLを手入力する場合にタイポが起きやすい。URLが間違っていると`git push`で「repository not found」や「Could not read from remote repository」というエラーになる。手入力ではなくGitHubの「Quick setup」画面のコピーボタンを使うのが確実で、手入力は避けた方がいいということを最初は知らなかった
- `git push -u origin main`の`-u`（`--set-upstream`）オプションは初回のみ必要だと思っていなかった。2回目以降も`-u origin main`を付けていたが、`-u`なしで`git push`だけで動くようになる。`-u`で一度設定すれば追跡関係が保存されるという仕組みを知らなかった
- 2020年以前に録画されたYouTubeの手順動画を参考にしていたため、パスワードで認証できるという前提で進めていた。「動画通りにやっているのに動かない」という状況の原因が「動画が古い」だとは最初思わなかった。GitHubの仕様は2021年に大きく変わっており、動画の公開日を確認してから参考にする必要があった
- GitHub Desktopを試したらあっさりpushが通った。これで「Gitのインストールやリポジトリ設定は正しい、認証だけが問題」だとわかった。CLIで詰まった時にGitHub Desktopで試してみることで問題の切り分けができた。「CLIで動かないからGitが壊れている」ではなく「認証方法が違う」という正確な診断ができた
- PATのスコープ「repo」と「public_repo」の違いを理解していなかった。「repo」はプライベートリポジトリも含む全リポジトリへのアクセス権で、「public_repo」はパブリックリポジトリのみに限定される。パブリックリポジトリへのpushだけなら「public_repo」で十分で、不必要に広い権限を与えないのがセキュリティの基本だと後から知った

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
