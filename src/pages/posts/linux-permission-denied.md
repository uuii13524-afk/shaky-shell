---
title: 'Linuxでpermission deniedエラーが出た時の対処法'
date: '2026-05-20'
category: 'Linux'
---

## 症状

Linuxでコマンドを実行すると以下のエラーが出る。

```
Permission denied
bash: ./script.sh: Permission denied
mkdir: cannot create directory: Permission denied
```

## 環境

- Linux（Ubuntu / Debian）
- WSL2
- Docker内のLinux

## 原因と対処法

### 原因1：実行権限がない

スクリプトファイルに実行権限が付いていない。

#### 確認方法

```bash
ls -la script.sh
# -rw-r--r-- 1 user user 100 May 20 12:00 script.sh
# 先頭が -rw- だと実行権限なし
```

#### 解決方法

```bash
chmod +x script.sh    # 実行権限を付与
./script.sh           # 実行
```

### 原因2：管理者権限が必要

システムファイルや `/etc/` などの操作には管理者権限が必要。

#### 解決方法

```bash
sudo コマンド
# 例：
sudo mkdir /var/myapp
sudo apt install nginx
```

### 原因3：ファイルの所有者が違う

ファイルの所有者が現在のユーザーと違う。

#### 確認方法

```bash
ls -la ファイル名
# root が所有者になっている場合など
```

#### 解決方法

```bash
sudo chown ユーザー名:グループ名 ファイル名
# 例：
sudo chown user:user /var/myapp
```

## chmodの権限設定

```bash
chmod 755 ファイル名   # 所有者：読み書き実行、他：読み実行
chmod 644 ファイル名   # 所有者：読み書き、他：読みのみ
chmod +x ファイル名    # 実行権限を追加
chmod -x ファイル名    # 実行権限を削除
```

## ハマったポイント

- WSL2でWindowsのファイルを操作するとPermission deniedになることがある
- `sudo` を使いすぎるとセキュリティリスクがある
- Dockerコンテナ内では権限の問題が起きやすい

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
