---
title: 'jqコマンドでJSONを整形・抽出する方法'
date: '2026-06-08'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'jq', 'JSON', 'コマンド', 'bash']
en_tags: ['Linux', 'jq', 'JSON', 'command', 'bash']
description: 'jqコマンドの基本的な使い方を解説。curlのJSON出力を整形する方法や、特定のキーを抽出するフィルタの書き方を実例で紹介。'
---
## やりたかったこと
curlでAPIを叩いてJSONのレスポンスを確認しようとしたら、出力が1行に詰まっていて全く読めなかった。
`python3 -m json.tool` で整形しようとしたが、Pythonが入っていないサーバーだったので `jq` を使うことにした。

## 環境
- Ubuntu 22.04
- jq 1.6
- bash 5.1

## jqのインストール

```bash
# Ubuntu / Debian
sudo apt install jq

# macOS
brew install jq
```

インストール確認：

```bash
jq --version
# jq-1.6
```

## 基本的な使い方

curlのレスポンスを整形するだけなら `.` を使う：

```bash
curl -s https://api.example.com/users | jq '.'
```

ファイルに保存してある場合：

```bash
jq '.' response.json
```

## よく使うフィルタ

### 特定のキーを取り出す

```bash
# {"name": "taro", "age": 30} から name だけ取り出す
echo '{"name": "taro", "age": 30}' | jq '.name'
# "taro"

# クォートを外したい場合は -r オプション
echo '{"name": "taro", "age": 30}' | jq -r '.name'
# taro
```

### 配列の操作

```bash
# 配列の全要素を展開
echo '[{"id":1},{"id":2}]' | jq '.[]'

# 最初の要素だけ取り出す
echo '[{"id":1},{"id":2}]' | jq '.[0]'

# 配列から特定のキーだけを抽出してリストにする
echo '[{"name":"taro"},{"name":"hanako"}]' | jq '[.[].name]'
```

### ネストしたキーの取り出し

```bash
# {"user": {"profile": {"email": "test@example.com"}}}
echo '{"user":{"profile":{"email":"test@example.com"}}}' | jq '.user.profile.email'
# "test@example.com"
```

### select でフィルタリング

```bash
# ageが30以上の要素だけ取り出す
echo '[{"name":"taro","age":30},{"name":"hanako","age":25}]' | jq '[.[] | select(.age >= 30)]'
```

### 複数キーを組み合わせて出力

```bash
echo '[{"name":"taro","age":30}]' | jq '.[] | {user: .name, years: .age}'
```

## 試したこと・うまくいかなかったこと

最初は `grep` で必要なフィールドだけ取り出そうとしていたが、JSONが複数行にわたると全然うまくいかなかった。
`grep '"name"'` と打っても、値が次の行にあるケースで拾えなくて諦めた。

次に `awk` で区切ろうとしたが、JSONはネストがあるのでawkでパースするのは限界があった。
`python3 -c "import json,sys;..."` のワンライナーも試したが、毎回書くのが面倒すぎた。

## 解決策

`jq` をインストールして使ったら一発で解決した。
curlとパイプでつなぐだけで整形・抽出ができるので、それ以来APIデバッグはほぼ全部jqでやるようになった。

```bash
curl -s https://api.example.com/users/1 | jq '.name'
```

## ハマったポイント

- `.name` と書くと値にダブルクォートがついてくる。シェルスクリプトで変数に入れたい時は `-r` オプションが必要なのを最初は知らなかった
- 配列を展開する `.[]` と `.[0]` の違いを最初は混同していた。`.[]` は全要素をバラバラに出力し、`.[0]` は先頭1件だけを返す
- `select()` の中で文字列比較するとき `== "value"` の形にする必要があって、最初は `= "value"` と書いてエラーが出続けた
- jqフィルタをシェルスクリプトに書くとき、シングルクォートで囲まないとbashが `$` や `|` を展開してしまう

## 関連記事
- [curlコマンドの基本的な使い方](/posts/linux-curl-command)
- [awkコマンドでテキストを抽出・加工する方法](/posts/linux-awk-command)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [sedコマンドで文字列を置換・編集する方法](/posts/linux-sed-command)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
