---
title: 'WindowsでWSL2をインストールする方法'
date: '2026-05-20'
category: 'Windows'
---

## やりたかったこと

WindowsでLinuxのコマンドを使いたかった。
WSL2（Windows Subsystem for Linux 2）を使うとWindows上でLinux環境を動かせる。

## 環境

- Windows 10 バージョン2004以降
- Windows 11

## 手順

### 1. WSL2をインストール

PowerShellを管理者として起動して以下を実行。

```
wsl --install
```

これだけでWSL2とUbuntuが自動でインストールされる。

完了後にWindowsを再起動する。

### 2. Ubuntuの初期設定

再起動後にUbuntuが自動で起動する。
ユーザー名とパスワードを設定する（Linuxのパスワードなのでこのパスワードを覚えておく）。

### 3. 動作確認

```
wsl
```

またはスタートメニューから「Ubuntu」を起動する。

Linuxのターミナルが起動すれば成功。

## インストール済みのディストリビューションを確認

```
wsl --list --verbose
```

## よく使うWSLコマンド

```
wsl                    # WSLを起動
wsl --shutdown         # WSLを停止
wsl --update           # WSLを更新
wsl --list --verbose   # インストール済み一覧
wsl --set-default-version 2  # デフォルトをWSL2に設定
```

## ハマったポイント

### BIOSの仮想化が無効

以下のエラーが出る場合。

```
Please enable the Virtual Machine Platform Windows feature and ensure virtualization is enabled in the BIOS.
```

BIOSでIntel VT-x / AMD-Vを有効にする。

### Windows Updateが必要

古いバージョンのWindowsではWSL2が動かない。
Windows Updateで最新版にしてから再試行する。

### Ubuntuが起動しない

```
wsl --update
wsl --shutdown
wsl
```

## WindowsとLinux間のファイルアクセス

WSL2からWindowsのファイルにアクセスする。

```bash
cd /mnt/c/Users/ユーザー名/
```

WindowsからWSL2のファイルにアクセスする。
エクスプローラーのアドレスバーに以下を入力。

```
\\wsl$\Ubuntu\home\ユーザー名
```

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
