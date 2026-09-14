---
title: '新しいUbuntu環境でgit pushすると「Permission denied (publickey)」になる原因と解決手順'
date: '2026-09-14'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '新しいUbuntu 24.04環境でgit pushを実行すると「Permission denied (publickey)」でGitHubに接続できない症状を解説。ssh -vTで原因を切り分け、新環境の公開鍵をGitHubに登録して解決するまでの手順を紹介します。'
ja_tags: ['Git', 'SSH', 'GitHub', 'publickey']
en_tags: ['Git', 'SSH', 'GitHub', 'publickey']
---

## やりたかったこと（症状）

自宅のデスクトップで使っていた開発環境を、新しく用意したミニPC（Ubuntu 24.04を新規インストール）に移行していた。既存のリポジトリを手元にcloneし直そうとしたところ、認証エラーで止まった。

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

旧デスクトップでは同じGitHubアカウントに何年も問題なくSSH接続できていたので、最初は「GitHub側の一時的な不調では」と疑い、少し時間を置いてから再実行した。結果は同じだった。

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

## 環境

- OS: Ubuntu 24.04.1 LTS（新規インストール直後のミニPC）
- Git: 2.43.0
- OpenSSH: 9.6p1
- 鍵の種類: ed25519（`ssh-keygen -t ed25519`で新規生成）
- GitHubアカウント: 旧デスクトップで数年前から利用している既存アカウント

## 試したこと

まず`~/.ssh`ディレクトリの中身を確認した。

```bash
ls -la ~/.ssh
```

```text
total 20
drwx------ 2 dev dev 4096 Sep 14 09:12 .
drwxr-x--- 15 dev dev 4096 Sep 14 09:10 ..
-rw------- 1 dev dev  411 Sep 14 09:12 id_ed25519
-rw-r--r-- 1 dev dev  102 Sep 14 09:12 id_ed25519.pub
```

新環境をセットアップした際に`ssh-keygen -t ed25519 -C "dev@example.com"`で鍵を作った記憶があり、鍵自体はここにある。パーミッションも`600`/`644`で特に問題は見当たらない。ここで一度「パーミッションの設定ミスでは」と疑ったが、`chmod 600 ~/.ssh/id_ed25519`を実行し直しても症状は変わらなかった。

次に`ssh-add -l`でエージェントに鍵が読み込まれているか確認した。

```bash
ssh-add -l
```

```text
2048 SHA256:9fK3l... /home/dev/.ssh/id_rsa (RSA)
```

表示されたのは旧デスクトップから`rsync`で持ってきていた古いRSA鍵だけで、新しく作った`id_ed25519`はエージェントに登録されていなかった。これを追加してから再度試した。

```bash
ssh-add ~/.ssh/id_ed25519
git clone git@github.com:example-org/internal-tools.git
```

```text
Identity added: /home/dev/.ssh/id_ed25519 (dev@example.com)
```

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

鍵をエージェントに追加しても状況は変わらなかった。ここまでの切り分けで「鍵ファイル自体・エージェントへの登録」は問題ではないとわかったため、次はSSH接続そのものを詳細ログ付きで確認することにした。

```bash
ssh -vT git@github.com
```

出力の末尾はこうなっていた。

```text
debug1: Offering public key: /home/dev/.ssh/id_ed25519 ED25519 SHA256:8pQmZ...
debug1: Authentications that can continue: publickey
debug1: Offering public key: /home/dev/.ssh/id_rsa RSA SHA256:9fK3l...
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
git@github.com: Permission denied (publickey).
```

このログで、クライアント側は`id_ed25519`と`id_rsa`の両方をきちんとGitHub側に提示している（`Offering public key`）ことがわかった。それでもGitHub側が両方とも拒否している、つまり**鍵は正しく送信できているが、GitHub側がこの公開鍵を「知らない」**という状態だと判断できた。

## 原因

新しいミニPCで`ssh-keygen`を実行して作った`id_ed25519`は、あくまでローカルに鍵ペアが生成されただけであり、その公開鍵（`id_ed25519.pub`）をGitHubアカウントの「SSH and GPG keys」に登録する作業をまだ行っていなかった。

GitHubはSSH認証時、接続元のマシンやアカウントの過去の利用履歴ではなく、そのアカウントに**明示的に登録された公開鍵のリスト**とだけ照合する。そのため「同じGitHubアカウントに以前から接続できていた」という事実は、新しいマシン・新しい鍵ペアの認証には一切関係がない。マシンを増やしたりOSを再インストールしたりして鍵を新規生成した場合、そのつど公開鍵をGitHub側に登録し直す必要がある。

`ssh -vT`のログで「鍵は提示されているのに全部拒否される」というパターンは、まさにこの「クライアントは正常、サーバー側の許可リストに未登録」というケースの典型的なサインだった。

## 解決手順

### 1. 新環境の公開鍵の中身を確認する

```bash
cat ~/.ssh/id_ed25519.pub
```

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN2q... dev@example.com
```

この1行をそのままコピーする。

### 2. GitHubの設定画面で公開鍵を登録する

GitHubにブラウザでログインし、`Settings > SSH and GPG keys > New SSH key`から、Titleに「mini-pc-2026」のようにマシンを識別できる名前を付け、Keyの欄に手順1でコピーした公開鍵の内容を貼り付けて保存した。

### 3. SSH接続を再テストする

```bash
ssh -T git@github.com
```

```text
Hi devuser! You've successfully authenticated, but GitHub does not provide shell access.
```

認証が通ったことを示すメッセージが返ってきた。

### 4. 改めてcloneを実行する

```bash
git clone git@github.com:example-org/internal-tools.git
```

```text
Cloning into 'internal-tools'...
remote: Enumerating objects: 842, done.
remote: Counting objects: 100% (842/842), done.
remote: Compressing objects: 100% (401/401), done.
remote: Total 842 (delta 398), reused 812 (delta 380), pack-reused 0
Receiving objects: 100% (842/842), 1.2 MiB | 4.8 MiB/s, done.
Resolving deltas: 100% (398/398), done.
```

エラーなくcloneが完了した。

### 5. 使わなくなった旧RSA鍵をエージェントから整理する

旧デスクトップから持ってきた`id_rsa`は今回のリポジトリでは不要だったため、混乱を避けるために`~/.ssh/config`でホストごとに使う鍵を明示しておいた。

```bash
# ~/.ssh/config
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

`IdentitiesOnly yes`を指定すると、エージェントに複数の鍵が登録されていても、指定した鍵だけを提示するようになる。

## 動作確認

`~/.ssh/config`を書き換えた後、念のためエージェントを一度クリアしてから再度接続テストを行った。

```bash
ssh-add -D
ssh -T git@github.com
```

```text
Identity removed: /home/dev/.ssh/id_ed25519 (dev@example.com)
Identity removed: /home/dev/.ssh/id_rsa (RSA)
All identities removed.
Hi devuser! You've successfully authenticated, but GitHub does not provide shell access.
```

エージェントが空の状態でも、`IdentityFile`の指定によって`id_ed25519`だけが提示され、認証に成功した。続けて既存の作業用リポジトリで`git push`も試したが、こちらも問題なく完了した。

```bash
cd internal-tools
git push origin main
```

```text
Everything up-to-date
```

## まとめ

- 「以前は接続できていたGitHubアカウント」でも、新しいマシン・新しい鍵ペアではそのつど公開鍵をGitHub側に登録し直す必要がある。鍵ファイルの存在やパーミッション、エージェントへの登録だけでは解決しない。
- `ssh -vT git@github.com`の末尾に`Offering public key`が並んだ上で`Permission denied (publickey)`になる場合は、クライアント側は正常で、サーバー（GitHub）側の許可リストに公開鍵が未登録であることを疑う。
- 複数の鍵を使い分ける場合は`~/.ssh/config`で`IdentityFile`と`IdentitiesOnly yes`を指定しておくと、意図しない鍵が先に提示されて拒否される事故を防げる。同種の「鍵はあるのに繋がらない」系のトラブルでも、まずログを詳細化して切り分けるという手順は応用できる。

## よくある質問

**Q: パスワード認証やHTTPS + Personal Access Tokenでも代用できますか？**
できます。`git remote set-url origin https://github.com/example-org/internal-tools.git`のようにHTTPS URLへ切り替え、認証にはPersonal Access Tokenを使う方法もあります。ただしプッシュのたびにトークン入力や認証情報ストアの管理が必要になるため、常用マシンではSSH鍵を登録しておくほうが手間が少ないです。

**Q: 1つのGitHubアカウントに複数の公開鍵を登録しても大丈夫ですか？**
問題ありません。GitHubは1アカウントに対して複数のSSH公開鍵を登録でき、マシンごとに鍵を分けて登録するのが公式にも推奨されている運用です。マシンを廃棄・入れ替えたときは、Settings画面から該当の鍵を削除しておくと安全です。

**Q: `ssh -vT`ではなく`ssh -T`だけでは原因は分かりませんか？**
`ssh -T git@github.com`だけだと`Permission denied (publickey)`という結果しか分からず、「鍵が未登録なのか」「エージェントに読み込まれていないのか」「別の鍵が優先されているのか」を切り分けられません。`-v`（さらに詳しく見たい場合は`-vvv`）を付けて`Offering public key`のログを見ることで、クライアント側とサーバー側のどちらに原因があるかを判断できます。

## 関連記事

- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git pushが「rejected」になる原因と解決手順](/posts/git-push-rejected-fix)
- [SSH設定ファイル（~/.ssh/config）の書き方](/posts/ssh-config-file)
- [WSL2にUbuntuをインストールする手順](/posts/wsl2-install-windows)

## おすすめのVPS
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
