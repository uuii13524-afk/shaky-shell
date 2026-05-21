---
title: 'LinuxのSSH接続の基本（VPSに接続する方法）'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

VPSやリモートサーバーにSSHで接続したかった。

## 環境

- Linux / Mac / Windows（Git Bash）

## 基本的なSSH接続

```bash
ssh ユーザー名@IPアドレス
ssh root@192.168.1.1
ssh root@example.com
```

## ポートを指定する

```bash
ssh -p 2222 root@example.com
```

## SSHキーを使って接続する

```bash
ssh -i ~/.ssh/id_ed25519 root@example.com
```

## ~/.ssh/configで設定を省略する

毎回オプションを入力するのが面倒な場合は設定ファイルに書く。

```
Host myserver
  HostName 192.168.1.1
  User root
  Port 22
  IdentityFile ~/.ssh/id_ed25519
```

設定後は以下だけで接続できる。

```bash
ssh myserver
```

## よく使うオプション

```bash
ssh -v root@example.com      # 詳細ログを表示
ssh -L 8080:localhost:80 root@example.com  # ポートフォワーディング
scp file.txt root@example.com:/tmp/       # ファイルをコピー
```

## セキュリティ設定

### rootログインを無効にする

```bash
nano /etc/ssh/sshd_config
# PermitRootLogin no に変更
systemctl restart sshd
```

### パスワード認証を無効にする

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
```

## ハマったポイント

- 接続できない場合はファイアウォールのポート22が開いているか確認する
- SSHキーのパーミッションは600でないと使えない（`chmod 600 ~/.ssh/id_ed25519`）
- VPSは初回接続時にフィンガープリントの確認が出る

## 関連記事

- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)

## おすすめのVPS

Linuxを本番環境で使うなら、VPSが手軽です。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
