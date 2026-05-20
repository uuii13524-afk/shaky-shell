---
title: 'WindowsにDockerをインストールして動かすまでの手順'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

WindowsでDockerを使えるようにしたかった。
インストール後に詰まるポイントが多いのでまとめる。

## 環境

- Windows 10 / 11（64bit）

## 前提条件

- Windows 10 バージョン2004以降 または Windows 11
- BIOSで仮想化（Virtualization）が有効になっている
- WSL2がインストールされている

## 手順

### 1. WSL2をインストール

PowerShellを管理者として起動して以下を実行。

```
wsl --install
```

インストール完了後にWindowsを再起動する。

### 2. Docker Desktopをダウンロード

https://www.docker.com/products/docker-desktop にアクセスして
「Download for Windows」をクリック。

### 3. インストール

ダウンロードしたインストーラーを実行する。

設定はデフォルトのままでOK。
「Use WSL 2 instead of Hyper-V」にチェックが入っていることを確認する。

インストール完了後にWindowsを再起動する。

### 4. 動作確認

ターミナルで以下を実行。

```
docker --version
docker run hello-world
```

以下のように表示されれば成功。

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

## ハマったポイント

### BIOSの仮想化が無効になっている

以下のエラーが出る場合。

```
Hardware assisted virtualization and data execution protection must be enabled in the BIOS
```

PCの起動時にBIOS設定画面を開いて仮想化（Intel VT-x / AMD-V）を有効にする。
設定方法はPCのメーカーによって異なる。

### WSL2のインストールが必要

```
WSL 2 installation is incomplete
```

PowerShellを管理者として起動して以下を実行。

```
wsl --install
wsl --update
```

再起動後に再度Docker Desktopを起動する。

### Docker Desktopが起動しない

タスクマネージャーでDocker関連のプロセスをすべて終了してから再起動する。

## 基本コマンド

```
docker --version          # バージョン確認
docker ps                 # 起動中のコンテナ一覧
docker ps -a              # 全コンテナ一覧
docker images             # イメージ一覧
docker run hello-world    # 動作確認
docker stop コンテナID    # コンテナを停止
docker rm コンテナID      # コンテナを削除
```

## 補足

Docker DesktopはWindowsのスタートアップに登録される。
PCの起動が遅くなる場合はスタートアップから外してもOK。
その場合はDockerを使う前に手動でDocker Desktopを起動する。
