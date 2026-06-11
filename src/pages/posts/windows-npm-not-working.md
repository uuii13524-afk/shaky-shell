---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでnpmコマンドが認識されない・動かない時の原因と解決方法を解説。PATHの確認・Node.jsの再インストール手順を紹介します。'
---

## やりたかったこと

AstroプロジェクトをWindowsで動かそうとして`npm install`を実行したら、コマンドが認識されないエラーが出た。Node.jsのインストーラーは昨日実行したはずで、インストール成功のメッセージも出ていたのになぜ使えないのかわからなかった。

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

「インストールしたのに使えない」という状況で、何が起きているのかの手がかりが全くなかった。再インストールしても同じエラーが出続けて、1時間以上同じことを繰り返した。

## 環境

- Windows 11 Home（22H2）
- Node.js 20.11.0（LTS版）
- PowerShell 7.4.1 / コマンドプロンプト
- VS Code 1.87.0

## 試したこと・うまくいかなかったこと

最初、「インストールが失敗したのかも」と思ってnodejs.orgからもう一度インストーラーをダウンロードして実行した。インストール完了のダイアログが出た。でも同じターミナルで`npm -v`を実行しても「認識されません」のエラーのままだった。インストールし直しても全く変わらなかった。なぜ変わらないのかが全く理解できなかった。

次に「PATH（パス）の問題かも」と思ったが、Windows 11で環境変数をどこから確認するのかわからなかった。昔のWindowsのように「マイコンピューター右クリック→プロパティ→詳細設定」という手順を試みたが、Windows 11では同じ場所に環境変数の設定が見当たらなかった。コントロールパネルを30分近く探し回った。

VS Codeのターミナルで試したらまた別のエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\Users\ユーザー名\AppData\Roaming\npm\npm.ps1 を
読み込むことができません。
```

最初のエラーとは全然違うメッセージで、これはPATHの問題ではなくPowerShellの実行ポリシーの問題だった。コマンドプロンプトでは出ないエラーが、PowerShellでは出る。VS CodeのターミナルはデフォルトでPowerShellを使うので、VS Codeでnpmが使えない場合はこのパターンのことがある。

「コマンドプロンプトで試してみよう」とcmdで`npm -v`を実行したら、今度は正常にバージョンが返ってきた。つまり問題はNode.jsのインストールではなく、VS CodeのターミナルがPowerShellを使っているせいだとわかった。

nvm（Node Version Manager）を使っている環境では、さらに別のはまり方をした。`nvm install 20`でNode.jsをインストールした後、`npm -v`を実行したら「認識されません」のエラーが出た。nvmでインストールしただけでは有効にならず、`nvm use 20`で明示的にバージョンを切り替えないといけないことを知らなかった。

## 解決策

原因は4パターン。上から順に確認していくのが早い。

### 原因1：ターミナルを再起動していない

Node.jsのインストール後に**同じターミナルをそのまま使い続けていると環境変数の変更が反映されない**。ターミナル（PowerShellやコマンドプロンプト）は起動時に環境変数を読み込む仕組みで、インストール後の変更は既存のターミナルには伝わらない。

インストール直後は一度ターミナルを完全に閉じて（×ボタンで終了）、新しく開き直す。

```bash
node -v
npm -v
```

これで通れば解決。VS Codeを使っている場合はVS Code自体も再起動する必要がある場合がある。

### 原因2：環境変数のPATHが通っていない

`node -v`でNodeのバージョンが表示されるのに`npm -v`が認識されない場合は、npmだけPATHが欠けている可能性がある。

Windows 11の環境変数確認方法：

1. スタートメニューを開いて「環境変数」と検索
2. 「システム環境変数の編集」を開く（コントロールパネルを探すより検索が圧倒的に早い）
3. 「詳細設定」タブ→「環境変数」ボタン
4. 「ユーザー環境変数」の`Path`を選択して「編集」
5. 以下のパスが含まれているか確認する：
   - `C:\Program Files\nodejs\`（Nodeのインストールパス）
   - `C:\Users\ユーザー名\AppData\Roaming\npm`（npmグローバルパス）

含まれていなければ「新規」で追加してOKを押す。その後ターミナルを再起動する。

PATHが設定されているか素早く確認したい場合：

```cmd
where npm
```

パスが出力されれば通っている。何も出力されない場合はPATHが通っていない。

PowerShellの場合は`Get-Command npm`で確認できる。

```powershell
Get-Command npm
```

`Source`の列にnpmのパスが表示されれば通っている。「コマンド 'npm' が見つかりません」というエラーが出る場合はPATHが通っていない。

### 原因3：PowerShellのスクリプト実行ポリシーが制限されている

VS CodeのターミナルでPowerShellを使っている時に出るエラー。コマンドプロンプトでは出ないが、PowerShellでは`.ps1`スクリプトの実行が制限されていることがある。

管理者としてPowerShellを開く（スタートメニュー→「PowerShell」と検索→「管理者として実行」）。

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

確認メッセージが出たら「Y」を入力してEnter。その後ターミナルを再起動する。

現在の実行ポリシーを確認するだけなら管理者権限不要。

```powershell
Get-ExecutionPolicy
```

`Restricted`や`AllSigned`が返ってきた場合は上記のコマンドで変更する。`RemoteSigned`が返ってくれば問題ない。

コマンドプロンプトを使う場合はこのエラーは出ないので、VS CodeのターミナルをPowerShellからコマンドプロンプトに切り替えるのも手。VS Codeのターミナル右上の「v」ボタンから「Command Prompt」を選択できる。

### 原因4：Node.jsがそもそもインストールされていない

`node -v`を実行してバージョンが出るか確認する。「認識されません」と出たらNode.js自体が入っていない。

`nodejs.org` からLTS版をダウンロードしてインストールする。インストール時に「Add to PATH」のチェックがデフォルトでオンになっているが、オフにしてしまっていると手動でPATHを追加する必要がある。

インストール後は必ずターミナルを再起動してから確認する。

インストール時の画面をよく見ていなかったせいで「Add to PATH」を外してしまっていたことがあった。アンインストールしてから「Add to PATH」のチェックが入った状態で再インストールする方が手っ取り早かった。

### nvmを使っている場合の注意

nvm（Node Version Manager）を使ってNode.jsを管理している場合、`nvm use`コマンドを実行するまでnpmが使えないことがある。

```cmd
nvm list          # インストール済みバージョン確認
nvm use 20.11.0  # バージョンを指定して切り替え
npm -v           # 確認
```

nvm経由でインストールしたNodeはシステムのPATHではなく、nvmの管理下のパスに入る。`nvm use`でアクティブにしていない状態ではnpmが見つからない。

`nvm use`を実行しても「No version found」が出る場合は、そのバージョンがインストールされていない。

```cmd
nvm list available  # インストール可能なバージョン一覧
nvm install 20.11.0  # インストール
nvm use 20.11.0
```

ターミナルを新しく開くたびに`nvm use`が必要になるのが面倒な場合は、`nvm alias default 20.11.0`でデフォルトバージョンを設定しておくと毎回実行しなくて済む。

## ハマったポイント

- インストールし直しても同じターミナルで実行したままでは絶対に直らない。環境変数はターミナル起動時にしか読み込まれないので、インストール後は必ずターミナルを完全に閉じて開き直す。これが一番多い原因だった。2回再インストールして2回とも同じターミナルで試すという無駄をやった
- Windows 11の「環境変数」設定がどこにあるか最初わからなかった。スタートメニューで「環境変数」と検索するのが一番早い。コントロールパネルを辿る方法は手順が多くて時間がかかる
- PowerShellとコマンドプロンプトでエラーの内容が違う。「スクリプトの実行が無効」エラーはPowerShell特有で、コマンドプロンプトでは出ない。VS CodeのターミナルはデフォルトでPowerShellを使うので気づきにくかった。「VS Codeでだけ動かない」という場合はこのパターンを疑う
- `npm`だけエラーになって`node`は動く場合がある。Node.jsのインストールパス（`C:\Program Files\nodejs\`）とnpmのグローバルパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）は別々にPATHに登録されているので、npmのパスだけ欠けていることがある
- nvmを使ってNode.jsのバージョンを切り替えた後に`npm`が使えなくなることがある。`nvm use 20`で明示的にバージョンを指定すると直る。nvmの使い方は[Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)を参照
- `where npm`コマンドでnpmのパスを確認できる。何も出力されない場合はPATHが通っていない。パスが出力される場合は実行ポリシーや権限の問題を疑う。PowerShellでは`Get-Command npm`でも確認できる
- Node.jsのインストール時に「Add to PATH」オプションをオフにしたまま進めてしまうとPATHが通らない。チェックを外したまま進んでしまった場合は、アンインストールしてから再インストールするのが一番速い。手動でPATHを追加するのは間違えやすい

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
