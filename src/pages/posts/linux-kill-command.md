---
title: 'kill コマンドの使い方｜プロセスを終了させる方法とSIGTERM・SIGKILLの違い'
date: '2026-07-04'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'kill', 'プロセス管理', 'SIGKILL', 'SIGTERM']
description: 'Linuxのkillコマンドでプロセスを終了させる方法を解説。SIGTERMとSIGKILLの違い、killall・pkillとの使い分け、no such processエラーの対処法も紹介。'
---

## ひとことで言うと

```bash
# 通常の終了要求(SIGTERM)を送る
kill 1234

# 強制終了(SIGKILL)を送る
kill -9 1234

# プロセス名で終了させる
pkill node
```

---

## やりたかったこと / 現象

「プロセスが固まって反応しない」「バックグラウンドで動かしたコマンドを止めたい」「ポートを掴んだままのプロセスを終了させたい」といった場面で、特定のプロセスを終了させたい。

`kill` はプロセスIDに対してシグナルを送るコマンドで、名前に反して必ずしも「強制終了」ではなく、まずはプロセスに「終了してほしい」という合図(シグナル)を送るのが基本的な使い方です。

---

## 環境

- OS: Linux（Ubuntu / CentOS / Debian など）
- 確認コマンド: `kill -l`, `ps aux`, `pgrep`

---

## 解決策

### 1. 終了したいプロセスのPIDを確認する

```bash
ps aux | grep node
```

```
user   1234  0.5  1.2  912345  45678 pts/0   Sl   10:00   0:03 node server.js
```

2列目の `1234` がプロセスID(PID)です。

### 2. SIGTERM(通常終了)を送る

```bash
kill 1234
```

シグナルを指定しない場合、デフォルトで `SIGTERM (15)` が送られます。プロセスに後片付け(ファイルのクローズ、接続の切断など)をする猶予を与えて終了を促すシグナルです。

### 3. SIGKILL(強制終了)を送る

SIGTERMを送ってもプロセスが終了しない場合は、強制的に終了させます。

```bash
kill -9 1234
# または
kill -SIGKILL 1234
```

`SIGKILL` はプロセス側で無視・後処理ができない、OSレベルで強制的に終了させるシグナルです。データの後片付けができないため、最終手段として使います。

### 4. プロセス名で終了させる(pkill / killall)

PIDを毎回調べるのが手間な場合は、名前を指定して終了できます。

```bash
# 名前が部分一致するプロセスを終了
pkill node

# 完全一致するプロセス名で終了
killall node
```

```bash
# 強制終了も同様にオプションを付けられる
pkill -9 node
```

### 5. 特定ユーザーのプロセスだけ終了する

```bash
pkill -u www-data
```

### 6. 使えるシグナル一覧を確認する

```bash
kill -l
```

```
 1) SIGHUP       2) SIGINT       3) SIGQUIT      9) SIGKILL
15) SIGTERM     ...
```

---

## よくあるエラーと対処

### `kill: (1234): No such process`

指定したPIDのプロセスがすでに終了しているか、PIDを間違えています。再度 `ps aux` や `pgrep` で確認しましょう。

```bash
pgrep -a node
```

### `Operation not permitted`

自分の所有ではないプロセス(rootや他ユーザーのプロセス)を終了しようとしています。権限を確認してください。

```bash
sudo kill -9 1234
```

### `kill -9` してもゾンビプロセスが残る

ゾンビプロセス(状態が `Z` のプロセス)は既に終了処理が完了しており、親プロセスが `wait()` していないだけの状態です。`kill` では消えません。親プロセスを再起動するか終了させる必要があります。

```bash
ps aux | grep 'Z'
```

### ポートを掴んでいるプロセスを終了したい

```bash
# ポート3000を使っているプロセスのPIDを調べて終了
lsof -i:3000
kill -9 $(lsof -t -i:3000)
```

---

## よくある質問

**Q: `kill -9` はいつでも使っていいですか？**
なるべく避けるべきです。`SIGKILL` はプロセスに後片付けの機会を与えないため、ファイル破損やデータ不整合の原因になることがあります。まず `kill`(SIGTERM)を試し、反応がなければ `-9` を使いましょう。

**Q: `kill` と `pkill` の違いは？**
`kill` はPID(プロセスID)を指定してシグナルを送ります。`pkill` はプロセス名やその他の条件で対象を検索し、まとめてシグナルを送れます。

**Q: `killall` と `pkill` はどちらを使うべき？**
`killall` はプロセス名の完全一致、`pkill` は正規表現によるパターンマッチにも対応しています。より柔軟な指定をしたい場合は `pkill` が便利です。

**Q: SIGTERMとSIGKILL以外によく使うシグナルはありますか？**
`SIGHUP (1)` は設定再読み込みの合図としてよく使われ、`SIGINT (2)` は `Ctrl+C` に相当します。

**Q: Windowsで同じようなことをしたい場合は？**
`taskkill /PID 1234 /F` が `kill -9` に近い動作をします。

**Q: バックグラウンドジョブを止めたいだけなら `kill` を使う必要がありますか？**
シェルで実行中のジョブなら `jobs` でジョブ番号を確認し、`kill %1` のように指定することもできます。

---

## 関連記事

- [Linuxのプロセス管理コマンドまとめ(ps / top / kill)](/posts/linux-process-management)
- [docker exec でコンテナ内に入る方法](/posts/docker-exec-bash)
- [linux permission denied エラーの対処法](/posts/linux-permission-denied)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
