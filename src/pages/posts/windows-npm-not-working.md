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

最終的にわかったのは「ターミナルの再起動」だけで解決するケースが圧倒的に多いということ。Node.jsをインストールした後に同じターミナルで確認しようとするのが最初のミスで、環境変数はターミナルの起動時にしか読み込まれない。この仕組みを理解していれば1時間の迷走は5分で終わっていた。

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

別の日に、Microsoft StoreからインストールしたNode.jsとnodejs.orgからインストールしたNode.jsが両方入っていて干渉し合うケースも経験した。`where node`を実行したら複数のパスが返ってきて、「どちらのNodeが使われているのか」が混乱した。Microsoft Storeのバージョンは更新管理がStore経由になるので、開発用途にはnodejs.orgからのインストールまたはnvmを使うほうが制御しやすかった。

nvm（nvm-windows）を使っていた時に`nvm use`を実行せずに`npm`を使おうとして「認識されません」になったこともあった。nvm経由でインストールしたNodeはnvm管理下のパスに入るので、`nvm use`でアクティブにしないとPATHに出てこない。

## 解決策

原因は4パターン。上から順に確認していくのが早い。

### 原因1：ターミナルを再起動していない

Node.jsのインストール後に**同じターミナルをそのまま使い続けていると環境変数の変更が反映されない**。ターミナル（PowerShellやコマンドプロンプト）は起動時に環境変数を読み込む仕組みで、インストール後の変更は既存のターミナルには伝わらない。

インストール直後は一度ターミナルを完全に閉じて（×ボタンで終了）、新しく開き直す。

```bash
node -v
npm -v
```

これで通れば解決。VS Codeを使っている場合はVS Code自体も再起動する必要がある場合がある。VS Codeのターミナルだけ閉じて開き直してもVS Code本体が古い環境変数を持ち続けていることがあった。VS Code全体を終了してから開き直すのが確実。

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

PATHを追加した後は、変更を反映させるためにターミナルを再起動する必要がある。環境変数の変更は新しく開いたターミナルから有効になる。

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

VS Code 1.85以降では、PowerShellとCommand Promptの切り替えがターミナルのタイトルバー横の「+」ボタン横の「v」から選べる。「既定のプロファイル」としてCommand Promptを設定しておくと毎回切り替える必要がなくなった。

### 原因4：Node.jsがそもそもインストールされていない

`node -v`を実行してバージョンが出るか確認する。「認識されません」と出たらNode.js自体が入っていない。

`nodejs.org` からLTS版をダウンロードしてインストールする。インストール時に「Add to PATH」のチェックがデフォルトでオンになっているが、オフにしてしまっていると手動でPATHを追加する必要がある。

インストール後は必ずターミナルを再起動してから確認する。

Microsoft Storeからもインストールできるが、パスの管理方法が通常のインストーラー版と異なる。`where node`を実行した時にStoreのパス（`C:\Users\ユーザー名\AppData\Local\Microsoft\WindowsApps\node.exe`のような形式）が返ってくる場合はStore版が優先されている。開発用途には`nodejs.org`のLTS版を使うほうがトラブルが少ない。

Microsoft Storeバージョンを削除するには、Windowsの「設定」→「アプリ」→「インストールされているアプリ」から「Node.js」を検索して削除する。削除後にnodejs.orgのLTS版をインストールし直す。

### nvmを使っている場合の注意

nvm（Node Version Manager）を使ってNode.jsを管理している場合、`nvm use`コマンドを実行するまでnpmが使えないことがある。

```cmd
nvm list          # インストール済みバージョン確認
nvm use 20.11.0  # バージョンを指定して切り替え
npm -v           # 確認
```

nvm経由でインストールしたNodeはシステムのPATHではなく、nvmの管理下のパスに入る。`nvm use`でアクティブにしていない状態ではnpmが見つからない。

Windowsでnvmを使う場合は`nvm-windows`（`github.com/coreybutler/nvm-windows`）を使う。LinuxやmacOS用のnvmとは別のツールで、インストール方法も管理方法も異なる。両方を混同していたために設定が壊れたことがあった。

nvm-windowsを使っている場合、コマンドプロンプトで`nvm use`は動くがPowerShellで`nvm use`を実行しても「nvm not found」になることがあった。nvm-windowsのインストール後はコマンドプロンプトで操作するか、PowerShellの実行ポリシーを設定し直す必要があった。

## ハマったポイント

- インストールし直しても同じターミナルで実行したままでは絶対に直らない。環境変数はターミナル起動時にしか読み込まれないので、インストール後は必ずターミナルを完全に閉じて開き直す。これが一番多い原因だった。2回再インストールして2回とも同じターミナルで試すという無駄をやった
- Windows 11の「環境変数」設定がどこにあるか最初わからなかった。スタートメニューで「環境変数」と検索するのが一番早い。コントロールパネルを辿る方法は手順が多くて時間がかかる
- PowerShellとコマンドプロンプトでエラーの内容が違う。「スクリプトの実行が無効」エラーはPowerShell特有で、コマンドプロンプトでは出ない。VS CodeのターミナルはデフォルトでPowerShellを使うので気づきにくかった。「VS Codeでだけ動かない」という場合はこのパターンを疑う
- `npm`だけエラーになって`node`は動く場合がある。Node.jsのインストールパス（`C:\Program Files\nodejs\`）とnpmのグローバルパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）は別々にPATHに登録されているので、npmのパスだけ欠けていることがある
- Microsoft Storeからインストールしたnode.exeが優先されてしまい、`nodejs.org`からインストールした方が使われない状態になっていたことがあった。`where node`で複数のパスが返ってくる場合はStore版を削除するか、Windowsの「アプリの実行エイリアス」でStoreのNode.jsを無効にする
- nvmを使ってNode.jsのバージョンを切り替えた後に`npm`が使えなくなることがある。`nvm use 20`で明示的にバージョンを指定すると直る。nvmの使い方は[Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)を参照
- `where npm`コマンドでnpmのパスを確認できる。何も出力されない場合はPATHが通っていない。パスが出力される場合は実行ポリシーや権限の問題を疑う。PowerShellでは`Get-Command npm`でも確認できる
- Node.jsのインストール時に「Add to PATH」オプションをオフにしたまま進めてしまうとPATHが通らない。チェックを外したまま進んでしまった場合は、アンインストールしてから再インストールするのが一番速い。手動でPATHを追加するのは間違えやすい
- VS Codeを「ターミナルを再起動しても直らない」ケースでは、VS Code本体を完全終了して開き直す必要があった。VS Codeはアプリ起動時に環境変数を取得するので、VS Codeが起動したままではターミナルを再起動しても古い環境変数が引き継がれることがある

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
