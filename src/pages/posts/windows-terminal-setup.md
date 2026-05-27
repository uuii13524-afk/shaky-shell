---
title: 'Windows Terminalをインストールして使いやすくする方法'
date: '2026-05-15'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windows Terminalをインストールして見た目や起動設定をカスタマイズする方法を解説。WSL2・PowerShell・コマンドプロンプトとの連携も紹介します。'
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

WSL2を使うとWindows Terminal上でLinuxコマンドが使えるようになる。[WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)と組み合わせるとWindowsでLinux開発環境が揃う。

## 関連記事

- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windowsで環境変数を設定・確認する方法](/posts/windows-env-variables)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">

## おすすめのプログラミングスクール

Windowsで開発環境を整えたら、次のステップとしてプログラミングスクールで体系的に学ぶのもおすすめです。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+7N2A9E+529E+5YRHE" rel="nofollow">【Winスクール】</a>は講師が寄り添う個人レッスン形式のスクールで、未経験からでも即戦力のプログラマーを目指せます。無料カウンセリングも受付中です。
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3VRB+7N2A9E+529E+5YRHE" alt="">
