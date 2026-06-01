---
title: 'xargsコマンドで複数のファイルや入力を一括処理する方法'
date: '2026-05-30'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'xargs', 'コマンド', 'シェル', 'bash']
en_tags: ['Linux', 'xargs', 'command', 'shell', 'bash']
description: 'xargsコマンドの基本的な使い方を解説。findやgrepと組み合わせてファイルを一括削除・処理する方法をまとめた。'
---
## やりたかったこと
findで大量のファイルを検索して、そのまま一括削除や処理をしたかった。
`find . -name "*.log" | rm`みたいなことをしようとしたら全然動かなくて、xargsの存在を知った。

## xargsの基本的な使い方

### パイプと組み合わせて引数として渡す
```bash
echo "file1.txt file2.txt file3.txt" | xargs ls -l
```
標準入力の内容をコマンドの引数として渡してくれる。

### findと組み合わせてファイルを一括削除
```bash
find . -name "*.log" | xargs rm
```
findの出力をxargsがrmの引数に変換してくれる。

### ファイル名にスペースがある場合は-0オプション
```bash
find . -name "*.txt" -print0 | xargs -0 rm
```
`-print0`と`-0`を組み合わせることでスペース入りのファイル名も安全に処理できる。

### 一度に処理する数を制限する（-n）
```bash
echo "a b c d e" | xargs -n 2 echo
```
```
a b
c d
e
```
`-n 2`で一度に2つずつ引数を渡せる。

### 引数の位置を指定する（-I）
```bash
ls *.txt | xargs -I{} cp {} /backup/{}
```
`-I{}`で引数の場所を`{}`で指定できる。ファイルをバックアップディレクトリにコピーする時によく使った。

### 並列実行（-P）
```bash
find . -name "*.gz" | xargs -P 4 -I{} gzip -d {}
```
`-P 4`で4プロセス並列処理。大量のファイルを処理する時に速くなった。

## ハマったポイント
- パイプ直後にrmを書いても動かない。必ずxargsを経由する必要がある
- ファイル名にスペースや改行が含まれる場合は`-print0 | xargs -0`がほぼ必須
- `-I{}`を使う時は`{}`の前後に必要に応じてパスを指定する
- 引数の数が多すぎると「Argument list too long」エラーが出るが、xargsを使えば回避できる
- `--dry-run`オプションは存在しないので、事前にechoで確認してから本番実行する

## 関連記事
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [sedコマンドで文字列を置換・編集する方法](/posts/linux-sed-command)
- [awkコマンドでテキストを抽出・加工する方法](/posts/linux-awk-command)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [rsyncでファイルを同期・バックアップする方法](/posts/linux-rsync)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
