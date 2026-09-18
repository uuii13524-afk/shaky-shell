---
title: 'サーバー再起動後にCannot connect to the Docker daemonが出る原因と解決手順'
date: '2026-09-18'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: 'VPSを再起動した後、docker psがCannot connect to the Docker daemonで失敗する症状を解説します。systemctl statusでdocker.serviceがinactiveになっている原因を特定し、enable --nowで再起動後も自動起動する状態に直す手順を紹介します。'
ja_tags: ['Docker', 'systemd', 'Cannot connect to the Docker daemon']
en_tags: ['Docker', 'systemd', 'Cannot connect to the Docker daemon']
---

## やりたかったこと（症状）

さくらのVPSで新規契約したUbuntu 24.04サーバーに`apt`でDockerをインストールし、いくつかコンテナを起動して動作確認をしていた。この時点では`docker ps`も`docker run`も問題なく動いていた。

数日後、カーネルアップデートを適用するために`sudo reboot`でサーバーを再起動した。再起動後、SSHで入り直して`docker ps`を実行したところ、以下のエラーで止まった。

```bash
docker ps
```

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

再起動前まで普通に動いていたコンテナ管理コマンドが軒並み使えなくなったので、最初はDockerのインストール自体が壊れたのかと思い、再インストールを検討した。

## 環境

- OS: Ubuntu 24.04.1 LTS（さくらのVPS）
- Docker Engine: 27.1.1
- Docker Compose: v2.29.1
- インストール方法: `sudo apt install docker.io`
- ログインユーザー: `deploy`（`sudo`権限あり、`docker`グループにも所属済み）

## 試したこと

まず、ユーザー権限の問題を疑った。以前どこかで見た`docker.sock`のパーミッションエラーと似ていると思ったからだ。しかし今回は権限エラーの文言（`permission denied`）ではなく、そもそも接続できないという文言だったため、`sudo`を付けても同じエラーになった。

```bash
sudo docker ps
```

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

`sudo`を付けても変わらないということは、権限の問題ではなく、Dockerデーモン自体が起動していない可能性が高いと判断した。次に`/var/run/docker.sock`の存在を確認した。

```bash
ls -la /var/run/docker.sock
```

```text
ls: cannot access '/var/run/docker.sock': No such file or directory
```

ソケットファイル自体が存在しなかった。これはデーモンが一度も起動していない（あるいは起動に失敗している）ことを示す。ここで初めて、再インストールではなくサービスの起動状態を確認する方向に切り替えた。

## 原因

`systemctl status`でdocker.serviceの状態を確認した。

```bash
sudo systemctl status docker
```

```text
○ docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; disabled; preset: enabled)
     Active: inactive (dead)
```

`disabled`となっており、さらに`Active: inactive (dead)`だった。`apt install docker.io`でインストールした直後は、パッケージのpostinstallスクリプトがその場でdocker.serviceを起動してくれるため、インストール直後の動作確認では問題なく`docker`コマンドが使えていた。しかし、起動時に自動起動する設定（`systemctl enable`）まではされていなかったため、`reboot`でOSを再起動した際にdocker.serviceが立ち上がらず、結果として`docker.sock`も作られない状態になっていた。

つまり、今回の症状は「Dockerが壊れた」のではなく、「Dockerサービスがブート時に自動起動する設定になっていなかった」ことが原因だった。`apt install`直後にdockerコマンドが動くことと、docker.serviceが有効化（enable）されていることは別問題であり、この違いに気づかないまま再インストールを検討していたら無駄な作業になるところだった。

## 解決手順

### 1. docker.serviceの現在の状態を確認する

```bash
sudo systemctl status docker
```

```text
○ docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; disabled; preset: enabled)
     Active: inactive (dead)
```

`disabled`と`inactive (dead)`の両方を確認し、自動起動設定と現在の起動状態の両方に問題があることを把握した。

### 2. docker.serviceを起動し、自動起動を有効化する

```bash
sudo systemctl enable --now docker
```

```text
Synchronizing state of docker.service with SxS service manager...
Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /usr/lib/systemd/system/docker.service.
```

`enable --now`を使うことで、「今すぐ起動する」と「次回以降のブート時にも自動起動する」を1コマンドで同時に設定できる。`start`だけだと今回は動くが次の再起動でまた同じ症状に戻ってしまう。

### 3. サービスの状態を再確認する

```bash
sudo systemctl status docker
```

```text
● docker.service - Docker Application Container Engine
     Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-09-18 10:12:03 UTC; 5s ago
```

`enabled`かつ`active (running)`になっていることを確認した。

### 4. docker.sockが作られているか確認する

```bash
ls -la /var/run/docker.sock
```

```text
srw-rw---- 1 root docker 0 Sep 18 10:12 /var/run/docker.sock
```

先ほど存在しなかったソケットファイルが作成されていた。

## 動作確認

`docker ps`が権限エラー・接続エラーなしで実行できることを確認した。

```bash
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

さらに、念のため実際にもう一度再起動して、再発しないことを確認した。

```bash
sudo reboot
```

```bash
# 再ログイン後
docker ps
```

```text
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

再起動後も`docker ps`がエラーなく応答することを確認できた。

## まとめ

- `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?`は、権限エラー（`permission denied`）ではなく、デーモン自体が起動していない・ソケットが存在しないことを示すエラー。`sudo`を付けても変わらない場合はこちらを疑う。
- `apt install docker.io`直後にdockerコマンドが動くのは、postinstallスクリプトがその場で一時的にサービスを起動しているだけで、ブート時の自動起動（`enable`）とは別。再起動して初めて設定漏れが発覚するパターンに注意する。
- `sudo systemctl enable --now docker`で「即時起動」と「次回起動時の自動起動」を同時に設定できる。同様のsystemd管理サービス（nginxやpostgresqlなど）でも、`start`だけで済ませず`enable --now`を使う癖をつけておくと再起動後のトラブルを防げる。

## よくある質問

**Q: `docker.sock`が存在しない場合、必ず`enable --now`で直りますか？**
Docker Engineのインストール自体が壊れていない前提であれば、多くの場合直ります。`systemctl status docker`の出力に`failed`や具体的なエラーログが出ている場合は、`journalctl -u docker --no-pager`でより詳細なログを確認し、設定ファイル（`/etc/docker/daemon.json`）の記述ミスなど別の原因を切り分ける必要があります。

**Q: なぜ`apt install`の時点で自動起動まで設定してくれないのですか？**
Debian/Ubuntu系のパッケージは、インストール直後にサービスを起動することはpostinstallスクリプトの一般的な挙動ですが、systemdの`enable`（ブート時自動起動）は別のフラグとして管理されています。ディストリビューションやパッケージのバージョンによって挙動が異なることがあるため、インストール後は`systemctl is-enabled docker`で明示的に確認するのが確実です。

**Q: Docker Compose経由で自動起動しているコンテナも同じ影響を受けますか？**
受けます。docker.service自体が起動していなければ、`restart: always`を設定したコンテナも含めて一切起動しません。再起動運用があるサーバーでは、`docker.service`の`enable`状態をデプロイ手順のチェック項目に含めておくことをおすすめします。

## 関連記事

- [Dockerでpermission deniedが出た時の対処法](/posts/docker-permission-denied)
- [docker system pruneで不要リソースを一括削除する方法](/posts/docker-system-prune)
- [systemdでサービスを管理する方法（start/stop/enable/status）](/posts/linux-systemd-service)
- [Dockerで「System has not been booted with systemd」の原因と解決手順](/posts/docker-systemd-not-booted)
- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)
