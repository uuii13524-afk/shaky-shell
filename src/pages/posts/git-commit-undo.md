---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitで間違えてcommitした時の取り消し方を解説。git reset --softやgit revertを使ったコミットの取り消し・修正方法をまとめて紹介します。'
---

## やりたかったこと

`.env`ファイルを誤ってコミットしていたことに、pushした後で気づいた。GitHubのリポジトリをブラウザで確認したら`.env`の中身がそのまま公開されていた。`STRIPE_SECRET_KEY=sk_live_xxxxxxxx`という行がコミットの差分ビューに丸見えになっていて、かなり焦った。

しかも気づくまでに3日かかった。GitHubのセキュリティbotから「Secret exposed in commit」という通知のissueが自動で作られていて、それで初めて気づいた。3日間、誰でも`.env`の中身を見られる状態が続いていた。Stripeのシークレットキーが悪用されていないかを確認するためにStripeダッシュボードのアクセスログを確認して回る羽目になった。

急いで取り消そうとしたが、「コミットを取り消す」方法を調べると`git reset`と`git revert`の2種類が出てきてどちらを使えばいいか判断できなかった。コマンドを間違えて`--hard`を指定してしまい、`.env`とは関係ない1時間分のコードがごっそり消えてしまうという失敗もした。

```bash
git reset --hard HEAD~1
# 実行後に git status したら全部消えていた
```

最終的に`git log --oneline`と`git reflog`で現在地を確認してから操作をやり直したら短時間で解決した。

## 環境

- Git 2.44.0
- Windows 11 / Ubuntu 22.04
- GitHub（リモートリポジトリあり）

## 試したこと・うまくいかなかったこと

**`git revert HEAD`を試した → GitHubで古いコミットを開いたら.envが見えた**

「revertの方が安全」という情報を見て`git revert HEAD`を試した。「Revert "add .env file"」という新しいコミットが作られた。「これで取り消せた」と思ってブラウザでGitHubを開いたら、古いコミットをクリックすると`.env`の内容が丸見えのままだった。`git revert`は「取り消しコミット」を追加するだけで、過去のコミット自体は履歴に残り続けることを知らなかった。

**`git reset --hard HEAD~1`を使った → 1時間分のコードが消えた**

「commit自体を完全に消したい」と思って`git reset --hard HEAD~1`を使った。コミットは確かに消えたが、その時に書いていた`.env`とは無関係のコードも全部消えた。`--soft`と`--hard`の違いを理解せずに使った結果で、`git status`を見ても何も残っていなかった。

```bash
git reset --hard HEAD~1
# 実行後
git status
# nothing to commit, working tree clean
# 1時間分の変更が跡形もなく消えた
```

**push後に`git commit --amend`を試した → force pushが必要になった**

コミットメッセージを修正しようとして`git commit --amend`を使ったら、すでにpushした後だったのでリモートとの差分が生まれてしまい`git push --force`が必要になった。チームリポジトリだったのでforce pushは使えなかった。

## 解決策

状況に合わせてコマンドを使い分ける。まだpushしていないか、すでにpushしたかで方法が変わる。

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

**pushする前の場合はこれが最も安全。** コミットは消えるが、変更したファイルはstaged状態で残る。

```bash
git reset --soft HEAD~1
```

実行後は`git status`で確認するとファイルが「Changes to be committed」の状態になっている。`.env`を`git restore --staged .env`でアンステージしてから、`.gitignore`に追加して改めてコミットする。

```bash
git restore --staged .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: remove .env from tracking"
```

`.gitignore`に先に追加しておかないと、次のコミット時にまた`.env`が含まれてしまう。「アンステージ」→「.gitignoreに追加」→「.gitignoreをコミット」という順番を必ず守る。

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も消す）

ファイルの変更ごと全部なかったことにしたい場合。**元に戻せないので実行前に`git diff HEAD~1`でどんな変更が消えるか必ず確認する。**

```bash
git diff HEAD~1  # 消える変更を先に確認
git reset --hard HEAD~1
```

`--hard`を実行する前に必ず現在のコミットハッシュをメモしておく。万が一間違えた場合でも`git reflog`から復元できる（後述）。

### 3. commitメッセージだけ変更したい

まだpushしていない場合のみ使う。pushした後に使うとforce pushが必要になる。

```bash
git commit --amend -m "新しいメッセージ"
```

amendを使う前に「まだpushしていないか」を確認するには`git status`の出力を見る。「Your branch is ahead of 'origin/main' by 1 commit」が出ていればpush前でamendを使っていい。「Your branch is up to date」が出ていれば既にpushされているのでamendは使わない。

### 4. pushした後に取り消したい場合

pushした後は`reset`で履歴を書き換えるとチームに迷惑がかかる。`revert`で「取り消しコミット」を新しく作る方法が安全。

```bash
git revert HEAD --no-edit
git push
```

ただし`.env`を含むコミットをpushしてしまった場合は、`git revert`だけでは不十分。GitHubのコミット履歴には`.env`の内容が残っているので、**パスワードや秘密鍵はすぐに変更・再発行するのが先決**。その後、履歴から完全に削除するには`git filter-repo`を使う。

```bash
# git-filter-repoをインストール（Python環境が必要）
pip install git-filter-repo

# 特定ファイルを全履歴から削除
git filter-repo --path .env --invert-paths
```

実行後は`git push --force`が必要になる。チームリポジトリの場合は全メンバーへの事前告知が必要（force push後に全員がcloneし直す必要がある）。

### 5. --hardで消してしまった変更を復元する

`git reset --hard`で消してしまっても、`git reflog`で一定期間は復元できる。

```bash
git reflog
```

実行すると操作の履歴が出てくる。

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~1
d4e5f6g HEAD@{1}: commit: 1時間かけて書いた変更
```

`HEAD@{1}`のハッシュに戻したい場合：

```bash
git reset --hard d4e5f6g
```

`git reflog`のエントリはデフォルトで90日間保持される。`git reset --hard`を実行する前に現在のハッシュをメモしておく癖をつけておくと、より確実に復元できる。

### 6. .envを誤ってpushした時の緊急対応手順

**Step 1：認証情報を即時無効化する（最優先）**

```
- Stripe/AWS/GCPなどのダッシュボードで該当キーを削除または無効化
- GitHubのPATが含まれている場合はDeveloper settingsから削除
- DBパスワードが含まれている場合はDBのパスワードを即時変更
- 新しいキー/パスワードを発行して.envを更新する
```

**Step 2：.gitignoreに追加してローカルでアンステージ**

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "remove .env from tracking"
```

**Step 3：git filter-repoで全履歴から削除**

```bash
pip install git-filter-repo
git filter-repo --path .env --invert-paths
```

**Step 4：force pushしてチームに通知**

```bash
git push --force origin main
```

force push前に必ずチームメンバーに「force pushします。完了したら全員git cloneし直してください」と連絡する。

**Step 5：GitHubのキャッシュクリアを依頼（必要に応じて）**

force push後もGitHubのキャッシュに古いコミットが残ることがある。該当コミットのURLにアクセスして`.env`の内容が見えないことを確認する。まだ見える場合はGitHub Supportに連絡する。

## ハマったポイント

- `git revert`は「安全な取り消し方法」だと思っていたが、実際には「取り消しコミットを追加する方法」で過去のコミット内容は履歴に残り続ける。`.env`を含むコミットを`git revert`してもGitHubの古いコミットをブラウザで開けば`.env`の内容は見えてしまう。pushしてしまった機密情報は「リポジトリから削除した」ではなく「漏洩済み」として扱い、コミット取り消しと認証情報の再発行は別々の問題として対処する必要があった
- `--soft`と`--hard`の違いを理解せずに`git reset --hard HEAD~1`を使ったら、`.env`とは関係ない1時間分のコードが跡形もなく消えた。`--soft`はコミットだけ消えてファイルはstaged状態で残る、`--hard`はコミット・ステージ・ワーキングツリーすべて消える。「コードを消さずにコミットだけ取り消したい」なら`--soft`一択だった
- push後に`git commit --amend`を使ったらforce pushが必要になった。push後のコミットに`--amend`を使うと「ローカルのコミット履歴がリモートより進んでいる」状態になり、次の`git push`が弾かれる。`git status`で「Your branch is ahead of origin」が出ていれば push 前、「up to date」なら push 済みという確認を先に行う
- `git reset --hard`で消したコードは「永遠に戻らない」と思っていたが、90日以内なら`git reflog`からコミットのハッシュを探して復元できる。これを知らなくて1時間分の作業をゼロから書き直した。`git reset --hard`を実行する前に現在のハッシュをメモしておくか、`git reflog`の使い方を覚えておけば取り返しがつく
- `.env`をpushしてからgit操作だけに集中して認証情報の無効化を後回しにしてしまった。git操作で履歴を消している間も漏洩は続いている。正しい優先順位は「まず認証情報を無効化、その後履歴から削除」で、この2つは並行して進めるべき別々の作業だった

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
