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

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
