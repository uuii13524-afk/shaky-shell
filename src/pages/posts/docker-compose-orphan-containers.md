---
title: 'docker composeで「Found orphan containers」警告が出る原因と解決手順'
date: '2026-07-31'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'docker compose up/down実行時に「Found orphan containers」という警告が出て、compose.ymlから削除したはずのサービスのコンテナが残り続ける症状を解説。--remove-orphansでの安全な削除手順と、名前付きボリュームを誤って消さないための注意点を紹介します。'
ja_tags: ['Docker', 'Docker Compose', '孤立コンテナ']
en_tags: ['Docker', 'Docker Compose', 'orphan containers']
---

## やりたかったこと（または「症状」）

`myapp`というディレクトリで、`web` / `worker` / `redis` の3サービスを`compose.yaml`で管理していた。`worker`サービスを別のホストに移すことになったので、`compose.yaml`から`worker`の定義を削除し、`docker compose up -d`で残りのサービスだけを起動し直そうとした。

```bash
docker compose up -d
```

```text
[+] Running 3/3
 ✔ Container myapp-redis-1  Started
 ✔ Container myapp-web-1    Started
WARN[0000] Found orphan containers ([myapp-worker-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
```

コマンド自体はエラーで止まらず`web`と`redis`は正常に起動したが、削除したはずの`worker`コンテナについて警告が出た。実際に確認すると、`worker`のコンテナはまだ動き続けていた。

```bash
docker ps --filter "label=com.docker.compose.project=myapp" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

```text
NAMES              IMAGE              STATUS
myapp-web-1        myapp-web:latest   Up 5 seconds
myapp-redis-1      redis:7            Up 5 seconds
myapp-worker-1     myapp-worker:old   Up 3 days
```

`compose.yaml`からサービス定義を消しただけでは、そのサービスの既存コンテナは自動では止まらないらしいと分かった。

## 環境

- OS: Ubuntu 22.04.4 LTS
- Docker Engine: 26.1.3
- Docker Compose: v2.27.0（`docker compose`プラグイン、旧`docker-compose`単体コマンドではない）
- プロジェクト名: ディレクトリ名から自動決定される`myapp`（`COMPOSE_PROJECT_NAME`未設定）
- 削除したサービス: `worker`（`compose.yaml`から定義を削除済み、別ホストへ移設予定）

## 試したこと

まず、`docker compose down`を実行すればプロジェクトに紐づくコンテナがまとめて消えるはずだと考えた。

```bash
docker compose down
```

```text
[+] Running 2/2
 ✔ Container myapp-web-1    Removed
 ✔ Container myapp-redis-1  Removed
```

`web`と`redis`は削除されたが、`worker`については何のメッセージも出なかった。念のため`docker ps`で確認すると、`myapp-worker-1`はまだ動いていた。

```bash
docker ps --filter "label=com.docker.compose.project=myapp"
```

```text
CONTAINER ID   IMAGE               COMMAND      STATUS
7f1a2b3c4d5e   myapp-worker:old    "node worker.js"   Up 3 days
```

`down`はcompose.yamlに書かれているサービスしか対象にせず、ファイルから消えた`worker`は対象外になっていた。手動で`docker rm -f`すれば消えることは分かったが、それだと今後同じことが起きるたびに手作業が必要になる。恒久的な解決策を探すことにした。

## 原因

Docker Composeは、起動したコンテナに`com.docker.compose.project`（プロジェクト名）と`com.docker.compose.service`（サービス名）というラベルを付けて管理している。`docker compose up`や`docker compose down`を実行するとき、Composeは現在の`compose.yaml`に定義されているサービス名の一覧と、実際にそのプロジェクトラベルを持つコンテナの一覧を突き合わせる。

このとき、コンテナ側には存在するがcompose.yamlの定義には存在しないサービス（今回の`worker`）が見つかると、それを「孤立コンテナ（orphan container）」として警告するが、**デフォルトでは削除しない**。これは、意図せずサービスを消して必要なコンテナやそれに紐づくデータを失う事故を防ぐための安全側の挙動で、`up`・`down`どちらのサブコマンドでも共通の仕様だった。つまり今回のケースは壊れているのではなく、「ファイルから消しただけでは実行中のコンテナは自動で片付かない」というComposeの意図した安全設計だった。

## 解決方法

### 1. 現在のプロジェクトに紐づくコンテナを確認する

```bash
docker ps -a --filter "label=com.docker.compose.project=myapp" --format "table {{.Names}}\t{{.Label \"com.docker.compose.service\"}}\t{{.Status}}"
```

`compose.yaml`に定義がないサービス名を持つコンテナがないか確認する。

### 2. 孤立コンテナに紐づくボリュームの有無を確認する

削除前に、名前付きボリュームを使っていないか必ず確認する。ボリュームはコンテナを消しても自動では消えない一方、うっかり残すとディスクを圧迫するため、両方向で事前確認が必要。

```bash
docker inspect myapp-worker-1 --format '{{ range .Mounts }}{{ .Name }} {{ end }}'
```

### 3. `--remove-orphans`フラグ付きで実行する

不要なコンテナだと確認できたら、`--remove-orphans`を付けて実行する。

```bash
docker compose up -d --remove-orphans
```

```text
[+] Running 2/2
 ✔ Container myapp-redis-1  Started
 ✔ Container myapp-web-1    Started
[+] Removing orphan containers
 ✔ Container myapp-worker-1  Removed
```

`down`側で使う場合も同様。

```bash
docker compose down --remove-orphans
```

### 4. 不要になった名前付きボリュームを個別に削除する（該当する場合のみ）

孤立コンテナ削除後もボリュームは残るため、本当に不要と確認できたものだけ削除する。

```bash
docker volume ls --filter "label=com.docker.compose.project=myapp"
docker volume rm myapp_worker-data
```

## 動作確認

```bash
docker compose up -d --remove-orphans
docker ps --filter "label=com.docker.compose.project=myapp"
```

```text
NAMES            IMAGE              STATUS
myapp-web-1      myapp-web:latest   Up 10 seconds
myapp-redis-1    redis:7            Up 10 seconds
```

`WARN`行が出なくなり、`docker ps`にも`worker`関連のコンテナが表示されなくなったことを確認できた。

## ハマったポイント

- `docker compose down`は「プロジェクト全体を掃除するコマンド」だと思い込んでいたが、実際には**現在のcompose.yamlに書かれているサービスのみ**が対象で、ファイルから消えたサービスのコンテナは対象外になる
- `--remove-orphans`は確認プロンプトなしで即座にコンテナを削除する。複数の`compose.yaml`を`-f`で分割運用していて、同じプロジェクト名を共有している場合、意図した以外のファイルのサービスまで「孤立」と誤判定されて消えるリスクがあるため、事前に`docker ps`で対象を確認してから実行するべきだった
- 名前付きボリュームはコンテナを消しても残り続ける。逆に言えば、コンテナを消してもデータは消えないので焦る必要はないが、放置するとディスク容量を圧迫するため、不要と確定した時点で`docker volume rm`まで含めて片付ける習慣にした

## よくある質問

**Q: `--remove-orphans`は常に付けて運用してよいですか？**
単一の`compose.yaml`だけをそのプロジェクト名で運用しているなら基本的に安全。ただし複数ファイルを`-f`で組み合わせて同じプロジェクト名を共有している構成では、意図しないサービスまで削除対象になり得るため、事前に`docker ps`で対象コンテナを確認してから実行するのが安全。

**Q: なぜdocker composeはデフォルトで孤立コンテナを自動削除しないのですか？**
サービス定義をファイルから誤って消してしまった場合などに、実行中のコンテナや紐づくデータを意図せず失う事故を防ぐための安全側のデフォルト仕様のため。

**Q: 孤立コンテナが使っていた名前付きボリュームはどうなりますか？**
コンテナを削除してもボリューム自体は自動では消えない。不要と確認できたら`docker volume rm`または`docker volume prune`で別途削除する必要がある。

## 関連記事

- [docker composeの基本コマンドまとめ](/posts/docker-compose-basic)
- [docker compose downの使い方と注意点](/posts/docker-compose-down)
- [docker compose logsでログを確認する方法](/posts/docker-compose-logs)
- [docker system pruneでの不要データ削除](/posts/docker-system-prune)
- [不要なDockerイメージを削除する方法](/posts/docker-image-cleanup)
