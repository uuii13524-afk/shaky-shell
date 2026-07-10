---
title: 'nohupコマンドの使い方｜SSH切断後もプロセスを実行し続ける方法'
date: '2026-07-10'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'nohup', 'SSH', 'バックグラウンド実行']
description: 'nohupコマンドを使ってSSHセッションが切れてもプロセスを実行し続ける方法。基本的な使い方、出力先の指定、&やdisownとの組み合わせ、よくあるエラーを解説。'
---

## ひとことで言うと

```bash
# コマンドをnohupで実行し、バックグラウンドに回す
nohup ./long-running-script.sh &

# 出力先を指定する場合
nohup ./long-running-script.sh > output.log 2>&1 &
```

---

## やりたかったこと / 現象

VPSにSSHで接続して時間のかかる処理を走らせたが、接続が切れると同時にプロセスも終了してしまった——`nohup` はまさにこの問題を解決するために存在するコマンドです。

SSHセッションが終了すると、そのセッションで起動したプロセスには通常 `SIGHUP`（hang up）シグナルが送られ、プロセスも一緒に終了します。`nohup` はこの `SIGHUP` を無視するようにプロセスを起動するコマンドで、「no hang up」の略です。ログアウトしても処理を継続させたい場面で頻繁に使われます。

---

## 環境

- OS: Linux（Ubuntu / CentOS / Debian など主要ディストリビューションで動作確認）
- シェル: bash / zsh

---

## 解決策

### 1. 基本構文

```bash
nohup <コマンド>
```

これだけでも `SIGHUP` は無視されますが、フォアグラウンドで実行され続けるとターミナルをブロックしてしまうため、通常は `&` を付けてバックグラウンドに回します。

```bash
nohup ./long-running-script.sh &
```

### 2. 出力先を指定する

`&` を付けずに `nohup` だけを実行すると、標準出力・標準エラー出力は自動的にカレントディレクトリの `nohup.out` に書き込まれます。

```bash
nohup ./long-running-script.sh &
cat nohup.out
```

出力先を明示的に指定したい場合は、リダイレクトを使います。

```bash
# 標準出力と標準エラー出力を同じファイルにまとめる
nohup ./long-running-script.sh > output.log 2>&1 &

# 標準出力と標準エラー出力を分ける
nohup ./long-running-script.sh > stdout.log 2> stderr.log &

# 出力を破棄する
nohup ./long-running-script.sh > /dev/null 2>&1 &
```

### 3. プロセスIDを確認する

バックグラウンドで実行すると、プロセスIDがすぐに表示される。

```bash
nohup ./long-running-script.sh &
[1] 12345
```

後から確認したい場合は `jobs -l` や `ps` を使う。

```bash
jobs -l
ps aux | grep long-running-script
```

### 4. プロセスを終了する

```bash
kill 12345
```

強制終了したい場合は `-9` を付ける。

```bash
kill -9 12345
```

### 5. disown と組み合わせる

`nohup` で `SIGHUP` は無視できても、シェル自体を終了すると `bash` の設定によってはジョブがまだ管理下に置かれていることがあります。より確実にシェルから切り離すには `disown` を併用します。

```bash
nohup ./long-running-script.sh &
disown
```

これで、シェルを終了してもプロセスがジョブテーブルから完全に切り離される。

### 6. 実行中のプロセスに後からnohupを適用する

すでに起動しているプロセスに対しては `nohup` を後付けできない。その場合は `disown` のみを使うか、`screen` / `tmux` のようなターミナルマルチプレクサへの移行を検討する。

```bash
# 実行中のジョブをシェルから切り離す（nohupの代用にはならないので注意）
disown -h %1
```

---

## よくあるエラーと対処

### `nohup: ignoring input and appending output to 'nohup.out'`

これはエラーではなく、出力先を指定しなかった場合に表示される正常なメッセージです。標準入力が無視され、出力が `nohup.out` に追記されることを示しています。

### `nohup: failed to run command: No such file or directory`

指定したコマンドやスクリプトが見つからない、または実行権限がないことが原因です。パスと権限を確認してください。

```bash
ls -l ./long-running-script.sh
chmod +x ./long-running-script.sh
```

### `nohup.out` が肥大化する

標準出力を明示的にリダイレクトせずに大量のログを出力し続けると `nohup.out` が際限なく増加します。`> /dev/null` で破棄するか、`logrotate` などでローテーションを設定してください。

### SSH切断後もプロセスが終了してしまう

`nohup` を付けたつもりでも `&` を忘れると、コマンドがフォアグラウンドのまま実行され、SSH接続を閉じた時点で結局終了してしまいます。`&` の付け忘れがないか確認してください。

---

## よくある質問

**Q: `nohup` と `screen` / `tmux` の違いは？**
`nohup` は単一のコマンドに `SIGHUP` を無視させるだけのシンプルな仕組みです。`screen` や `tmux` はセッションそのものを永続化し、再接続して途中経過を確認したり対話的に操作したりできる点が異なります。長時間の対話的な作業には `screen` / `tmux`、単発のバッチ処理には `nohup` が向いています。

**Q: `nohup command &` と `command & disown` は同じですか？**
似ていますが完全に同じではありません。`nohup` は `SIGHUP` シグナル自体を無視させ、`disown` はシェルのジョブテーブルからプロセスを切り離します。より確実に切断したい場合は両方を組み合わせるのが安全です。

**Q: `nohup` で実行したプロセスの終了を確認するには？**
`ps aux | grep <プロセス名>` でプロセスの有無を確認するか、ログファイルの内容を確認します。終了コードを残したい場合はスクリプト側で終了時にログへ書き込むようにするとよいでしょう。

**Q: systemdサービスの代わりに`nohup`を使ってもいいですか？**
一時的な作業や検証用途であれば問題ありません。ただし本番環境で自動起動・再起動・ログ管理まで必要な場合は `systemd` サービスとして定義するほうが運用は安定します。

**Q: `nohup` を使ってもプロセスが終了してしまうことがあるのはなぜ？**
`&` の付け忘れのほか、親プロセスグループごとkillされている、サーバー自体が再起動された、などの理由が考えられます。プロセスの親子関係を `ps -ef --forest` などで確認してください。

---

## 関連記事

- [screenコマンドでSSHセッションを永続化する方法](/posts/linux-screen-command)
- [systemdでサービスを管理する方法（start/stop/enable/status）](/posts/linux-systemd-service)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
