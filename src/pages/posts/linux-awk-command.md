---
title: 'awkコマンドでテキストを抽出・加工する方法'
date: '2026-05-29'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'awk', 'コマンドライン', 'テキスト処理']
en_tags: ['Linux', 'awk', 'command line', 'text processing']
description: 'Linuxのawkコマンドで列抽出・条件フィルタ・集計をする方法を解説。grep・sedと組み合わせたログ解析の実例も紹介。'
---
## やりたかったこと
ログファイルから特定の列だけ取り出したり、条件に合う行だけ集計したかった。
grepでは行単位、sedでは置換が得意だが、列ごとに処理するには awk が便利だった。

## awkの基本構文

```bash
awk '条件 { アクション }' ファイル名
```

何も条件を書かなければ全行に対してアクションが実行される。

### 特定の列を取り出す

スペース区切りのファイルで、1列目と3列目だけ表示する。

```bash
awk '{ print $1, $3 }' access.log
```

`$1` が1列目、`$2` が2列目…、`$NF` が最終列。

### 区切り文字を指定する

CSVなどカンマ区切りのファイルを扱うときは `-F` で区切り文字を指定する。

```bash
awk -F',' '{ print $2 }' data.csv
```

コロン区切りで `/etc/passwd` からユーザー名だけ取り出す例。

```bash
awk -F':' '{ print $1 }' /etc/passwd
```

### 条件でフィルタする

3列目が500以上の行だけ表示する。

```bash
awk '$3 >= 500 { print $0 }' access.log
```

特定の文字列を含む行だけ処理する。

```bash
awk '/ERROR/ { print $0 }' app.log
```

### 行数・合計を計算する

ファイルの行数を数える（`wc -l` と同じ）。

```bash
awk 'END { print NR }' file.txt
```

3列目の合計を計算する。

```bash
awk '{ sum += $3 } END { print sum }' access.log
```

### BEGIN と END ブロック

`BEGIN` はファイルを読む前、`END` は全行処理した後に実行される。

```bash
awk 'BEGIN { print "=== start ===" } { print $1 } END { print "=== end ===" }' file.txt
```

### grepと組み合わせる

nginxのアクセスログから500番台エラーのIPアドレスだけ抽出する実例。

```bash
grep ' 5[0-9][0-9] ' access.log | awk '{ print $1 }' | sort | uniq -c | sort -rn | head -20
```

### 変数を使う

awk内で変数を宣言して使える。

```bash
awk '{ count[$1]++ } END { for (ip in count) print count[ip], ip }' access.log | sort -rn | head -10
```

IPアドレス別のアクセス数集計によく使うパターン。

## ハマったポイント
- `$0` は行全体、`$1` から始まるのでゼロインデックスではない
- デフォルトの区切り文字はスペースとタブで複数の連続スペースもひとつとして扱う
- `-F','` で区切り文字を指定するとき、引数はシングルクォートで囲む
- `print $1 $2` は連結、`print $1, $2` はスペース区切りで出力される（カンマの有無に注意）
- 大きなログを処理するときは `awk` 単体の方が `python` より起動が速くて便利だった

## 関連記事
- [sedコマンドで文字列を置換・編集する方法](/posts/linux-sed-command)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [nginxのアクセスログとエラーログの確認方法](/posts/nginx-access-log)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
