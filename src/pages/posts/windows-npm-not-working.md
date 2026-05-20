---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-20'
category: 'Windows'
---

## 症状

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

または

```
npm : このシステムではスクリプトの実行が無効になっているため
```

## 環境

- Windows 10 / 11
- Node.js
- PowerShell / コマンドプロンプト

## 原因と解決方法

### 原因1：Node.jsがインストールされていない

```
node -v
npm -v
```

認識されない場合はhttps://nodejs.org からLTS版をインストール。

### 原因2：環境変数のPATHが通っていない

1. Windowsの検索で「環境変数」を検索
2. 「Path」を選択して「編集」
3. Node.jsのインストールパスを追加（例：C:\Program Files\nodejs\）
4. ターミナルを再起動

### 原因3：PowerShellのスクリプト実行ポリシーが制限されている

PowerShellを管理者として起動して実行。

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 原因4：ターミナルを再起動していない

インストール後にターミナルを再起動する。

## 確認コマンド

```
node -v
npm -v
```

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)
