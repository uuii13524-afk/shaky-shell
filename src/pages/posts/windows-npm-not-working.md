---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでnpmコマンドが認識されない・動かない時の原因と解決方法を解説。PATHの確認・Node.jsの再インストール手順を紹介します。'
---

## やりたかったこと

AstroプロジェクトをWindowsで動かそうとして`npm install`を実行したら、コマンドが認識されないエラーが出た。Node.jsはインストールしたはずなのに、なぜかnpmが使えなかった。

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

## 環境

- Windows 11 Home（22H2）
- Node.js 20.11.0（LTS版）
- PowerShell 7.4.1 / コマンドプロンプト
- VS Code 1.87.0

## 試したこと・うまくいかなかったこと

最初、「Node.jsをインストールしたのになぜ動かないのか」と思ってもう一度nodejs.orgからインストーラーをダウンロードして実行した。インストール完了のメッセージが出たのに、同じターミナルで`npm -v`を実行してもエラーのままだった。インストールし直しても意味がなかった。

次に「PATHが通っていないのかも」と思って環境変数を確認しようとしたが、どこを見ればいいかわからなかった。「コンピューター」を右クリックして「システム」→「詳細設定」という昔のUIを探したが、Windows 11の場合は別の場所にあって迷った。

PowerShellで実行しようとしたら別のエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\...\npm.ps1 を読み込むことができません。
```

これはPATHの問題ではなくPowerShellのスクリプト実行ポリシーの問題で、別の対処が必要だった。

## 解決策

原因は以下の4パターン。上から順に確認する。

### 原因1：ターミナルを再起動していない

Node.jsのインストール後にターミナルを閉じて開き直していない場合、環境変数の変更が反映されない。インストール直後は必ずターミナルを一度閉じて開き直す。

```bash
# 再起動後に確認
node -v
npm -v
```

これで通れば解決。

### 原因2：Node.jsがインストールされていない

`node -v`を実行してバージョンが出るか確認する。「認識されません」と出たらNode.js自体が入っていない。`https://nodejs.org` からLTS版をダウンロードしてインストールする。

### 原因3：環境変数のPATHが通っていない

Windows 11の環境変数の確認方法：

1. スタートメニューを開いて「環境変数」と検索
2. 「システム環境変数の編集」を開く
3. 「詳細設定」タブ→「環境変数」ボタン
4. 「ユーザー環境変数」の`Path`を選択して「編集」
5. Node.jsのインストールパス（`C:\Program Files\nodejs\`）が含まれているか確認

含まれていない場合は「新規」で追加してOKを押す。その後ターミナルを再起動する。

### 原因4：PowerShellのスクリプト実行ポリシーが制限されている

PowerShellで以下のエラーが出た場合はこのパターン。

```
npm : このシステムではスクリプトの実行が無効になっているため...
```

管理者としてPowerShellを開いて実行する。

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

確認メッセージが出たら「Y」を入力してEnter。その後ターミナルを再起動すると`npm`が使えるようになった。

コマンドプロンプトを使う場合はこのエラーは出ないので、PowerShellをやめてコマンドプロンプトに切り替えるのも解決策のひとつ。

## ハマったポイント

- インストールし直しても同じターミナルで実行したままでは絶対に直らない。環境変数はターミナル起動時に読み込まれるので、インストール後は必ずターミナルを閉じて開き直す
- Windows 11の「環境変数」設定がどこにあるか最初わからなかった。スタートメニューで「環境変数」と検索するのが一番早い。コントロールパネルを辿るのは無駄に時間がかかる
- PowerShellとコマンドプロンプトでエラーの内容が違う。PowerShellでは実行ポリシーエラーが出ることがあるが、コマンドプロンプトでは出ない。VS CodeのターミナルはデフォルトでPowerShellを使うので注意
- `npm`だけエラーになって`node`は動く場合がある。Node.jsのインストールパスとnpmのパスが別々にPATHに登録されているのが原因で、npmだけパスが欠けていることがある
- nvmを使ってNode.jsのバージョンを切り替えた後に`npm`が使えなくなることがある。`nvm use 20`で明示的にバージョンを指定すると直る。nvmの使い方は[Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)を参照

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
