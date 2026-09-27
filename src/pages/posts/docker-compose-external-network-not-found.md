---
title: 'docker compose upで「network ... not found」エラーが出る原因と解決手順'
date: '2026-09-27'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'docker compose upが「network app_shared_net not found」で失敗する症状を解説。external networkがdocker network pruneで消える原因と、再作成による復旧手順、再発防止策を紹介します。'
ja_tags: ['Docker', 'Docker Compose', 'ネットワーク']
en_tags: ['Docker', 'Docker Compose', 'network']
---

## やりたかったこと（症状）

複数のdocker-compose構成（アプリ本体と監視スタック）を同じDockerネットワーク上で相互通信させたかった。そのため、あらかじめ手動でネットワークを作成し、両方のcompose定義から`external: true`で参照する構成にしていた。

```bash
docker network create app_shared_net
```

```yaml
# app側 docker-compose.yml
services:
  web:
    image: myapp:latest
    networks:
      - app_shared_net

networks:
  app_shared_net:
    external: true
```

ある日、ディスク容量が逼迫してきたので、不要なDockerリソースをまとめて掃除しようと`docker network prune`を実行した。このとき監視スタック側は起動していたが、アプリ本体（web）は一時的に`docker compose down`で停止していた状態だった。

```bash
docker network prune
```

```text
WARNING! This will remove all custom networks not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Networks:
app_shared_net
```

掃除が終わったあと、アプリ本体を再度起動しようとしたところ、いきなり失敗した。

```bash
docker compose up -d
```

```text
Error response from daemon: network app_shared_net not found
```

## 環境

- OS: Ubuntu 24.04 LTS
- Docker Engine: 27.1.1
- Docker Compose: v2.29.1（Composeプラグイン、`docker compose`コマンド）
- 対象プロジェクト: アプリ本体（web）と監視スタック（Prometheus/Grafana）の2つのcompose構成
- ネットワーク: `app_shared_net`（手動作成の外部ネットワーク、両構成から`external: true`で参照）

## 試したこと

最初は`docker-compose.yml`のタイプミスを疑った。`networks:`セクションのインデントやネットワーク名のスペルを何度も見直したが、ファイルには問題がなかった。

次に`docker compose down`してから`docker compose up -d`をやり直そうとしたが、`down`も途中で失敗した。

```bash
docker compose down
```

```text
Network app_shared_net not found.
```

`down`側もネットワークが存在しない前提で動いていることが分かり、compose定義の問題ではなく「ネットワークそのものが消えている」可能性を疑い始めた。

```bash
docker network ls | grep app_shared_net
```

このコマンドは何も出力しなかった。ここでようやく、先ほど実行した`docker network prune`が原因だと気づいた。

## 原因

`docker network prune`は「少なくとも1つのコンテナに使用されていないカスタムネットワーク」をすべて削除するコマンドである。今回、`app_shared_net`を使っていたのは監視スタックのコンテナだけで、アプリ本体は`docker compose down`で全コンテナが停止済みだった。監視スタック側のコンテナがまだ動いていたにもかかわらず削除された理由を確認したところ、実際には監視スタック側も別のタイミングで一時停止しており、pruneを実行した瞬間にはネットワークへ接続しているコンテナが1つもない状態になっていた。

一方、`docker-compose.yml`側は`external: true`を指定している。これは「このネットワークはcompose自身が作成・管理するのではなく、既に存在するものを利用する」という宣言であり、`docker compose up`はネットワークの存在確認をするだけで、無ければ自動作成はしない。そのため、手動作成した`app_shared_net`が`prune`で消えた時点で、`up`も`down`も即座にエラーで止まるようになっていた。

## 解決手順

### 1. ネットワークが本当に存在しないことを確認する

```bash
docker network ls | grep app_shared_net
```

出力なし。`app_shared_net`が存在しないことを再確認した。

### 2. 同じ名前でネットワークを再作成する

カスタムサブネットやドライバ指定をしていない標準構成だったため、単純に同名で作り直した。

```bash
docker network create app_shared_net
```

```text
b6f2a1c4e8d3f7a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3
```

カスタムサブネットやIPAM設定をしている場合は、`docker network inspect`で削除前の設定を記録していないと同一構成での復元ができない点に注意が必要だった（今回は標準ブリッジ設定だったため影響はなかった）。

### 3. アプリ本体を再起動する

```bash
docker compose up -d
```

```text
[+] Running 2/2
 ✔ Network app_shared_net  Created
 ✔ Container myapp-web-1   Started
```

`Network app_shared_net Created`と表示されているが、これはcompose側の内部管理上の表示であり、実体は手順2で作成済みのネットワークにコンテナが接続された状態である。

### 4. 監視スタック側も同じネットワークに接続されているか確認する

```bash
docker network inspect app_shared_net --format '{{range .Containers}}{{.Name}} {{end}}'
```

```text
myapp-web-1 grafana-1 prometheus-1
```

アプリ本体と監視スタックの両方のコンテナが同じネットワークに接続されていることを確認できた。

### 5. 再発防止策を入れる

`docker network prune`を素朴に実行すると、今回のように一時的に全コンテナが停止しているタイミングで外部ネットワークごと消えてしまう。セットアップスクリプト側でネットワーク作成を冪等化しておく。

```bash
docker network inspect app_shared_net >/dev/null 2>&1 || docker network create app_shared_net
```

このワンライナーをデプロイスクリプトの先頭に置いておけば、ネットワークが存在しない場合のみ作成し、存在する場合は何もしない。また、pruneを使う際は`-f`や無条件実行を避け、対象を絞る。

```bash
docker network prune --filter "label!=keep"
```

外部ネットワークには`--label keep=true`を付けて作成しておくと、この除外フィルタで保護できる。

## 動作確認

ネットワーク再作成後、アプリ本体と監視スタックの両方を再起動し、相互通信を確認した。

```bash
docker compose exec web curl -s http://prometheus:9090/-/healthy
```

```text
Prometheus Server is Healthy.
```

アプリ本体から監視スタックのPrometheusへ、コンテナ名での名前解決とHTTP通信ができることを確認し、ネットワーク復旧が完了したと判断した。

## まとめ

- `docker network prune`は「接続中のコンテナが1つも無いネットワーク」を無条件に削除する。複数のcompose構成で共有している外部ネットワークは、片方が一時停止しているタイミングで巻き添えになることがある。
- `external: true`を指定したネットワークは、compose側が自動作成してくれない。存在しなければ`up`も`down`も即座にエラーになるため、「ファイルの記述ミス」を疑う前に`docker network ls`で実体の有無を確認するのが早い。
- 復旧は同名での`docker network create`で足りるが、カスタムサブネットを使っている場合は事前に`docker network inspect`の設定を控えておく。セットアップスクリプトを`inspect || create`のパターンで冪等化しておくと、同じ事故を防げる。

## 関連記事

- [dockerでネットワークを作成・接続する基本コマンド](/posts/docker-network-basics)
- [docker composeで「Found orphan containers」警告が出る原因と解決手順](/posts/docker-compose-orphan-containers)
- [docker composeでコンテナを停止・削除する（down）の使い方](/posts/docker-compose-down)
- [docker system pruneで不要リソースを一括削除する方法](/posts/docker-system-prune)
