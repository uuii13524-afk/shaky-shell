---
title: 'WindowsにDockerをインストールして動かすまでの手順'
date: '2026-05-20'
category: 'Docker'
---

## やりたかったこと

WindowsでDockerを使えるようにしたかった。

## 環境

- Windows 10 / 11（64bit）

## 手順

### 1. WSL2をインストール

PowerShellを管理者として起動。

```
wsl --install
```

再起動する。

### 2. Docker Desktopをダウンロード

https://www.docker.com/products/docker-desktop から「Download for Windows」。

### 3. インストール

「Use WSL 2 instead of Hyper-V」にチェックが入っていることを確認してインストール。
完了後に再起動する。

### 4. 動作確認

```
docker --version
docker run hello-world
```

「Hello from Docker!」と表示されれば成功。

## ハマったポイント

### BIOSの仮想化が無効

```
Hardware assisted virtualization and data execution protection must be enabled in the BIOS
```

BIOSで Intel VT-x / AMD-V を有効にする。

### WSL2のインストールが必要

```
wsl --install
wsl --update
```

### Docker Desktopが起動しない

タスクマネージャーでDocker関連のプロセスをすべて終了してから再起動する。

## 基本コマンド

```
docker --version
docker ps
docker ps -a
docker images
docker run hello-world
docker stop コンテナID
docker rm コンテナID
```

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
