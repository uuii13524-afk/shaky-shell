---
title: 'Dockerコンテナの再起動ポリシー設定｜--restart オプションの使い方まとめ'
date: '2026-07-01'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'restart policy', 'コンテナ運用']
description: 'docker run --restart オプションでコンテナの自動再起動を設定する方法を解説。no/on-failure/always/unless-stoppedの違いと、既存コンテナへの適用方法を紹介します。'
---

## ひとことで言うと

```bash
# サーバー再起動後も自動でコンテナを起動させる
docker run -d --restart unless-stopped nginx

# 既存コンテナに再起動ポリシーを後から設定
docker update --restart unless-stopped <container_name>
```

---

## やりたかったこと / 現象

コンテナがクラッシュしたり、サーバーを再起動したりすると、コンテナが自動で立ち上がってこない。本番環境で常時稼働させたいサービスに、再起動ポリシーを設定したい。

---

## 環境

- Docker Engine 24.x 以降
- OS: Ubuntu 22.04 / CentOS / WSL2
- systemd で `docker` サービスが自動起動する設定済みであること

> **注意:** 再起動ポリシーが効くのは Docker デーモン自体が起動している場合のみです。OS起動時に Docker サービス自体が立ち上がるよう `systemctl enable docker` も併せて設定してください。

---

## 解決策

### 再起動ポリシーの4種類

```bash
docker run -d --restart no <image>              # 再起動しない（デフォルト）
docker run -d --restart on-failure <image>       # エラー終了時のみ再起動
docker run -d --restart on-failure:5 <image>     # 最大5回まで再起動
docker run -d --restart always <image>           # 常に再起動（手動停止でも）
docker run -d --restart unless-stopped <image>   # 手動停止以外は常に再起動
```

| ポリシー | 動作 |
|---------|------|
| `no` | 自動再起動しない（デフォルト） |
| `on-failure[:回数]` | 終了コードが0以外の場合のみ再起動 |
| `always` | どんな理由で停止しても再起動。`docker stop` 後もデーモン再起動で復活する |
| `unless-stopped` | `always` と同じだが、明示的に `docker stop` した場合は再起動しない |

### 本番環境でのおすすめ

常時稼働させたいWebサーバーやDBには `unless-stopped` が最も扱いやすいです。

```bash
docker run -d --restart unless-stopped -p 80:80 nginx
```

`always` だと、意図的に `docker stop` してもデーモン再起動時に復活してしまうため、メンテナンス時に混乱しやすいです。

### 既存コンテナのポリシーを変更する

すでに起動しているコンテナにも後から設定できます。

```bash
docker update --restart unless-stopped my-container
```

複数コンテナをまとめて変更する場合:

```bash
docker update --restart unless-stopped $(docker ps -q)
```

### docker-compose での設定

```yaml
services:
  web:
    image: nginx
    restart: unless-stopped
```

`docker compose up -d` で起動すれば、自動的にこのポリシーが適用されます。

### 現在のポリシーを確認する

```bash
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' my-container
```

---

## よくあるエラーと対処

### 再起動ポリシーを設定してもサーバー再起動後にコンテナが起動しない

Docker デーモン自体が自動起動していない可能性があります。

```bash
sudo systemctl enable docker
sudo systemctl status docker
```

### `Error response from daemon: no such container`

コンテナ名やIDが間違っています。`docker ps -a` で正確な名前を確認してください。

```bash
docker ps -a
docker update --restart unless-stopped <正しいコンテナ名>
```

### `on-failure` を設定したのに再起動が止まらない

回数制限を指定していない場合、失敗するたびに無限に再起動を試みます。回数を指定しましょう。

```bash
docker update --restart on-failure:3 my-container
```

### コンテナが再起動ループに陥る（CrashLoop）

アプリ側のエラーが原因で `on-failure` や `always` のループに入ることがあります。ログを確認してください。

```bash
docker logs --tail 50 my-container
```

---

## よくある質問

**Q: `always` と `unless-stopped` の違いは何ですか？**  
`always` は `docker stop` で止めても、Dockerデーモンが再起動すると自動的にコンテナも再起動します。`unless-stopped` は明示的に停止した場合はデーモン再起動後も停止したままになります。

**Q: 再起動ポリシーはデフォルトで何が設定されていますか？**  
`--restart` オプションを指定しない場合、デフォルトは `no`（自動再起動しない）です。

**Q: `docker-compose.yml` で `restart: always` と `restart: unless-stopped` はどちらが推奨ですか？**  
本番運用では `unless-stopped` が推奨です。メンテナンスで意図的に停止した際に、予期せず再起動してしまうのを防げます。

**Q: 再起動ポリシーの設定を確認するコマンドは？**  
`docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' <container_name>` で確認できます。

**Q: `on-failure` の回数制限を超えた場合はどうなりますか？**  
指定回数を超えて失敗すると、Dockerは再起動を諦めてコンテナは停止したままになります。

---

## 関連記事

- [docker compose down の使い方](/posts/docker-compose-down)
- [docker logs でコンテナのログを確認する](/posts/docker-logs)
- [docker system prune で不要なリソースを一掃する](/posts/docker-system-prune)
- [docker exec でコンテナ内にbashで入る方法](/posts/docker-exec-bash)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
