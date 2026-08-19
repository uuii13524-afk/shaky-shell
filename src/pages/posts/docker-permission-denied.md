---
title: 'Dockerでpermission deniedが出た時の対処法'
date: '2026-07-18'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'sudoなしでdocker psを実行するとpermission deniedエラーが出る症状を解説します。chmod 666では再起動で戻ってしまう原因を説明し、usermod -aG dockerとセッション再作成で恒久的に解決する手順を紹介します。'
ja_tags: ['Docker', 'permission denied', 'docker.sock', 'usermod']
en_tags: ['Docker', 'permission denied', 'docker.sock', 'usermod']
---

## やりたかったこと（または「症状」）

新しく借りたVPSにDockerを`apt`でインストールし、公式ドキュメント通りに動作確認をしようとした。`sudo`なしで`docker ps`を叩いたところ、コンテナ一覧どころか以下のエラーで止まった。

```text
docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.45/containers/json": dial unix /var/run/docker.sock: connect: permission denied
```

インストール自体は`Client: Docker Engine - Community`と`Server:`のバージョン情報が両方表示されており失敗していないように見えたので、なぜ`docker ps`単体がこけるのか最初は理解できなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS（さくらのVPS）
- Docker Engine: 26.1.4
- Docker Compose: v2.27.0
- ログインユーザー: `deploy`（`sudo`権限はあるが非root）
- インストール方法: `get.docker.com`公式スクリプト経由

## 試したこと

最初は毎回`sudo`を付ければいいと考え、`sudo docker ps`で回避していた。これは動くが、後で`docker-compose.yml`を`deploy`ユーザーの権限で自動デプロイするGitHub Actionsのself-hosted runnerから叩いた際、runnerのスクリプトに`sudo`のパスワードプロンプトを挟めず、そのままジョブが停止してしまった。

次に、根本解決のつもりで`/var/run/docker.sock`のパーミッションを直接書き換えた。

```bash
sudo chmod 666 /var/run/docker.sock
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES
```

このときは`sudo`なしで`docker ps`が通り、解決したと思って作業を進めた。ところが翌日にVPSを再起動したところ、まったく同じ`permission denied`エラーが復活した。`chmod`で直接変更したパーミッションは、dockerdがソケットを再生成するたびに初期値へ戻されるため、再起動のたびに設定し直す必要があり、恒久対策にならないと分かった。

## 原因

Dockerデーモンは`/var/run/docker.sock`というUnixソケット経由でクライアントからの要求を受け付ける。このソケットは`root:docker`の所有・グループで作成され、パーミッションは`660`（所有者とグループのみ読み書き可）に設定される。ログインユーザーが`docker`グループに所属していない場合、root権限を持つプロセス（`sudo`経由）以外はこのソケットにアクセスできず、`permission denied`となる。`chmod`でその場のパーミッションを変えても、dockerdの起動・再起動時にsystemdのソケットユニットがデフォルト値でソケットを作り直すため、変更は永続しない。

## 解決方法

### 1. ユーザーをdockerグループに追加する

```bash
sudo usermod -aG docker $USER
```

このコマンド自体はエラーなく完了するが、この時点ではまだ現在のシェルセッションのグループ情報は更新されていない。

### 2. グループ変更を反映させる

ログアウトして再ログインするか、`newgrp`でグループ変更をそのセッションに反映する。

```bash
newgrp docker
groups
```

```text
deploy sudo docker
```

`groups`の出力に`docker`が含まれていれば、現在のシェルが`docker`グループの権限を持った状態になっている。ログインシェルのグループ情報はログイン時に決定されるため、`usermod`だけでは反映されず、セッションの再作成（再ログインまたは`newgrp`）が必要になる。

### 3. sudoなしで動作確認する

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES
```

`sudo`を付けずに`docker ps`がエラーなく完了すれば、`docker.sock`へのアクセス権が正しく付与されている。この方法はsystemdによるソケット再生成の影響を受けないため、再起動後も設定し直す必要がない。

## ハマったポイント

- `usermod -aG docker $USER`を実行した直後、同じターミナルのまま`docker ps`を叩いて「直っていない」と勘違いした。グループ情報はログインシェル起動時に固定されるため、同一セッション内では反映されない
- `chmod 666 /var/run/docker.sock`で一時的に解決したように見えたが、VPSを再起動した翌日に同じエラーが再発した。dockerdの再起動でソケットが作り直され、パーミッションが`660`に戻っていた
- `docker`グループへの追加は事実上rootと同等の権限を与えることになる、という点を後から知った。`docker`グループのユーザーはホストのファイルシステムをマウントしたコンテナを起動できるため、root権限昇格の経路になり得る
- GitHub Actionsのself-hosted runnerを`deploy`ユーザーで動かしていた際、runnerのプロセスが`usermod`実行前に起動していたため、グループ変更後もrunnerサービス自体を再起動するまで反映されなかった

## よくある質問

**Q: `docker`グループにユーザーを追加するのはセキュリティ的に安全ですか？**
`docker`グループのメンバーは、ホストの任意のディレクトリをマウントしたコンテナを起動できるため、実質的にroot権限を持つのと同等になる。信頼できる個人開発環境や検証用VPSでは一般的な運用だが、複数人が共有するサーバーでは慎重に権限を絞る必要がある。

**Q: サーバーを再起動せずに今すぐ反映したいです。**
`newgrp docker`を実行すれば、そのシェルセッション内だけグループ変更を即座に反映できる。別のターミナルやSSHセッションには影響しないため、恒久的に反映したい場合は最終的にログアウト・再ログインが必要になる。

**Q: WSL2上のDocker Desktopでも同じ手順で直りますか？**
Docker DesktopのWSL2統合を使っている場合、`/var/run/docker.sock`はWindows側のDocker Desktopエンジンからプロキシされているため、WSL内で`usermod`しても解決しないことがある。その場合はDocker Desktopの設定にある「Resources > WSL Integration」で対象のディストリビューションを有効化する必要がある。

## 関連記事

- [docker psコマンドでコンテナ一覧を確認する方法](/posts/docker-ps-command)
- [docker execでコンテナ内にbashで入る・コマンドを実行する方法](/posts/docker-exec-bash)
- [Linuxのユーザー管理コマンドまとめ](/posts/linux-user-management)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [VPSにDockerをインストールしてWebサーバーを構築する方法](/posts/vps-docker-setup)
