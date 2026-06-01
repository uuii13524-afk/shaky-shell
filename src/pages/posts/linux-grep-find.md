---
title: 'Linuxでファイルを検索するgrep・findコマンドの使い方'
date: '2026-05-16'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
description: 'Linuxのgrepコマンドでファイル内のテキストを検索し、findコマンドでファイルを探す方法を解説。正規表現や絞り込みオプションも紹介します。'
---

## grep：ファイルの中身を検索

```bash
grep "error" app.log              # error を含む行
grep -r "検索文字列" src/          # フォルダ内を再帰的に検索
grep -i "error" app.log           # 大文字小文字を区別しない
grep -n "error" app.log           # 行番号を表示
grep -A 3 -B 3 "error" app.log    # 前後3行も表示
```

## find：ファイルの場所を検索

```bash
find . -name "*.log"               # 拡張子で検索
find . -type d -name "node_modules" # フォルダを検索
find . -mtime -1                   # 1日以内に更新されたファイル
```

## findとgrepを組み合わせる

```bash
find . -name "*.js" | xargs grep "console.log"
```

## ハマったポイント

- `grep -r` はnode_modulesも検索する。フォルダを絞ること
- `find /` はルートから検索するので時間がかかる

ログファイルをリアルタイムで監視しながらgrepで絞り込む使い方については[Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)も参考にしてほしい。

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
