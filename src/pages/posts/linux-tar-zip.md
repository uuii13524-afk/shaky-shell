---
title: 'tarとzipコマンドでファイルを圧縮・解凍する方法'
date: '2026-05-26'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'tar', 'zip', 'コマンド', 'ファイル操作']
en_tags: ['Linux', 'tar', 'zip', 'command', 'file operation']
description: 'tarコマンドでtar.gzファイルを作成・解凍する方法とzipコマンドの使い方を解説。ファイル圧縮・展開に必要なオプションをまとめて紹介します。'
---

## やりたかったこと

サーバー上のファイルをまとめてバックアップしたり、ログを圧縮して容量を節約したかった。
tarとzipはどちらもよく使うのに、オプションが多くていつも調べ直していた。

## tarコマンドの基本

### アーカイブを作成する（圧縮なし）

```bash
tar -cvf archive.tar ./mydir
```

- `-c` : 作成（create）
- `-v` : 詳細表示（verbose）
- `-f` : ファイル名を指定

### gzip圧縮で作成する（.tar.gz）

```bash
tar -czvf archive.tar.gz ./mydir
```

### bzip2圧縮で作成する（.tar.bz2）

```bash
tar -cjvf archive.tar.bz2 ./mydir
```

## tarで解凍する

```bash
# .tar を展開
tar -xvf archive.tar

# .tar.gz を展開
tar -xzvf archive.tar.gz

# .tar.bz2 を展開
tar -xjvf archive.tar.bz2

# 展開先ディレクトリを指定する
tar -xzvf archive.tar.gz -C /tmp/
```

## tarの中身を確認する（展開せずに）

```bash
tar -tzvf archive.tar.gz
```

## zipコマンドの基本

```bash
# ファイルを圧縮
zip archive.zip file1.txt file2.txt

# ディレクトリごと圧縮（再帰的に）
zip -r archive.zip ./mydir

# 圧縮レベルを指定（0〜9、デフォルトは6）
zip -r -9 archive.zip ./mydir
```

## unzipで解凍する

```bash
# カレントディレクトリに解凍
unzip archive.zip

# 解凍先を指定する
unzip archive.zip -d /tmp/output

# 中身を確認する（解凍せずに）
unzip -l archive.zip
```

## よく使うパターン

### ログを日付付きでアーカイブする

```bash
tar -czvf "logs-$(date +%Y%m%d).tar.gz" /var/log/nginx/
```

### 特定のファイルを除外して圧縮する

```bash
tar -czvf archive.tar.gz ./mydir --exclude='*.log' --exclude='node_modules'
```

### 圧縮率を確認する

```bash
ls -lh archive.tar.gz
du -sh ./mydir
```

## ハマったポイント

- `tar -xzvf` の `f` オプションは必ず最後にする（`-f`の直後にファイル名が来る）
- `zip -r` の `-r` を忘れるとディレクトリの中身が入らない
- `.tar.gz` と `.tgz` は同じ形式なのでどちらのオプションでも展開できる
- Linuxサーバーに `unzip` が入っていないことがある（`apt install unzip` で入れる）
- `tar` でパスを指定する際、先頭の `/` があると絶対パスで展開されて危険なことがある（`-P` オプションで解除可能）

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [rsyncでファイルを同期・バックアップする方法](/posts/linux-rsync)
- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
