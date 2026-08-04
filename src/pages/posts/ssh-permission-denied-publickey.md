---
title: 'SSHで「Permission denied (publickey)」になる原因と解決手順'
date: '2026-08-04'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
description: '新規VPSに鍵認証でSSH接続しようとするとPermission denied (publickey)で弾かれる症状を解説。sshd側のStrictModesと.sshディレクトリ・authorized_keysのパーミッションを確認し、原因を切り分けて解決するまでの手順を紹介します。'
ja_tags: ['SSH', 'Linux', 'VPS', 'パーミッション']
en_tags: ['SSH', 'Linux', 'VPS', 'permissions']
---

## やりたかったこと（症状）

新規契約したVPS（Ubuntu 22.04）に、ローカルで生成したed25519鍵を使ってSSH接続しようとした。`ssh-copy-id`は使わず、コンソール（VPS管理画面のブラウザターミナル）から手動で`authorized_keys`を作成した直後の状態だった。

```bash
ssh -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

パスワード入力を求められることもなく、いきなり接続を拒否された。

```text
deploy@203.0.113.10: Permission denied (publickey).
```

公開鍵は間違いなく`authorized_keys`に貼り付けたはずで、秘密鍵のパスも合っている。パスワード認証は別途無効化していたため、パスワードでのフォールバックもできない状態だった。

## 環境

- クライアント: macOS 14.5（ローカル）
- サーバー: Ubuntu 22.04.4 LTS（新規契約VPS）
- OpenSSH: クライアント9.6p1 / サーバー8.9p1
- 鍵の種類: ed25519（`ssh-keygen -t ed25519`で生成）
- 接続ユーザー: `deploy`（コンソールから`adduser`で作成、`authorized_keys`は手動配置）

## 試したこと

まず秘密鍵のパスとパーミッションを疑い、`-v`オプションで詳細ログを確認した。

```bash
ssh -v -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

```text
debug1: Offering public key: /Users/me/.ssh/id_ed25519_vps ED25519 SHA256:xxxxxxxx
debug1: Authentications that can continue: publickey
debug1: Trying private key: /Users/me/.ssh/id_ed25519_vps
debug1: Authentications that can continue: publickey
debug1: No more authentication methods to try.
deploy@203.0.113.10: Permission denied (publickey).
```

クライアント側は鍵を正しく提示できている（`Offering public key`まで進んでいる）のに、サーバー側が受理していない。ここでクライアント側の問題ではなくサーバー側の設定を疑い、VPSのコンソールから直接ログインして`sshd`のログを確認した。

```bash
sudo tail -n 20 /var/log/auth.log
```

```text
Aug  4 10:12:03 vps sshd[1842]: Authentication refused: bad ownership or modes for directory /home/deploy
Aug  4 10:12:03 vps sshd[1842]: Connection closed by authenticating user deploy 203.0.113.1 port 51422 [preauth]
```

`bad ownership or modes for directory /home/deploy`という具体的な理由がログに出ていた。パーミッションを確認する。

```bash
ls -ld /home/deploy /home/deploy/.ssh /home/deploy/.ssh/authorized_keys
```

```text
drwxrwxrwx 3 deploy deploy 4096 Aug  4 10:05 /home/deploy
drwxrwxrwx 2 deploy deploy 4096 Aug  4 10:06 /home/deploy/.ssh
-rw-rw-rw- 1 deploy deploy  103 Aug  4 10:07 /home/deploy/.ssh/authorized_keys

```

コンソールで`mkdir -p ~/.ssh`や`nano ~/.ssh/authorized_keys`を実行した際にumaskの設定でパーミッションが緩く（`777`/`666`）作成されていた。

## 原因

OpenSSHサーバーは`StrictModes yes`（デフォルト）の場合、鍵認証を受理する前にホームディレクトリ・`.ssh`ディレクトリ・`authorized_keys`ファイルの所有者とパーミッションを検証する。グループやその他のユーザーに書き込み権限（`group-writable`/`world-writable`）があると、「他人が`authorized_keys`を書き換えられる状態」とみなして認証自体を拒否する。今回は`/home/deploy`が`777`、`.ssh`が`777`、`authorized_keys`が`666`になっており、この検証に引っかかっていた。クライアント側の秘密鍵やログ上の`Offering public key`は正常だったため、鍵そのものではなくサーバー側のパーミッションが原因だと切り分けられた。

## 解決手順

### 1. ホームディレクトリと.sshディレクトリのパーミッションを修正する

VPS側にSSH経由では入れないため、コンソール（ブラウザターミナル）から作業する。

```bash
chmod 755 /home/deploy
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
```

- `700`: `.ssh`ディレクトリは所有者のみ読み書き実行可能にする。
- `600`: `authorized_keys`は所有者のみ読み書き可能にする。

### 2. 修正結果を確認する

```bash
ls -ld /home/deploy /home/deploy/.ssh /home/deploy/.ssh/authorized_keys
```

```text
drwxr-xr-x 3 deploy deploy 4096 Aug  4 10:20 /home/deploy
drwx------ 2 deploy deploy 4096 Aug  4 10:20 /home/deploy/.ssh
-rw------- 1 deploy deploy  103 Aug  4 10:20 /home/deploy/.ssh/authorized_keys
```

### 3. sshdの認証ログをリアルタイムで確認しながら再接続する

コンソール側で別セッションを開き、ログを監視した状態で改めて接続する。

```bash
# VPSコンソール側
sudo tail -f /var/log/auth.log
```

```bash
# ローカル側
ssh -i ~/.ssh/id_ed25519_vps deploy@203.0.113.10
```

## 動作確認

ローカルからの接続がパスワード入力なしで成功した。

```text
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-107-generic x86_64)
deploy@vps:~$
```

サーバー側のログにも、`Authentication refused`ではなく認証成功のログが出力されていることを確認した。

```text
Aug  4 10:24:11 vps sshd[1901]: Accepted publickey for deploy from 203.0.113.1 port 51501 ssh2: ED25519 SHA256:xxxxxxxx
```

## まとめ

- `Permission denied (publickey)`は鍵そのものの問題とは限らず、サーバー側の`StrictModes`によるパーミッション検証で拒否されているケースがある。まず`sudo tail /var/log/auth.log`（distroによっては`/var/log/secure`）で具体的な拒否理由を確認するのが近道。
- `bad ownership or modes for directory`のようなログが出ていたら、ホームディレクトリ・`.ssh`・`authorized_keys`のパーミッションを疑う。目安は`.ssh`が`700`、`authorized_keys`が`600`。
- コンソールから手動で`.ssh`や`authorized_keys`を作成すると、umaskの設定次第で意図せず緩いパーミッションになることがある。`ssh-copy-id`を使える環境なら、そちらの方が正しいパーミッションで作成されるため事故が少ない。

## よくある質問

**Q: `chmod 700`と`600`以外に緩めても大丈夫な設定はありますか？**
`.ssh`を`750`、`authorized_keys`を`640`程度までは動作することがありますが、グループ・その他への書き込み権限が付くと`StrictModes`で拒否されます。安全のため`700`/`600`を基本にしてください。

**Q: `StrictModes`を`no`にすれば回避できますか？**
できますが推奨しません。`StrictModes no`にすると誰でも`authorized_keys`を書き換えられる状態でも認証を通してしまい、セキュリティリスクになります。パーミッションを正しく設定する方が安全です。

**Q: ホームディレクトリ自体のパーミッションも影響しますか？**
します。ホームディレクトリがグループ・その他に書き込み可能（`775`/`777`など）になっていると、`.ssh`や`authorized_keys`が正しくても`bad ownership or modes for directory`で拒否されます。今回のケースもこれが直接の原因でした。

## 関連記事

- [SSH鍵をGitHubに登録する方法](/posts/ssh-key-github)
- [SSH configファイルで接続設定をまとめる方法](/posts/ssh-config-file)
- [Linuxのファイルパーミッションの基本](/posts/linux-file-permissions)
- [Linuxのユーザー管理コマンド](/posts/linux-user-management)
- [VPSにDockerをセットアップする手順](/posts/vps-docker-setup)
