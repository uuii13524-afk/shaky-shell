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
