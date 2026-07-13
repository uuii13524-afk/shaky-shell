---
title: 'docker save / load コマンドの使い方｜イメージをファイルにエクスポート・インポートする方法'
date: '2026-07-13'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker save', 'docker load', 'イメージ移行']
description: 'docker save / docker loadコマンドでDockerイメージをtarファイルにエクスポートし、レジストリを経由せずに別環境へ移行する方法。よくあるエラーとdocker export/importとの違いも解説。'
---

## ひとことで言うと

```bash
# イメージをtarファイルとして書き出す
docker save -o myimage.tar myimage:latest

# tarファイルからイメージを読み込む
docker load -i myimage.tar
```

---

## やりたかったこと / 現象

インターネットに接続できないオフライン環境にDockerイメージを持っていきたい、DockerHubやプライベートレジストリを使わずに別のサーバーへイメージをコピーしたい——そんなときに `docker save` と `docker load` の組み合わせが役に立ちます。

`docker push` / `docker pull` はレジストリ経由の移行方法ですが、`docker save` / `docker load` はイメージをtarファイルとして直接やり取りする方法です。閉域網や検証環境など、レジストリを使えない・使いたくない場面で重宝します。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. イメージをtarファイルに書き出す（docker save）

```bash
docker save -o myimage.tar myimage:latest
```

`-o` を使わずに標準出力へ流し、`gzip` で圧縮することもできます。

```bash
docker save myimage:latest | gzip > myimage.tar.gz
```

複数のイメージをまとめて1つのtarファイルに書き出すことも可能です。

```bash
docker save -o images.tar myimage:latest another-image:v1
```

### 2. 別のマシンにファイルを転送する

```bash
scp myimage.tar user@remote-host:/tmp/
```

USBメモリなど物理メディア経由でもかまいません。

### 3. tarファイルからイメージを読み込む（docker load）

```bash
docker load -i myimage.tar
```

圧縮ファイルの場合はそのまま読み込めます。

```bash
docker load -i myimage.tar.gz
```

標準入力から読み込むことも可能です。

```bash
cat myimage.tar | docker load
```

### 4. 読み込んだイメージを確認する

```bash
docker images
```

`docker save` 時のタグ名がそのまま維持されるので、`docker run myimage:latest` のように元と同じ名前で起動できます。

### 5. コンテナのファイルシステムをエクスポートしたい場合（docker export）

イメージそのものではなく、動作中のコンテナのファイルシステムだけをエクスポートしたい場合は `docker export` を使います。

```bash
docker export <コンテナ名> -o container.tar
```

`docker export` で作成したtarファイルは `docker import` で読み込みますが、レイヤー履歴や `CMD`/`ENTRYPOINT` などのメタデータは失われる点に注意してください。

```bash
docker import container.tar myimage:imported
```

---

## よくあるエラーと対処

### `open myimage.tar: no such file or directory`

`docker load -i` に渡したファイルパスが間違っているか、`docker save` の出力先ディレクトリと異なる場所を指定しています。

```bash
ls -la myimage.tar
docker load -i ./myimage.tar
```

### `Error processing tar file(exit status 1): unexpected EOF`

ファイル転送が途中で中断され、tarファイルが破損していることが原因です。`scp` や `rsync` を使い直すか、`sha256sum` でファイルサイズ・ハッシュ値を転送前後で比較してください。

```bash
sha256sum myimage.tar
```

### `docker load` 後に `docker images` に何も表示されない

`docker load` が別のDockerデーモン（別のコンテキストやリモートホスト）に対して実行されている可能性があります。`docker context ls` で現在のコンテキストを確認してください。

```bash
docker context ls
docker context use default
```

### `no space left on device`

tarファイルの展開先でディスク容量が不足しています。`docker system df` で使用状況を確認し、不要なイメージ・コンテナを削除してください。

```bash
docker system df
docker system prune
```

---

## よくある質問

**Q: `docker save` と `docker export` の違いは？**
`docker save` はイメージをレイヤー構造・メタデータ（`CMD`/`ENTRYPOINT`・環境変数など）ごと丸ごと書き出します。`docker export` は動作中のコンテナのファイルシステムをフラットな1レイヤーとして書き出すもので、メタデータは保持されません。イメージをそのまま移行したい場合は `docker save` を使ってください。

**Q: tarファイルのサイズを小さくする方法は？**
`docker save myimage | gzip > myimage.tar.gz` のように圧縮するのが基本です。またマルチステージビルドで不要なレイヤーを削減しておくと、そもそものイメージサイズが小さくなります。

**Q: `docker load` でタグを変更できますか？**
`docker load` 自体にタグを変更するオプションはありません。読み込み後に `docker tag` で付け直してください。

```bash
docker tag myimage:latest myimage:v2
```

**Q: レジストリを使う方法と比べてどちらが良いですか？**
継続的にイメージを配布するならDockerHubやプライベートレジストリ（ECR、GCRなど）経由の `push`/`pull` が管理しやすくおすすめです。オフライン環境や一時的な移行には `save`/`load` が手軽です。

**Q: 複数イメージを1つのtarにまとめた場合、個別に読み込めますか？**
`docker load` はtarファイル内の全イメージを一括で読み込みます。個別に読み込みたい場合は、あらかじめイメージごとに `docker save` を分けて実行してください。

---

## 関連記事

- [docker inspect コマンドの使い方](/posts/docker-inspect-command)
- [Dockerイメージのタグ付け（docker tag）](/posts/docker-tag-command)
- [不要なDockerイメージを削除する（docker image cleanup）](/posts/docker-image-cleanup)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
