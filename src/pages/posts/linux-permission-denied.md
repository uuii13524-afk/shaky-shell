---
title: 'Linuxでpermission deniedエラーが出た時の対処法'
date: '2026-05-14'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## 症状

```
Permission denied
bash: ./script.sh: Permission denied
```

## 原因と解決方法

### 実行権限がない

```bash
chmod +x script.sh
./script.sh
```

### 管理者権限が必要

```bash
sudo コマンド
```

### ファイルの所有者が違う

```bash
sudo chown ユーザー名:グループ名 ファイル名
```

## chmodの権限設定

```bash
chmod 755 ファイル名   # 所有者：読み書き実行、他：読み実行
chmod 644 ファイル名   # 所有者：読み書き、他：読みのみ
chmod +x ファイル名    # 実行権限を追加
```

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
