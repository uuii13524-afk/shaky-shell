---
title: 'Windowsでnpmコマンドが動かない時の対処法'
date: '2026-05-06'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
description: 'Windowsでnpmコマンドが認識されない・動かない時の原因と解決方法を解説。PATHの確認・Node.jsの再インストール手順を紹介します。'
---

## ひとことで言うと

```cmd
# まずターミナルを完全に閉じて開き直す（これだけで直るケースが多い）
# 開き直した後
node -v
npm -v
```

Node.jsインストール後に同じターミナルで確認しても絶対に直らない。ターミナルは起動時にしか環境変数を読み込まない。インストール後は**ターミナルを閉じて開き直す**のが最初の一手。

---

## やりたかったこと

AstroプロジェクトをWindowsで動かそうとして`npm install`を実行したら、コマンドが認識されないエラーが出た。Node.jsのインストーラーは前日に実行してインストール完了のダイアログも確認していたのに、なぜ使えないのかわからなかった。

```
'npm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

「インストール失敗したのかも」と思って再インストールしたが、同じエラーが出続けた。2回再インストールして2回とも同じターミナルウィンドウで確認したので、もちろん変わらなかった。

途中で「本当にインストールされているのか？」と思って`C:\Program Files\nodejs\`フォルダをエクスプローラーで開いた。`npm.cmd`というファイルが存在していた。試しにフルパスで`"C:\Program Files\nodejs\npm" -v`を実行したらバージョンが正常に返ってきた。「インストールは成功していて、PATHが通っていないせいで見つからないだけ」だと確信した瞬間だった。

VS Codeのターミナルで試したら今度は全然違うエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\Users\ユーザー名\AppData\Roaming\npm\npm.ps1 を
読み込むことができません。
```

「コマンドが認識されない」エラーと「スクリプトの実行が無効」エラーは全然別の問題なのに、どちらも「npmが使えない」という状況として混乱した。

最終的にわかったのは、Node.jsをインストールした後に同じターミナルで確認しようとするのが最初のミスで、環境変数はターミナルの起動時にしか読み込まれないということだった。

## 環境

- Windows 11 Home（22H2）
- Node.js 20.11.0（LTS版）
- PowerShell 7.4.1 / コマンドプロンプト
- VS Code 1.87.0

## 試したこと・うまくいかなかったこと

**Node.jsを再インストールした → 同じターミナルで確認したので変わらなかった**

「インストールが失敗したのかも」と思ってnodejs.orgからもう一度インストーラーをダウンロードして実行した。インストール完了のダイアログが出た。でも同じターミナルウィンドウで`npm -v`を実行しても「認識されません」のエラーのままだった。「インストールし直しても変わらないのは何かが根本的におかしい」と思い込んで、Windowsの「アプリと機能」からNode.jsを削除してから再インストールするという作業を繰り返した。2回とも同じターミナルで確認したので、もちろん変わらなかった。

**VS Codeのターミナルで試したら別のエラーが出た**

「コマンドプロンプトは古い、VS Codeのターミナルで試してみよう」と思って試したら、全く別のエラーが出た。

```
npm : このシステムではスクリプトの実行が無効になっているため、
ファイル C:\Users\ユーザー名\AppData\Roaming\npm\npm.ps1 を
読み込むことができません。
```

「コマンドが認識されない」エラーとは別の問題で混乱した。後でわかったのは、VS CodeのターミナルはデフォルトでPowerShellを使っていて、PowerShellはスクリプトの実行ポリシーでnpmが弾かれていたということだった。コマンドプロンプト（cmd）に切り替えて`npm -v`を実行したら正常にバージョンが返ってきた。つまりNode.jsのインストールは成功していて、PowerShellの実行ポリシーだけが問題だった。

**Microsoft Storeと通常インストールのNodeが両方入っていた**

別の日に`where node`を実行したら複数のパスが返ってきた。

```
C:\Users\ユーザー名\AppData\Local\Microsoft\WindowsApps\node.exe
C:\Program Files\nodejs\node.exe
```

Microsoft Storeのバージョンが先に見つかってしまい、更新管理がStore経由になる上にバージョンが古かった。「where nodeで複数パスが出る」という可能性を最初は考えていなかった。

解決策はWindowsの設定から「アプリの実行エイリアス」を無効にすること。「設定 → アプリ → アプリの実行エイリアス」を開くと「アプリインストーラー - node.exe」という項目があるのでオフにする。これでStore版のNodeが無視されてnodejs.org版が優先されるようになった。アンインストールするより素早く切り替えられた。

**`npm install`は成功するのに`npm run dev`でエラーが出た**

node_modulesのインストール後に`npm run dev`を実行したら以下のエラーが出た。

```
Error: EPERM: operation not permitted, mkdir 'C:\Users\ユーザー名\project\node_modules\.vite'
```

OneDriveの同期フォルダの中にプロジェクトを作っていたのが原因だった。OneDriveがファイルをクラウドに同期しようとする処理と、Viteがキャッシュファイルを書き込もうとする処理がぶつかってEPERMエラーになっていた。プロジェクトをOneDrive外の`C:\dev\`フォルダに移してから起動したら正常に動いた。「インストールは通るのにrunでだけ失敗する」という場合はOneDriveやDropboxの同期フォルダに入っていないか確認するといい。

## 解決策

原因は4パターン。上から順に確認していくのが早い。

### 原因1：ターミナルを再起動していない

Node.jsのインストール後に**同じターミナルをそのまま使い続けていると環境変数の変更が反映されない**。ターミナルは起動時に環境変数を読み込む仕組みで、インストール後の変更は既存のターミナルには伝わらない。

インストール直後は一度ターミナルを完全に閉じて（×ボタンで終了）、新しく開き直す。

```bash
node -v
npm -v
```

これで通れば解決。VS Codeを使っている場合はVS Code自体も再起動する。VS Codeのターミナルだけ閉じて開き直してもVS Code本体が古い環境変数を持ち続けていることがあったので、VS Code全体を終了してから開き直すのが確実。

### 原因2：環境変数のPATHが通っていない

Windows 11の環境変数確認方法：

1. スタートメニューで「環境変数」と検索（コントロールパネルを探すより圧倒的に早い）
2. 「システム環境変数の編集」を開く
3. 「詳細設定」タブ→「環境変数」ボタン
4. 「ユーザー環境変数」の`Path`を選択して「編集」
5. 以下のパスが含まれているか確認：
   - `C:\Program Files\nodejs\`
   - `C:\Users\ユーザー名\AppData\Roaming\npm`

PATHが設定されているか素早く確認したい場合：

```cmd
where npm
```

パスが出力されれば通っている。何も出力されない場合はPATHが通っていない。PowerShellの場合は`Get-Command npm`で確認できる。

### 原因3：PowerShellのスクリプト実行ポリシーが制限されている

VS CodeのターミナルでPowerShellを使っている時に出るエラー。コマンドプロンプトでは出ないが、PowerShellでは`.ps1`スクリプトの実行が制限されていることがある。

管理者としてPowerShellを開く（スタートメニュー→「PowerShell」と検索→「管理者として実行」）。

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

確認メッセージが出たら「Y」を入力してEnter。その後ターミナルを再起動する。

コマンドプロンプトを使う場合はこのエラーは出ないので、VS CodeのターミナルをPowerShellからコマンドプロンプトに切り替えるのも手。VS Codeのターミナル右上の「v」ボタンから「Command Prompt」を選択できる。

### 原因4：Node.jsがそもそもインストールされていない

`node -v`を実行してバージョンが出るか確認する。「認識されません」と出たらNode.js自体が入っていない。

`nodejs.org` からLTS版をダウンロードしてインストールする。インストール後は必ずターミナルを再起動してから確認する。

Microsoft Storeからもインストールできるが、パスの管理方法が通常のインストーラー版と異なる。`where node`を実行した時にStoreのパス（`C:\Users\ユーザー名\AppData\Local\Microsoft\WindowsApps\node.exe`のような形式）が返ってくる場合はStore版が優先されている。開発用途には`nodejs.org`のLTS版を使うほうがトラブルが少ない。

### nvmを使っている場合の注意

nvm（Node Version Manager）を使ってNode.jsを管理している場合、`nvm use`コマンドを実行するまでnpmが使えないことがある。

```cmd
nvm list          # インストール済みバージョン確認
nvm use 20.11.0  # バージョンを指定して切り替え
npm -v           # 確認
```

Windowsでnvmを使う場合は`nvm-windows`を使う。LinuxやmacOS用のnvmとは別のツールで、インストール方法も管理方法も異なる。

### npmコマンドが急に動かなくなった場合

フルパスで直接実行できるか確認する：

```cmd
"C:\Program Files\nodejs\npm" -v
```

これで正常にバージョンが返ってきた場合は、インストール自体は壊れていなくてPATHの問題だとわかる。

## ハマったポイント

- インストールし直せば直ると思っていたが、同じターミナルで確認し続けている限り絶対に直らなかった。環境変数はターミナルの起動時にしか読み込まれないので、インストール後は必ずターミナルを完全に閉じて開き直す必要があった。2回再インストールして2回とも同じターミナルで確認するという時間を無駄にした
- PowerShellとコマンドプロンプトで全く同じエラーが出ると思っていたが、「スクリプトの実行が無効」エラーはPowerShell特有で、コマンドプロンプトでは出なかった。VS CodeのターミナルはデフォルトでPowerShellを使うので「VS Codeでだけnpmが使えない」という現象が起きた。最初からコマンドプロンプトとPowerShellの両方で試していれば問題の切り分けがすぐできた
- `node -v`は通るのに`npm -v`が「認識されません」になるパターンがあるとは知らなかった。Node.jsのインストールパス（`C:\Program Files\nodejs\`）とnpmのグローバルパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）は別々にPATHに登録されているので、npmのパスだけ欠けていることがある。「Nodeが動くからインストールは成功している」と思い込んで問題の切り分けが遅れた
- `where node`を実行したら複数のパスが返ってきて、Microsoft Storeのnode.exeが先に見つかってしまっていた。Store版を削除するか、Windowsの「アプリの実行エイリアス」でStoreのNode.jsを無効にするかで解決した。「インストールが重複していることがある」という発想が最初なかった
- VS Codeのターミナルだけ再起動しても直らないと思っていたが、原因はVS Code自体を再起動していなかったことだった。VS Codeはアプリ起動時に環境変数を取得するので、VS Codeが起動したままではターミナルを何度再起動しても古い環境変数が引き継がれ続ける。VS Code全体を終了してから開き直すのが確実だった

## よくある質問

**Q: ターミナルを再起動しても直りません。**
VS Codeを使っている場合はVS Code自体も終了して開き直す。VS Codeはアプリ起動時に環境変数を取得するため、VS Codeのターミナルだけ閉じても古い環境変数が引き継がれる。VS Code全体を終了 → 再起動が確実。

**Q: `node -v` は通るのに `npm -v` が「認識されません」と出ます。**
Node.jsのインストールパス（`C:\Program Files\nodejs\`）とnpmのグローバルパス（`C:\Users\ユーザー名\AppData\Roaming\npm`）は別々にPATHに登録されている。npmのパスだけ欠けていることがある。環境変数の設定でこのnpmのパスが含まれているか確認する。

**Q: VS CodeのターミナルでPowerShellの実行ポリシーエラーが出ます。**
管理者としてPowerShellを開いて `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` を実行する。またはVS Codeのターミナルをコマンドプロンプト（cmd）に切り替えると、このエラーは出なくなる。ターミナル右上の「v」ボタンから「Command Prompt」を選択できる。

**Q: `where node` で複数のパスが返ってきます。**
Microsoft Store版とnodejs.org版が両方インストールされている状態。Windowsの「アプリと機能」からMicrosoft Store版のNode.jsを削除するか、「アプリの実行エイリアス」でStoreのNode.jsを無効にする。開発用途はnodejs.orgのLTS版を使う方がPATHの管理が素直で問題が少ない。

---

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Windowsのターミナルでパスにスペースがある時の対処法](/posts/windows-path-with-spaces)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
