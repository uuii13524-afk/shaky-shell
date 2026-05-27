---
title: 'Dockerの基本コマンドまとめ（run/stop/rm/ps）'
date: '2026-05-12'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'Dockerのrun・stop・rm・psなど基本的なコマンドの使い方をまとめました。コンテナの起動・停止・削除・確認に必要なオプションも解説します。'
---

## コンテナの操作

```bash
docker run -d -p 8080:80 --name myapp nginx  # 起動
docker ps           # 起動中のコンテナ一覧
docker ps -a        # 全コンテナ一覧
docker stop myapp   # 停止
docker rm myapp     # 削除
docker exec -it myapp bash  # コンテナに入る
docker logs -f myapp        # ログをリアルタイム表示
```

## イメージの操作

```bash
docker images               # イメージ一覧
docker pull nginx            # イメージを取得
docker rmi イメージID        # イメージを削除
docker build -t myapp .      # Dockerfileからビルド
```

## ハマったポイント

- `-d` をつけないとフォアグラウンドで起動してターミナルが占有される
- ポートは `-p ホスト側:コンテナ側` の順番

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [Dockerのボリュームでデータを永続化する方法](/posts/docker-volume-basics)
- [Dockerでポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
