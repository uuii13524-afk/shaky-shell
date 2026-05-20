---
title: 'Windows Terminalをインストールして使いやすくする方法'
date: '2026-05-20'
category: 'Windows'
---

## やりたかったこと

Windowsのデフォルトのコマンドプロンプトは使いにくいのでWindows Terminalに乗り換えたかった。

## 環境

- Windows 10 / 11

## インストール

### Microsoft Storeからインストール

1. Microsoft Storeを開く
2. 「Windows Terminal」を検索
3. 「入手」をクリック

### wingetでインストール

```
winget install Microsoft.WindowsTerminal
```

## 基本的な使い方

### タブで複数のシェルを使う

上部の「+」ボタンで新しいタブを開く。
「∨」ボタンでシェルの種類を選べる。

- コマンドプロンプト
- PowerShell
- Windows PowerShell
- Ubuntu（WSL2がインストールされている場合）
- Git Bash（Gitがインストールされている場合）

### キーボードショートカット

```
Ctrl + Shift + T    # 新しいタブを開く
Ctrl + Shift + W    # タブを閉じる
Ctrl + Tab          # 次のタブへ
Ctrl + Shift + 1    # プロファイル1を開く
Alt + Shift + D     # 画面を分割
```

## 設定のカスタマイズ

設定ファイルを開く：`Ctrl + ,`

### デフォルトのシェルを変更

設定→スタートアップ→「既定のプロファイル」でシェルを選択する。

### フォントサイズを変更

設定→プロファイル→外観→「フォントサイズ」で変更する。

## ハマったポイント

- Windows 11はWindows Terminalがデフォルトでインストールされている
- WSL2をインストールするとUbuntuがプロファイルに自動追加される
- Git Bashを使いたい場合はGitのインストール時に「Add a Git Bash profile to Windows Terminal」を選ぶ

## 関連記事

- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
