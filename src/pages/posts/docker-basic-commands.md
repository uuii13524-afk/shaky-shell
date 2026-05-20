---
title: 'Dockerの基本コマンドまとめ（run/stop/rm/ps）'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

Dockerを使い始めたがコマンドが多くて覚えられなかった。
よく使うコマンドだけまとめる。

## 環境

- Docker Desktop（Windows / Mac）
- Docker（Linux）

## コンテナの操作

### docker run：コンテナを起動

```bash
docker run nginx                    # nginxを起動
docker run -d nginx                 # バックグラウンドで起動
docker run -d -p 8080:80 nginx      # ポートを指定して起動
docker run -d --name myapp nginx    # 名前を付けて起動
docker run -it ubuntu bash          # 対話モードで起動
```

### docker ps：起動中のコンテナを確認

```bash
docker ps           # 起動中のコンテナ一覧
docker ps -a        # 全コンテナ一覧（停止中含む）
```

### docker stop：コンテナを停止

```bash
docker stop コンテナID
docker stop myapp   # 名前で指定
```

### docker start：停止中のコンテナを起動

```bash
docker start コンテナID
```

### docker rm：コンテナを削除

```bash
docker rm コンテナID
docker rm -f コンテナID   # 起動中でも強制削除
```

## イメージの操作

```bash
docker images                       # イメージ一覧
docker pull nginx                   # イメージを取得
docker rmi イメージID               # イメージを削除
docker build -t myapp .             # Dockerfileからビルド
```

## ログ・デバッグ

```bash
docker logs コンテナID              # ログを表示
docker logs -f コンテナID           # リアルタイムでログを表示
docker exec -it コンテナID bash     # コンテナに入る
docker inspect コンテナID           # 詳細情報を表示
```

## まとめてクリーンアップ

```bash
docker system prune                 # 不要なリソースを削除
docker system prune -a              # 全て削除（注意）
```

## ハマったポイント

- コンテナIDは最初の数文字だけで指定できる
- `-d` をつけないとフォアグラウンドで起動してターミナルが占有される
- `docker ps` に出ないコンテナは `docker ps -a` で確認する
- ポートは `-p ホスト側:コンテナ側` の順番

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
