---
title: 'lsofコマンドの使い方｜ポートやファイルを使用中のプロセスを特定する'
date: '2026-07-08'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'lsof', 'プロセス管理']
description: 'lsofコマンドでポートやファイルを使用しているプロセスを特定する方法を解説。ポート競合の調査、削除できないファイルの原因調査、インストール方法やよくあるエラーも紹介。'
---

## ひとことで言うと

```bash
# 特定のポートを使っているプロセスを調べる
lsof -i :8080

# 特定のファイルを開いているプロセスを調べる
lsof /var/log/app.log
```

---

## やりたかったこと / 現象

サーバーを起動しようとしたら `Address already in use` と言われたり、ファイルを削除しようとしたら `Device or resource busy` と言われて操作できなかった。どのプロセスがポートやファイルを掴んでいるのか分からず作業が止まってしまった——そんな時に使うのが `lsof`（LiSt Open Files）コマンドです。

---

## 環境

- OS: Ubuntu 22.04 LTS / CentOS Stream 9 / macOS
- lsof: 4.94以降で動作確認

---

## 解決策

### 1. インストール確認

```bash
lsof -v
```

入っていない場合はインストールする。

```bash
# Ubuntu / Debian
sudo apt install lsof

# CentOS / RHEL
sudo dnf install lsof
```

### 2. ポートを使っているプロセスを調べる

```bash
lsof -i :8080
```

```
COMMAND   PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node     3142   user   22u  IPv4  85432      0t0  TCP *:8080 (LISTEN)
```

PIDが分かれば `kill` で終了できる。

```bash
kill -9 3142
```

### 3. ファイルを開いているプロセスを調べる

```bash
lsof /var/log/app.log
```

ログローテーション後に古いファイルハンドルを掴んだままのプロセスを見つけたい時などに使う。

### 4. 特定のプロセスが開いているファイル一覧を見る

```bash
lsof -p 3142
```

PIDを指定すると、そのプロセスが開いている全ファイル・ソケットを一覧できる。

### 5. 特定のディレクトリ配下で開かれているファイルを調べる

```bash
lsof +D /var/www/html
```

アンマウントできないディスクの原因調査などに便利。

### 6. 特定ユーザーが開いているファイルを調べる

```bash
lsof -u www-data
```

### 7. TCP/UDPの接続状態で絞り込む

```bash
# LISTEN状態のみ
lsof -i -sTCP:LISTEN

# 特定ホストとの接続のみ
lsof -i @192.168.1.10
```

---

## よくあるエラーと対処

### `lsof: command not found`

デフォルトで入っていないディストリビューションがある。パッケージマネージャーでインストールする。

```bash
sudo apt install lsof
```

### `lsof: WARNING: can't stat() ... file system`

NFSマウントなど一部のファイルシステムで権限不足の際に出る警告。動作自体には影響しないことが多いが、`sudo lsof` で実行すると解消することが多い。

### 出力が空で何も表示されない

一般ユーザー権限では他ユーザーのプロセス情報が見えないことがある。`sudo` を付けて実行する。

```bash
sudo lsof -i :8080
```

### `lsof` の実行が異常に遅い

ネットワークマウント（NFS等）が多いと `lsof` が全マウントをスキャンして遅くなることがある。`-i` などオプションで対象を絞ると速くなる。

```bash
lsof -i :8080 -a -c node
```

---

## よくある質問

**Q: `lsof` と `netstat` の違いは？**
`netstat` はネットワーク接続の一覧に特化していますが、`lsof` はネットワークソケットだけでなく通常ファイル・ディレクトリ・デバイスなど「開いているものすべて」を対象にできる汎用ツールです。

**Q: `ss` コマンドとどう使い分けますか？**
ポート使用状況の確認だけなら `ss -tulpn` の方が高速です。ファイルとプロセスの紐付けまで調べたい場合は `lsof` が向いています。

**Q: 権限がないと表示されないのはなぜ？**
自分が所有していないプロセスの情報を見るには root 権限が必要です。`sudo lsof` を使ってください。

**Q: 削除できないファイルを特定するには？**
`lsof <ファイルパス>` を実行し、表示されたPIDのプロセスを終了するか、そのプロセスが正常終了するのを待ってから削除します。

**Q: macOSでも同じ使い方ができますか？**
はい。macOSには標準で `lsof` が入っており、オプションもほぼ共通です。

---

## 関連記事

- [Dockerでポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)
- [linux kill コマンドの使い方](/posts/linux-kill-command)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
