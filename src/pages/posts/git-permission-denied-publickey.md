---
title: '新規VPSでgit cloneすると「Permission denied (publickey)」になる原因と解決手順（Ubuntu 24.04）'
date: '2026-08-24'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '新しく用意したVPSでgit cloneを実行すると「Permission denied (publickey)」となりリポジトリを取得できない症状を解説。SSH鍵のパーミッション修正からssh-agentへの登録、GitHub側の公開鍵確認までの解決手順を紹介します。'
ja_tags: ['Git', 'SSH', 'Permission denied']
en_tags: ['Git', 'SSH', 'Permission denied']
---

## やりたかったこと（症状）

新しく契約したUbuntu 24.04のVPSに、普段開発しているプライベートリポジトリをデプロイ用にcloneしようとした。SSH鍵はローカルPCで生成したものをそのままVPSにも配置していた。

```bash
git clone git@github.com:example-org/deploy-target.git
```

しかし以下のエラーで即座に失敗した。

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

ローカルPCでは同じリポジトリを問題なくclone・pushできていたため、最初はリポジトリのアクセス権限自体が剥がれたのかと思い、GitHub側のリポジトリ設定を確認しに行った。

## 環境

- OS: Ubuntu 24.04 LTS（新規契約のVPS）
- Git: 2.43.0（Ubuntu 24.04標準パッケージ）
- OpenSSH: 9.6p1
- SSH鍵: ed25519形式（ローカルPCで生成したものをVPSへコピー）
- GitHubアカウント: 個人アカウント（Organizationのプライベートリポジトリへのアクセス権あり）

## 試したこと

まずGitHub側の「Settings > Collaborators」を確認したが、自分のアカウントには問題なくアクセス権が付与されていた。次にリポジトリURLのタイプミスを疑い、HTTPSとSSHのURLを見比べたが、こちらも正しかった。

ここでようやくSSH接続そのものを疑い、GitHub公式が用意している疎通確認コマンドを実行した。

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

`git clone`と同じエラーが、Gitを経由しない素のSSH接続でも再現した。これでGitHubのリポジトリ設定ではなく、SSH認証そのものに問題があることが確定した。

原因を切り分けるため、`-v`オプションを付けて詳細ログを見た。

```bash
ssh -vT git@github.com
```

```text
debug1: Offering public key: /root/.ssh/id_ed25519 ED25519 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
git@github.com: Permission denied (publickey).
```

鍵ファイル自体は認識され、GitHubに提示はされているが、認証が通っていない。鍵の中身は壊れていなさそうなので、次にファイルのパーミッションを確認した。

```bash
ls -la ~/.ssh/
```

```text
-rw-r--r-- 1 root root  411 Aug 24 09:12 id_ed25519
-rw-r--r-- 1 root root  100 Aug 24 09:12 id_ed25519.pub
```

秘密鍵`id_ed25519`のパーミッションが`644`（`-rw-r--r--`）になっている。ローカルPCからVPSへ`scp`でコピーした際に、コピー元の権限がそのまま引き継がれず、デフォルトのumaskで上書きされたのが原因だった。

## 原因

OpenSSHのクライアントは、秘密鍵ファイルの権限が緩すぎる（グループやその他のユーザーに読み取り権限がある）場合、その鍵をセキュリティ上の理由で**黙って無視**する。エラーメッセージには「パーミッションが原因である」とは一切表示されず、GitHub側からの応答も「Permission denied (publickey)」という汎用的な文言しか返ってこないため、鍵の中身やGitHub側の設定を疑ってしまいやすい。

`ssh -v`のデバッグログでは「鍵を提示した（Offering public key）」というログは出るが、実際にはOpenSSHクライアントがローカルの権限チェックの時点で鍵を候補から除外している場合があり、`-vvv`まで上げないと権限起因かどうかの直接的な手がかりは出にくい。今回は状況証拠（`ls -la`でのパーミッション確認）から原因を特定した。

正しい秘密鍵のパーミッションは`600`（所有者のみ読み書き可）で、`.ssh`ディレクトリ自体も`700`である必要がある。今回は`scp`でのファイル転送時にVPS側のumask設定（`022`）がそのまま適用され、`644`になっていた。

## 解決手順

### 1. `.ssh`ディレクトリと秘密鍵のパーミッションを修正する

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

秘密鍵は所有者のみ読み書き可（`600`）、公開鍵は他者が読めても問題ないため`644`のままでよい。

### 2. パーミッションが正しく反映されたか確認する

```bash
ls -la ~/.ssh/
```

```text
drwx------ 2 root root 4096 Aug 24 09:12 .
-rw------- 1 root root  411 Aug 24 09:12 id_ed25519
-rw-r--r-- 1 root root  100 Aug 24 09:12 id_ed25519.pub
```

`id_ed25519`が`-rw-------`（600）になっていることを確認した。

### 3. ssh-agentに鍵を登録する

VPS側では`ssh-agent`が起動していないことが多いため、明示的に起動して鍵を追加した。

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

```text
Agent pid 3241
Identity added: /root/.ssh/id_ed25519 (deploy@vps)
```

### 4. SSH疎通を再確認する

```bash
ssh -T git@github.com
```

```text
Hi example-user! You've successfully authenticated, but GitHub does not provide shell access.
```

「successfully authenticated」が返り、認証が通ったことを確認できた。

### 5. 改めてcloneを実行する

```bash
git clone git@github.com:example-org/deploy-target.git
```

```text
Cloning into 'deploy-target'...
remote: Enumerating objects: 142, done.
remote: Counting objects: 100% (142/142), done.
remote: Compressing objects: 100% (98/98), done.
remote: Total 142 (delta 31), reused 120 (delta 18), pack-reused 0
Receiving objects: 100% (142/142), 1.02 MiB | 3.14 MiB/s, done.
Resolving deltas: 100% (31/31), done.
```

エラーなくcloneが完了した。

## 動作確認

デプロイ運用中に毎回`ssh-add`を手動実行するのは現実的ではないため、VPS再起動後も同じ状態を再現できるか確認した。

```bash
ssh-add -l
```

```text
The agent has no identities.
```

再起動後は案の定ssh-agentの登録が消えていた。恒久対応として`~/.bashrc`に自動登録を追記し、再ログイン後に再確認した。

```bash
grep -A2 "ssh-agent" ~/.bashrc
```

```text
eval "$(ssh-agent -s)" > /dev/null
ssh-add ~/.ssh/id_ed25519 2>/dev/null
```

```bash
ssh-add -l
```

```text
256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx deploy@vps (ED25519)
```

再ログイン後も鍵が自動登録され、`git clone`・`git pull`が鍵の再入力なしで通ることを確認した。

## まとめ

- 「Permission denied (publickey)」は鍵の中身の破損だけでなく、**秘密鍵のパーミッションが緩すぎる場合にも同じメッセージで失敗する**。エラー文言だけでは原因が特定できない。
- `scp`や`rsync`でSSH鍵を別環境へ移す際は、転送先のumaskによって権限が変わることがあるため、コピー後は必ず`ls -la ~/.ssh/`でパーミッション（秘密鍵は`600`、`.ssh`ディレクトリは`700`）を確認する。
- 切り分けは`git clone`ではなく`ssh -T git@github.com`（必要なら`-v`付き）で行うと、GitやGitHubのリポジトリ設定の問題なのか、SSH認証そのものの問題なのかを素早く区別できる。

## よくある質問

**Q: `ssh -v`のログに「Offering public key」と出ているのに、なぜ失敗するのですか？**
OpenSSHクライアント側で鍵を候補として提示する動作と、実際にその鍵が有効な候補として使われるかどうかは別です。パーミッションが緩い鍵はローカルのチェックで弾かれることがあり、`-v`程度のログでは「弾かれた」という直接的なメッセージが出ないことがあります。今回のように`ls -la`でパーミッションを目視確認するのが確実です。

**Q: 毎回`chmod`し忘れないようにする方法はありますか？**
鍵を生成する`ssh-keygen`コマンド自体は最初から`600`で秘密鍵を作成します。今回のように権限が崩れるのは、`scp`・`rsync`・アーカイブ展開（`tar`/`zip`）など、別環境へのファイル転送を経由したときがほとんどです。転送後は必ず`ssh -T git@github.com`で疎通確認する習慣をつけると早期に気づけます。

**Q: VPS再起動のたびに`ssh-add`し直すのが面倒です。**
`~/.bashrc`や`~/.profile`に`ssh-agent`の起動と`ssh-add`を追記しておけば、ログインのたびに自動で鍵が登録されます。デプロイ専用ユーザーであれば、`~/.ssh/config`で鍵のパスを明示的に指定しておくのも有効です。

## 関連記事

- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [SSHのconfigファイルで接続設定をまとめる方法](/posts/ssh-config-file)
- [git pushが拒否される（rejected）ときの原因と解決手順](/posts/git-push-rejected-fix)
- [Linuxのファイルパーミッション（chmod/chown）の基本](/posts/linux-file-permissions)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
