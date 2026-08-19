---
title: 'Node.jsでEADDRINUSEエラーが出た時の対処法'
date: '2026-07-21'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'nodemonでNode.jsを再起動するとError: listen EADDRINUSE: address already in use :::3000が発生。原因はゾンビ化した旧プロセスがポートを占有していたことで、lsof -i :3000でPIDを特定しkill -9で解決した手順を解説します。'
ja_tags: ['Node.js', 'EADDRINUSE', 'ポート使用中', 'express']
en_tags: ['Node.js', 'EADDRINUSE', 'port in use', 'express']
---

## やりたかったこと（または「症状」）

WSL2上でExpress製のAPIサーバーをnodemonで動かしながら開発していた。コード修正中にサーバーが一度クラッシュしたので、`Ctrl + C`でターミナルを止め、`npm run dev`を打ち直して再起動しようとしたところ、次のエラーが出てサーバーが起動できなくなった。

```text
node:events:495
      throw er; // Unhandled 'error' event
      ^

Error: listen EADDRINUSE: address already in use :::3000
    at Server.setupListenHandle [as _listen2] (node:net:1740:16)
    at listenInCluster (node:net:1788:12)
    at Server.listen (node:net:1876:7)
    at Function.listen (/home/user/api/node_modules/express/lib/application.js:635:24)
    at Object.<anonymous> (/home/user/api/src/index.js:42:10)
Emitted 'error' event on Server instance at:
    at emitErrorNT (node:net:1923:8)
    at process.processTicksAndRejections (node:internal/process/task_queues.js:83:21) {
  code: 'EADDRINUSE',
  errno: -98,
  syscall: 'listen',
  address: '::',
  port: 3000
}
```

さっきまで動いていたのと同じコードで、変更したのはコントローラー1ファイルだけだった。ポート番号もコード上は3000のまま変えていないのに、なぜ「使用中」と言われるのか分からなかった。

## 環境

- OS: Windows 11 23H2 + WSL2（Ubuntu 22.04.3 LTS）
- Node.js: v20.11.1
- npm: 10.2.4
- フレームワーク: Express 4.19.2 + nodemon 3.1.0
- エディタ: VSCode（WSL Remote拡張経由でターミナル操作）

## 試したこと

最初はVSCodeのターミナルタブをゴミ箱アイコンで強制的に閉じれば、動いていたプロセスも一緒に終了するはずだと考えた。タブを閉じて新しいターミナルを開き、`npm run dev`を実行し直した。

```bash
npm run dev
```

```text
Error: listen EADDRINUSE: address already in use :::3000
```

結果は変わらず同じエラーだった。ターミナルタブを閉じただけでは、そのシェルから起動した子プロセス（nodemonがforkしたnode本体）が確実に終了するとは限らないと分かった。今回のケースでは、直前のクラッシュがコントローラー内の非同期処理で発生した未処理の例外によるもので、nodemonがwatchによる再起動処理に入る前に古いnodeプロセスがゾンビ状態のままポート3000を掴み続けていた。

次に`ps aux | grep node`でnode関連プロセスを確認したところ、`node src/index.js`というプロセスが2つ表示され、片方はターミナルを閉じたはずの古いプロセスだった。

```bash
ps aux | grep node
```

```text
user      1823  0.3  1.2 923456 48120 ?        Sl   21:02   0:02 node src/index.js
user      2941  0.0  0.0  17456  1092 pts/3    S+   21:14   0:00 grep node
```

新しいプロセス（2941）はgrepコマンド自体で、肝心の古いnodeプロセス（1823）が端末を切り離した後もバックグラウンドで生き残っていた。

## 原因

TCPのポートは同時に1つのプロセスしかbind（待ち受け）できない。Node.jsの`Server.listen()`はOS側にポート番号の予約を要求するが、既に別のプロセスが同じポートをbind済みだと、OSはそれを拒否し、Node.jsは`EADDRINUSE`（Address already in use）エラーを投げてプロセスを終了する。今回のケースでは、直前のクラッシュ時にnodemonの子プロセスへ正しくSIGTERMが伝わらず、親のシェルやターミナルタブを閉じても、切り離された（detachされた）子プロセスだけがバックグラウンドで存続していた。そのプロセスがポート3000を握ったままだったため、新しく起動しようとしたプロセスがbindできずに同じエラーを繰り返していた。

## 解決方法

### 1. ポートを使っているプロセスを特定する

```bash
sudo lsof -i :3000
```

```text
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
node    1823 user   20u  IPv6  34521      0t0  TCP *:3000 (LISTEN)
```

`lsof -i :ポート番号`で、指定ポートを実際にLISTEN状態で保持しているプロセスのPIDが分かる。今回はPID 1823が犯人だった。

### 2. 該当プロセスを終了する

```bash
kill -9 1823
```

```bash
sudo lsof -i :3000
```

実行後は`lsof`の出力が空になり、ポート3000を保持しているプロセスがいなくなったことを確認できた。`kill -9`はプロセスに終了処理の猶予を与えず強制終了するシグナルで、シェルとの親子関係が切れて通常のシグナルが届かなくなったプロセスを止める際に有効。

### 3. npm run devで再起動する

```bash
npm run dev
```

```text
[nodemon] starting `node src/index.js`
Server listening on port 3000
```

ポートの占有がなくなったことで、Node.jsのServerが正常にbindできるようになり、サーバーが起動した。

## ハマったポイント

- ターミナルタブを閉じただけではプロセスが必ず終了するとは限らず、`ps aux`で確認するまでバックグラウンドで生存し続けていることに気づかなかった
- `kill 1823`（シグナル番号省略、デフォルトのSIGTERM）を試したところ、プロセスがasync処理の途中で終了シグナルを無視しており、数秒待っても`lsof`から消えなかった。`kill -9`でSIGKILLを送るまで残り続けた
- WSL2環境では、Windows側のタスクマネージャーでは該当のnodeプロセスが表示されず、WSL内の`ps`コマンドでしか見つけられなかった
- nodemonの設定で`ignore`に対象ファイルを含めていたため、コード修正後の自動再起動がそもそも走っておらず、古いプロセスがそのまま残り続けていたことも一因だった

## よくある質問

**Q: Windows（WSL2を使わないネイティブ環境）でポートを使っているプロセスを調べるには？**
PowerShellで`netstat -ano | findstr :3000`を実行するとポート番号とPIDが表示され、続けて`taskkill /PID <PID> /F`で強制終了できる。WSL2内の`lsof`や`kill`とはコマンド体系が異なるので注意する。

**Q: EADDRINUSEを毎回手動で対処するのが面倒です。何か自動化する方法はありますか？**
`npx kill-port 3000`を実行すると、指定ポートを使用しているプロセスを自動で検出して終了できる。npmスクリプトの`predev`フックに仕込んでおけば、`npm run dev`のたびに自動でポートを空けてから起動できる。

**Q: Docker Composeで動かしているコンテナでも同じエラーが出ます。原因は同じですか？**
根本原理は同じだが、Dockerの場合はホスト側のポートマッピング（`ports: - "3000:3000"`）が競合していることが多い。`docker ps`で同じポートを公開している別のコンテナが起動していないか確認し、不要なら`docker compose down`で停止してから再実行する。

## 関連記事

- [Linuxでプロセスをkillコマンドで終了する方法](/posts/linux-kill-command)
- [Linuxでlsofコマンドを使ってファイルやポートの使用状況を確認する方法](/posts/linux-lsof-command)
- [Dockerで「ポートが既に使用されています」エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [pm2でNode.jsアプリケーションをプロセス管理する方法](/posts/node-pm2-setup)
- [Windows Terminalの基本設定方法](/posts/windows-terminal-setup)
