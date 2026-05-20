---
title: 'Linuxでファイルを検索するgrep・findコマンドの使い方'
date: '2026-05-16'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
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

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
