---
title: 'Windowsで環境変数を設定・確認する方法'
date: '2026-05-18'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでシステム・ユーザー環境変数をGUIとコマンドプロンプトで設定・確認する方法を解説。PATHへの追加手順もわかりやすく紹介します。'
---

## GUIで設定する方法

1. 「環境変数」を検索→「システム環境変数の編集」
2. 「環境変数」→「Path」を選択→「編集」→「新規」
3. OKで閉じる→ターミナルを再起動

## コマンドで確認する方法

```powershell
$env:PATH -split ";"    # PowerShell
echo %PATH%             # コマンドプロンプト
```

## 一時的に設定する方法

```powershell
$env:MY_KEY = "my_value"    # PowerShell
set MY_KEY=my_value          # コマンドプロンプト
```

## ハマったポイント

- 変更後はターミナルを再起動しないと反映されない
- ユーザー環境変数はそのユーザーのみ有効

環境変数を設定してもnpmコマンドが動かない場合は[Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)でPATHの設定を確認してほしい。

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Windows Terminalをインストールして使いやすくする方法](/posts/windows-terminal-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
