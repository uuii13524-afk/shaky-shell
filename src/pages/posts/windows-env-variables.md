---
title: 'Windowsで環境変数を設定・確認する方法'
date: '2026-05-18'
category: 'Windows'
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

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Windows Terminalをインストールして使いやすくする方法](/posts/windows-terminal-setup)
