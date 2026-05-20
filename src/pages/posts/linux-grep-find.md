---
title: 'Linuxでファイルを検索するgrep・findコマンドの使い方'
date: '2026-05-20'
category: 'Linux'
---

## やりたかったこと

Linuxでファイルの中身や場所を素早く探したかった。

## 環境

- Linux（Ubuntu / Debian）
- Mac
- WSL2

## grep：ファイルの中身を検索

```bash
grep "検索文字列" ファイル名
grep "error" app.log              # app.log から error を含む行を表示
grep -r "検索文字列" フォルダ名   # フォルダ内を再帰的に検索
grep -i "error" app.log           # 大文字小文字を区別しない
grep -n "error" app.log           # 行番号を表示
grep -v "error" app.log           # 含まない行を表示
grep -c "error" app.log           # マッチした行数を表示
```

### よく使う組み合わせ

```bash
# ログからエラーだけ抽出
grep "ERROR" /var/log/nginx/error.log

# 複数ファイルを検索
grep -r "TODO" src/

# 前後の行も表示
grep -A 3 -B 3 "error" app.log  # マッチした行の前後3行も表示
```

## find：ファイルの場所を検索

```bash
find . -name "ファイル名"          # 現在のフォルダ以下を検索
find / -name "nginx.conf"          # ルートから検索
find . -name "*.log"               # 拡張子で検索
find . -type d -name "node_modules" # フォルダを検索
find . -mtime -1                   # 1日以内に更新されたファイル
find . -size +10M                  # 10MB以上のファイル
```

### findとgrepを組み合わせる

```bash
find . -name "*.js" | xargs grep "console.log"
```

## ハマったポイント

- `grep -r` はフォルダを再帰的に検索するのでnode_modulesも検索してしまう
  - `grep -r "検索文字列" src/` のようにフォルダを絞る
- `find /` はルートから検索するので時間がかかる
- `grep` の検索文字列に特殊文字（`.`, `*`など）が含まれる場合はエスケープが必要

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
