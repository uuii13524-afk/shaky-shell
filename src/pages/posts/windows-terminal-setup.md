---
title: 'Windows Terminalをインストールして使いやすくする方法'
date: '2026-05-15'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
---

## インストール

```
winget install Microsoft.WindowsTerminal
```

またはMicrosoft Storeから「Windows Terminal」を検索してインストール。

## キーボードショートカット

```
Ctrl + Shift + T    # 新しいタブを開く
Ctrl + Shift + W    # タブを閉じる
Alt + Shift + D     # 画面を分割
```

## デフォルトのシェルを変更

設定（Ctrl + ,）→スタートアップ→「既定のプロファイル」で変更。

## ハマったポイント

- Windows 11はデフォルトでインストール済み
- WSL2をインストールするとUbuntuが自動追加される

## 関連記事

- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windowsで環境変数を設定・確認する方法](/posts/windows-env-variables)
