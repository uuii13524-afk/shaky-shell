---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでnpmコマンドが認識されない・動かない時の原因と解決方法を解説。PATHの確認・Node.jsの再インストール手順を紹介します。'
---

## やりたかったこと

AstroプロジェクトをWindowsで動かそうとして`npm install`を実行したら、コマンドが認識されないエラーが出た。Node.jsのインストーラーは前日に実行してインストール完了のダイアログも確認していたのに、なぜ使えないのかわからなかった。

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

「インストール失敗したのかも」と思って再インストールしたが、同じエラーが出続けた。もう一度インストーラーを実行して成功のダイアログが出ても、コマンドは認識されないままだった。「インストールし直せば直る」という思い込みで2回再インストールしてしまい、1時間以上同じことを繰り返した。

VS Codeのターミナルで試したら今度は全然違うエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\Users\ユーザー名\AppData\Roaming\npm\npm.ps1 を
読み込むことができません。
```

「コマンドが認識されない」エラーと「スクリプトの実行が無効」エラーは全然別の問題なのに、どちらも「npmが使えない」という状況として混乱した。

最終的にわかったのは「ターミナルの再起動」だけで解決するケースが圧倒的に多いということ。Node.jsをインストールした後に同じターミナルで確認しようとするのが最初のミスで、環境変数はターミナルの起動時にしか読み込まれない。この仕組みを知っていれば1時間の迷走は5分で終わっていた。

## 環境

- Windows 11 Home（22H2）
- Node.js 20.11.0（LTS版）
- PowerShell 7.4.1 / コマンドプロンプト
- VS Code 1.87.0

## 試したこと・うまくいかなかったこと

最初、「インストールが失敗したのかも」と思ってnodejs.orgからもう一度インストーラーをダウンロードして実行した。インストール完了のダイアログが出た。でも同じターミナルウィンドウで`npm -v`を実行しても「認識されません」のエラーのままだった。「インストールし直しても変わらないのは何かが根本的におかしいのでは」と思い込んで、Windowsの「アプリと機能」からNode.jsを削除してから再インストールするという作業を繰り返した。2回目も同じターミナルで確認したので、もちろん変わらなかった。

次に「PATH（パス）の問題かも」と思ったが、Windows 11で環境変数をどこから確認するのかわからなかった。昔のWindowsのように「マイコンピューター右クリック→プロパティ→詳細設定」という手順を試みたが、Windows 11では同じ場所に環境変数の設定が見当たらなかった。「詳細システム設定」や「システムの詳細設定」などを検索しながらコントロールパネルを30分近く探し回った。

VS Codeのターミナルで試したら、「認識されません」エラーとは全く別のエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\Users\ユーザー名\AppData\Roaming\npm\npm.ps1 を
読み込むことができません。
```

このエラーはPATHの問題ではなくPowerShellのスクリプト実行ポリシーの問題だとわかったのは後になってから。コマンドプロンプト（cmd）では出ないエラーがPowerShellでは出る。VS CodeのターミナルはデフォルトでPowerShellを使うので、VS Codeでnpmが使えない場合はこのパターンが多い。

「コマンドプロンプトで試してみよう」とcmdで`npm -v`を実行したら、正常にバージョンが返ってきた。

```
10.2.4
```

つまりNode.jsのインストールは成功していて、PowerShellの実行ポリシーだけが問題だった。最初から`node -v`と`npm -v`をコマンドプロンプトとPowerShellの両方で試していれば、すぐに問題の切り分けができた。

別の日に、Microsoft StoreからインストールしたNode.jsとnodejs.orgからインストールしたNode.jsが両方入っていて干渉し合うケースも経験した。`where node`を実行したら複数のパスが返ってきた。

```
C:\Users\ユーザー名\AppData\Local\Microsoft\WindowsApps\node.exe
C:\Program Files\nodejs\node.exe
```

Microsoft Storeのバージョンが先に見つかってしまい、更新管理がStore経由になる上にバージョンが古かった。開発用途にはnodejs.orgからのインストールまたはnvmを使うほうが制御しやすいとわかった。

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

全スコープの設定を確認したい場合：

```powershell
Get-ExecutionPolicy -List
```

`CurrentUser`の行が`Undefined`になっている場合は、設定がまだ入っていない状態。`-Scope CurrentUser`で設定し直す。

コマンドプロンプトを使う場合はこのエラーは出ないので、VS CodeのターミナルをPowerShellからコマンドプロンプトに切り替えるのも手。VS Codeのターミナル右上の「v」ボタンから「Command Prompt」を選択できる。VS Code 1.85以降では「既定のプロファイル」としてCommand Promptを設定しておくと毎回切り替える必要がなくなった。

`-Scope CurrentUser`で設定した実行ポリシーは現在のユーザーにのみ適用される。職場のPCや共有PCでは`-Scope LocalMachine`ではなく`-Scope CurrentUser`を使うのが安全で、他のユーザーの設定に影響を与えない。

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

### npmのグローバルパッケージがインストールされているのに使えない場合

`npm install -g`でグローバルインストールしたパッケージのコマンドが使えない場合も、npmグローバルのパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）がPATHに通っていないことが多い。

```cmd
npm root -g
```

このコマンドでグローバルパッケージのインストール先を確認できる。出力されたパスの親ディレクトリ（`npm`フォルダがある場所）がPATHに入っているか確認する。

グローバルパッケージのコマンドが「認識されません」になる場合は、PATHに`C:\Users\ユーザー名\AppData\Roaming\npm`が追加されているか確認する。Node.jsのインストールで自動追加されることが多いが、インストールオプションの組み合わせによっては追加されないことがあった。

## ハマったポイント

- インストールし直せば直ると思っていたが、同じターミナルで確認し続けている限り絶対に直らなかった。環境変数はターミナルの起動時にしか読み込まれないので、インストール後は必ずターミナルを完全に閉じて開き直す必要があった。2回再インストールして2回とも同じターミナルで試すという無駄をしてしまった
- Windows 11の「環境変数」設定がコントロールパネルに見つからないと思って30分探し回ったが、実際にはスタートメニューで「環境変数」と検索するのが一番早かった。コントロールパネルを辿る旧来の方法は手順が多くて時間がかかる上に、Windows 11では表示が変わっていてたどり着きにくかった
- PowerShellとコマンドプロンプトで全く同じエラーが出ると思っていたが、「スクリプトの実行が無効」エラーはPowerShell特有で、コマンドプロンプトでは出なかった。VS CodeのターミナルはデフォルトでPowerShellを使うので「VS Codeでだけnpmが使えない」という現象が起きた。最初にコマンドプロンプトとPowerShellを両方試していれば問題の切り分けがすぐできた
- `npm`だけエラーになって`node`は動く場合があると知らなかった。Node.jsのインストールパス（`C:\Program Files\nodejs\`）とnpmのグローバルパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）は別々にPATHに登録されているので、npmのパスだけ欠けていることがある。「Nodeが動くからインストールは成功している」と思い込んで問題の切り分けが遅れた
- Microsoft Storeからインストールしたnode.exeが優先されてしまい、`nodejs.org`からインストールした方が使われない状態になっていた。`where node`を実行して初めて2つのパスが存在していることに気づいた。Store版を削除するか、Windowsの「アプリの実行エイリアス」でStoreのNode.jsを無効にするかで解決した。「インストールが重複していることがある」という発想が最初なかった
- nvmを使ってNode.jsのバージョンを管理する場合、`nvm use`でアクティブにしないとnpmが使えないと思っていなかった。nvmはNodeのバージョンを切り替えるツールで、使いたいバージョンを`nvm use`で明示的に指定する必要がある。「nvmを入れた後はいつでもnpmが使える」と思っていた
- `where npm`コマンドでnpmのパスを確認できることを知らなかった。パスが出力されればPATHが通っている、何も出力されない場合はPATHが通っていない、という確認方法を最初から知っていれば切り分けが早かった。PowerShellでは`Get-Command npm`で同様の確認ができる
- Node.jsのインストール時に「Add to PATH」オプションがデフォルトでオンになっていることを知らなかった。インストール画面をよく読まずに「Next」を連打しているとオフにしてしまうことはないが、あえて外した記憶はないのにPATHが通っていないという状況になっていた。チェックを外したままインストールした場合はアンインストールして再インストールするのが一番速い
- VS Codeを「ターミナルを再起動しても直らない」と思っていたが、原因はVS Code自体を再起動していなかったことだった。VS Codeはアプリ起動時に環境変数を取得するので、VS Codeが起動したままではターミナルを何度再起動しても古い環境変数が引き継がれ続ける。VS Code全体を終了してから開き直すのが確実だった
- PowerShellの実行ポリシーを`-Scope CurrentUser`で設定しても反映されないと思っていたが、実際には管理者権限で開いたPowerShellと通常のPowerShellで設定のスコープが異なっていた。通常のPowerShellで`Get-ExecutionPolicy -List`を実行すると全スコープの設定を確認でき、`CurrentUser`が`Undefined`になっている場合は設定がまだ入っていない状態だとわかった

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
