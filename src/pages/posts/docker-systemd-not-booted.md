---
title: 'Dockerで「System has not been booted with systemd」の原因と解決手順'
date: '2026-07-29'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: '軽量VPSやLXCコンテナにDockerをインストール後、systemctl start dockerを実行すると「System has not been booted with systemd as init system」で失敗する症状を解説。PID 1がsystemdでない環境の原因と、dockerdを直接起動する解決手順を紹介します。'
ja_tags: ['Docker', 'systemd', 'dockerd', 'PID 1']
en_tags: ['Docker', 'systemd', 'dockerd', 'PID 1']
---

## やりたかったこと（または「症状」）

契約している軽量プランのVPSに公式手順どおりDockerをインストールし、動作確認のために`docker ps`を実行したところ、デーモンに接続できないというエラーが出た。

```bash
docker ps
```

```text
failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /var/run/docker.sock: connect: no such file or directory
```

デーモンが起動していないのだろうと判断し、`systemctl`でDockerサービスを起動しようとしたが、こちらも別のエラーで失敗した。

```bash
systemctl start docker
```

```text
System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down
```

インストール自体はエラーなく完了していたし、`docker --version`でクライアントのバージョンも正しく表示される。それなのにサービスの起動コマンドがそもそも受け付けられない状態で、最初は何が起きているのか分からなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- 実行環境: 軽量プランのVPS（LXCベースのコンテナ仮想化。KVMではなくOSレベル仮想化のプラン）
- Docker: 29.3.1（公式インストールスクリプト経由）
- init: PID 1がsystemdではなく、コンテナのランチャープロセスになっている

## 試したこと

まず`service`コマンド（SysVinit経由）でも同じように起動できないか試した。

```bash
service docker start
```

```text
* Docker is not running
```

```bash
service docker status
```

```text
* Docker is not running
```

`service`コマンド自体はエラーなく実行できたが、実際にはDockerは起動していなかった。次に、そもそもこのサーバーでsystemdがPID 1として動いているか確認した。

```bash
ps -p 1 -o pid,comm
```

```text
    PID COMMAND
      1 tini
```

PID 1が`systemd`ではなく`tini`（軽量な初期化プロセス）になっていた。これで`systemctl`が「System has not been booted with systemd as init system」と言っていた理由が分かった。このVPSはKVM等のフル仮想化ではなく、コンテナ型の軽量仮想化プランで、ホスト側のinitプロセスをそのまま使う構成になっており、systemdそのものが存在しない、あるいはPID 1として動いていない環境だった。

## 原因

`systemctl`や`service`コマンドは、systemdのinitプロセス（PID 1）にsocket経由で命令を送ることでサービスを起動・停止している。今回の環境ではPID 1が`tini`であり、systemdがそもそも稼働していなかったため、`systemctl start docker`は「systemdとして起動していないので操作できない」というエラーで即座に失敗していた。`dpkg`や公式インストールスクリプトはDockerパッケージ自体（`dockerd`本体やCLI、`docker.service`ユニットファイル）を正しく配置してくれるが、そのユニットファイルを実際に起動する仕組み（systemd）が環境に存在しなければ、サービスとしての自動起動はできない。つまり原因は「Dockerのインストールミス」ではなく、「このVPSプランがsystemdベースのinitを持たない仮想化方式である」という環境側の制約だった。

## 解決方法

### 1. PID 1がsystemdかどうかを確認する

```bash
ps -p 1 -o comm=
```

`systemd`以外（`tini`や`init`など）が返ってきた場合、`systemctl`／`service`でのDocker管理はそもそも成立しない。

### 2. dockerdを直接起動する

systemdに頼らず、`dockerd`をバックグラウンドプロセスとして直接起動する。

```bash
dockerd > /var/log/dockerd.log 2>&1 &
```

数秒待ってからログの末尾を確認し、`API listen on /var/run/docker.sock`が出ていれば起動成功。

```bash
tail -5 /var/log/dockerd.log
```

```text
time="2026-07-29T00:10:25.601757834Z" level=info msg="Docker daemon" commit=f78c987 containerd-snapshotter=true storage-driver=overlayfs version=29.3.1
time="2026-07-29T00:10:25.640565695Z" level=info msg="Daemon has completed initialization"
time="2026-07-29T00:10:25.640910959Z" level=info msg="API listen on /var/run/docker.sock"
```

### 3. 動作確認する

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

エラーなく空のコンテナ一覧が返ってきて、デーモンに接続できるようになった。

### 4. 再起動後も自動で立ち上がるようにする

`&`でバックグラウンド起動しただけでは、サーバー再起動後に再度手動で`dockerd`を叩く必要がある。恒常的に使う場合は、環境が対応していればsupervisord等のプロセスマネージャに`dockerd`を登録するか、起動スクリプト（`/etc/rc.local`相当）に起動コマンドを追記して、サーバー起動時に自動実行されるようにしておく。

## ハマったポイント

- `service docker start`が「エラーなく」終了したように見えたため、一瞬起動できたのかと勘違いした。実際には裏でsystemd未検出により何もしていなかった。`service docker status`まで必ず確認する必要があった
- インストールスクリプトが成功メッセージを出していたため、Docker自体のインストール手順を何度もやり直してしまい、時間を無駄にした。原因はインストールではなくinitシステム側にあった
- `dockerd`をフォアグラウンドで動かしたままSSHセッションを切断すると、プロセスごと終了してDockerが止まってしまう。`&`でバックグラウンド化するか、`nohup`／`disown`を併用する必要がある

## よくある質問

**Q: このエラーはWSLでも出ますか？**
WSL1やsystemdを有効化していないWSL2ディストリビューションでも、PID 1がsystemdでないため同様のエラーが出ることがある。WSL2でsystemdサポートが有効になっている場合は通常どおり`systemctl`が使える。

**Q: `dockerd`を直接起動する方法は本番運用でも問題ないですか？**
恒常的に稼働させるなら、SSH切断で落ちないようプロセスマネージャ（supervisord等）で管理することを強く推奨する。手動での`&`起動はあくまで動作確認や一時的な用途向け。

**Q: そもそもこの仮想化方式のVPSでDocker（Docker in Docker相当）を使うこと自体に制約はありますか？**
コンテナ型仮想化の環境では、カーネル機能の一部がホストと共有されるため、ネットワークやcgroup周りで通常のKVM環境と挙動が異なる場合がある。今回のケースでは`docker ps`自体は正常に動いたが、環境によってはさらに追加の対応が必要になることもある。

## 関連記事

- [VPSにDockerをインストールしてWebサーバーを構築する方法](/posts/vps-docker-setup)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [dockerコマンドがpermission deniedになる時の対処法](/posts/docker-permission-denied)
- [docker-composeの基本的な使い方](/posts/docker-compose-basic)
- [不要なDockerイメージを整理する方法](/posts/docker-image-cleanup)
