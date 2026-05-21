---
title: 'Linuxでユーザーを追加・削除する方法（useradd/userdel）'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

VPSにrootではない一般ユーザーを追加したかった。
rootでの作業はセキュリティリスクがあるので一般ユーザーを作成する。

## ユーザーの追加

```bash
useradd -m ユーザー名       # ユーザーを追加（ホームディレクトリも作成）
passwd ユーザー名            # パスワードを設定
```

## sudoグループに追加する

```bash
usermod -aG sudo ユーザー名
```

## ユーザーの確認

```bash
cat /etc/passwd             # ユーザー一覧
id ユーザー名               # ユーザーのID確認
groups ユーザー名           # 所属グループの確認
```

## ユーザーの削除

```bash
userdel ユーザー名          # ユーザーを削除
userdel -r ユーザー名       # ホームディレクトリごと削除
```

## ハマったポイント

- `-m` オプションを付けないとホームディレクトリが作成されない
- sudoを使うには `sudo` グループへの追加が必要
- rootログインを無効にする前に必ずsudo権限を持つユーザーを作成する

## 関連記事

- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)

## おすすめのVPS

Linuxを本番環境で使うなら、VPSが手軽です。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
