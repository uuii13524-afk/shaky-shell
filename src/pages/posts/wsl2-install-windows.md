---
title: 'WindowsでWSL2をインストールする方法'
date: '2026-05-11'
category: 'Windows'
---

## 手順

### 1. WSL2をインストール

PowerShellを管理者として起動。

```
wsl --install
```

再起動する。

### 2. Ubuntuの初期設定

再起動後にUbuntuが起動。ユーザー名とパスワードを設定する。

### 3. 動作確認

```
wsl
```

## よく使うWSLコマンド

```
wsl --shutdown         # WSLを停止
wsl --update           # WSLを更新
wsl --list --verbose   # インストール済み一覧
```

## ハマったポイント

- BIOSでIntel VT-x / AMD-Vを有効にする
- Windows Updateで最新版にしてから実行する

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windows Terminalをインストールして使いやすくする方法](/posts/windows-terminal-setup)
