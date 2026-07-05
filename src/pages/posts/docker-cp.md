---
title: 'docker cp コマンドの使い方｜コンテナとホスト間でファイルをコピーする方法'
date: '2026-07-05'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker cp', 'ファイルコピー', 'コンテナ']
description: 'docker cpコマンドでホストとコンテナ間でファイルやディレクトリをコピーする方法を解説。停止中コンテナへのコピーやパーミッションエラーの対処法も紹介。'
---

## ひとことで言うと

```bash
# ホスト → コンテナへコピー
docker cp ./local-file.txt my-container:/app/file.txt

# コンテナ → ホストへコピー
docker cp my-container:/app/file.txt ./local-file.txt
```

---

## やりたかったこと / 現象

「コンテナの中に設定ファイルを1つだけ入れたい」「コンテナ内で生成されたログやDBダンプをホスト側に取り出したい」といった場面で、コンテナ全体を再ビルドせずにファイルだけをやり取りしたい。

`docker cp` はホストとコンテナの間でファイル・ディレクトリをコピーするコマンドで、Dockerfileの変更やイメージの再ビルドが不要な、その場しのぎのファイル転送に向いています。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. コンテナ名・IDを確認する

```bash
docker ps
```

```
CONTAINER ID   IMAGE     NAMES
a1b2c3d4e5f6   nginx     my-container
```

`NAMES` 列の `my-container` か `CONTAINER ID` を指定します。

### 2. ホストからコンテナへコピーする

```bash
docker cp ./config.yml my-container:/etc/app/config.yml
```

コピー先のディレクトリ（この例では `/etc/app/`）は事前に存在している必要があります。存在しない場合はエラーになります。

### 3. コンテナからホストへコピーする

```bash
docker cp my-container:/var/log/app.log ./app.log
```

コンテナ内のログファイルやDBダンプをホスト側に取り出すときによく使う書き方です。

### 4. ディレクトリごとコピーする

```bash
# ホスト → コンテナ（ディレクトリごと）
docker cp ./dist my-container:/usr/share/nginx/html

# コンテナ → ホスト（ディレクトリごと）
docker cp my-container:/app/logs ./logs
```

ファイル・ディレクトリのどちらを指定しても同じ `docker cp` コマンドでコピーできます。

### 5. 停止中のコンテナに対してもコピーできる

```bash
docker ps -a
docker cp ./config.yml stopped-container:/etc/app/config.yml
```

`docker cp` はコンテナが起動していなくても実行できます（起動しているプロセスへの介入ではなく、コンテナのファイルシステムを直接操作するため）。

### 6. docker-compose環境でのコンテナ名の確認

```bash
docker compose ps
```

`docker compose` で立ち上げた場合、コンテナ名は `プロジェクト名_サービス名_1` のような形式になることが多いので、`docker ps` や `docker compose ps` で正確な名前を確認してからコピーしましょう。

---

## よくあるエラーと対処

### `Error: No such container:path: my-container:/app/file.txt`

コピー元のパスがコンテナ内に存在しません。コンテナに入って確認しましょう。

```bash
docker exec -it my-container ls /app
```

### `lstat /path/to/local-file: no such file or directory`

ホスト側のコピー元パスが間違っています。相対パスを使う場合は、実行しているディレクトリを確認してください。

```bash
pwd
ls -la ./local-file.txt
```

### コピー先ディレクトリがなくてエラーになる

```
Error response from daemon: ... no such file or directory
```

コンテナ内にコピー先のディレクトリが存在しないと失敗します。先にディレクトリを作成してからコピーします。

```bash
docker exec my-container mkdir -p /etc/app
docker cp ./config.yml my-container:/etc/app/config.yml
```

### コピーしたファイルの所有者がrootになる

`docker cp` はデフォルトでコピー先の所有者をコンテナ内のrootにすることが多く、アプリの実行ユーザーと異なる場合、パーミッションエラーの原因になります。

```bash
docker exec my-container chown appuser:appuser /app/file.txt
```

---

## よくある質問

**Q: `docker cp` はコンテナが起動していなくても使えますか？**
使えます。停止中のコンテナでもファイルシステムには直接アクセスできるため、`docker cp` は実行可能です。

**Q: ワイルドカード（`*`）は使えますか？**
`docker cp` 自体はワイルドカードをサポートしていません。複数ファイルをコピーしたい場合はディレクトリごとコピーするか、`tar` と組み合わせる方法があります。

**Q: シンボリックリンクはどう扱われますか？**
デフォルトではシンボリックリンクの実体ではなく、リンクそのものがコピーされます。実体を追跡したい場合は `docker cp -L` オプションを使います。

**Q: `docker cp` と bind mount（`-v` オプション）はどう使い分けますか？**
継続的にファイルを同期させたい場合は bind mount が適しています。`docker cp` は一時的・一回限りのファイル転送に向いています。

**Q: `docker-compose` 環境でも使えますか？**
使えます。`docker compose ps` でコンテナ名を確認し、通常の `docker cp` と同様に指定します。

**Q: コピー中にコンテナが停止したらどうなりますか？**
コピー処理はDockerデーモンがファイルシステムに対して直接行うため、コンテナの起動状態が途中で変わっても影響を受けにくいですが、基本的にはコピー完了後に他の操作を行うことを推奨します。

---

## 関連記事

- [docker exec でコンテナ内に入る方法](/posts/docker-exec-bash)
- [Dockerのボリューム基本操作まとめ](/posts/docker-volume-basics)
- [docker logsコマンドの使い方](/posts/docker-logs)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
