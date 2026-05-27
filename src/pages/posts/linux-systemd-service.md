---
title: 'systemdでサービスを管理する方法（start/stop/enable/status）'
date: '2026-05-24'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'systemd', 'サービス管理']
en_tags: ['Linux', 'systemd', 'service management']
description: 'systemctlコマンドでsystemdサービスをstart・stop・enable・disableする方法を解説。自作サービスのユニットファイル作成方法も紹介します。'
---

## やりたかったこと

nginxやDockerを再起動したり、OS起動時に自動起動させたかった。
Linuxではsystemdでサービスの起動・停止・自動起動を管理する。

## 基本コマンド

```bash
# サービスを起動
sudo systemctl start nginx

# サービスを停止
sudo systemctl stop nginx

# サービスを再起動
sudo systemctl restart nginx

# 設定を再読み込み（停止せずに反映）
sudo systemctl reload nginx
```

## サービスの状態を確認する

```bash
sudo systemctl status nginx
```

実行すると以下のような出力が得られる。

```
● nginx.service - A high performance web server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)
     Active: active (running) since ...
```

- `active (running)` → 起動中
- `inactive (dead)` → 停止中
- `failed` → 起動失敗

## 自動起動の設定

OS起動時にサービスを自動起動させるにはenableを使う。

```bash
# 自動起動を有効にする
sudo systemctl enable nginx

# 自動起動を無効にする
sudo systemctl disable nginx

# 現在の自動起動設定を確認
sudo systemctl is-enabled nginx
```

`enabled` と表示されれば自動起動が設定されている。

## ログを確認する（journalctl）

```bash
# サービスのログを表示
sudo journalctl -u nginx

# 最新のログだけ表示
sudo journalctl -u nginx -n 50

# リアルタイムでログを追う
sudo journalctl -u nginx -f

# 今日のログだけ表示
sudo journalctl -u nginx --since today
```

## カスタムサービスを作成する

自作スクリプトをsystemdのサービスとして登録できる。

```bash
sudo vim /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=My Application
After=network.target

[Service]
ExecStart=/home/user/myapp/start.sh
Restart=always
User=user
WorkingDirectory=/home/user/myapp

[Install]
WantedBy=multi-user.target
```

ファイルを作成したらデーモンをリロードしてから起動する。

```bash
# systemdに設定を再読み込みさせる
sudo systemctl daemon-reload

# サービスを起動して自動起動も設定
sudo systemctl enable --now myapp
```

## よく使うコマンドまとめ

```bash
# 全サービスの状態一覧
sudo systemctl list-units --type=service

# 起動失敗したサービスだけ表示
sudo systemctl --failed

# サービス定義ファイルの場所を確認
sudo systemctl cat nginx
```

## ハマったポイント

- `enable` だけでは起動しない。`start` も別途実行するか `enable --now` を使う
- カスタムサービスを追加・変更したら必ず `daemon-reload` が必要
- `ExecStart` にはフルパスで指定する（`/usr/bin/python3` など）
- `Restart=always` を設定するとクラッシュ時に自動で再起動する
- ログが溜まってディスクを圧迫する場合は `journalctl --vacuum-time=7d` で削除できる

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxのプロセス管理（ps/kill/top）](/posts/linux-process-management)
- [LinuxでCronジョブを設定して定期実行する方法](/posts/linux-cron-setup)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
