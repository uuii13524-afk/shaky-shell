---
title: 'Dockerの基本コマンドまとめ（run/stop/rm/ps）'
date: '2026-05-12'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
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
