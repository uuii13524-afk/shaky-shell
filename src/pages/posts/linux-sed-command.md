---
title: 'sedコマンドで文字列を置換・編集する方法'
date: '2026-05-27'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'sed', 'テキスト処理', 'コマンドライン']
en_tags: ['Linux', 'sed', 'text processing', 'command line']
description: 'sedコマンドを使ってファイル内の文字列を一括置換・行削除・抽出する方法。よく使うオプションと実例をまとめた。'
---
## やりたかったこと
設定ファイルの文字列を一括置換したり、ログファイルから特定の行だけ取り出したかった。
grepで検索はできるのに、置換となるとsedの使い方がよくわからなかった。

## sedの基本構文

```bash
sed 's/置換前/置換後/g' ファイル名
```

- `s` は substitute（置換）の意味
- `g` はglobal（行内すべてを置換）
- `g` を省略すると各行の最初の1つだけ置換する

## よく使う操作

### 文字列を置換する

```bash
# ファイル内の foo を bar に置換して出力
sed 's/foo/bar/g' config.txt

# ファイルを直接書き換える（-i オプション）
sed -i 's/foo/bar/g' config.txt

# macOS では -i '' が必要
sed -i '' 's/foo/bar/g' config.txt
```

### ファイルをバックアップしてから書き換える

```bash
# .bak ファイルを残しつつ上書き
sed -i.bak 's/foo/bar/g' config.txt
```

### 特定の行を削除する

```bash
# 3行目を削除
sed '3d' file.txt

# 空行をすべて削除
sed '/^$/d' file.txt

# コメント行（# で始まる行）を削除
sed '/^#/d' file.txt
```

### 特定の行だけ表示する

```bash
# 5行目から10行目を表示
sed -n '5,10p' file.txt

# "error" を含む行だけ表示
sed -n '/error/p' file.txt
```

### 行を追加する

```bash
# 3行目の後に行を追加
sed '3a\追加するテキスト' file.txt

# 3行目の前に行を追加
sed '3i\追加するテキスト' file.txt
```

### 複数の置換を一度に行う

```bash
# -e で複数条件を指定
sed -e 's/foo/bar/g' -e 's/hoge/fuga/g' file.txt
```

### スラッシュを含む文字列を置換する

URLやパスのような `/` が含まれる文字列を置換するときはデリミタを変える。

```bash
# デリミタを | に変える
sed 's|/old/path|/new/path|g' config.txt
```

## ハマったポイント

- `-i` でファイルを直接書き換えると元に戻せないので、`.bak` バックアップをつけておくのが安全
- macOS と Linux で `-i` の挙動が違う（macOS は `-i ''` が必要）
- 正規表現のメタ文字（`.` `*` `[` `]`）はバックスラッシュでエスケープが必要
- `g` フラグを忘れると各行の最初の1つしか置換されない
- sed はデフォルトで標準出力に書き出すだけで元ファイルは変更しない

## 関連記事
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)
- [curlコマンドの基本的な使い方](/posts/linux-curl-command)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
