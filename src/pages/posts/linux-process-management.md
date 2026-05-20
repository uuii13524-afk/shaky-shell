---
title: 'Linuxでプロセスを確認・終了する方法（ps/kill）'
date: '2026-05-20'
category: 'Linux'
---

## やりたかったこと

Linuxで動いているプロセスを確認して、固まったプロセスを終了したかった。

## 環境

- Linux（Ubuntu / Debian）
- Mac
- WSL2

## プロセスの確認

### ps：プロセス一覧を表示

```bash
ps aux                    # 全プロセスを表示
ps aux | grep nginx       # nginxのプロセスを検索
ps -ef                    # 全プロセスを詳細表示
```

### top：リアルタイムでプロセスを監視

```bash
top                       # リアルタイム監視（qで終了）
top -u ユーザー名         # 特定ユーザーのプロセスのみ
```

### htop（インストールが必要）

```bash
sudo apt install htop
htop                      # カラフルで見やすいtop
```

## プロセスの終了

### kill：PIDを指定して終了

```bash
kill PID                  # プロセスを終了（正常終了を要求）
kill -9 PID               # プロセスを強制終了
kill -15 PID              # プロセスを終了（kill と同じ）
```

### pkill：プロセス名で終了

```bash
pkill nginx               # nginx という名前のプロセスを終了
pkill -9 nginx            # 強制終了
```

### killall：同名の全プロセスを終了

```bash
killall nginx             # nginx という名前の全プロセスを終了
```

## ポートを使っているプロセスを確認

```bash
lsof -i :8080             # 8080ポートを使っているプロセス
ss -tlnp | grep 8080      # 同上（ssコマンド）
```

## ハマったポイント

- `kill` だけでは終了しない場合は `kill -9` で強制終了
- `kill -9` はプロセスが後処理できないので最終手段
- PIDは `ps aux | grep プロセス名` で確認する
- Dockerコンテナのプロセスは `docker stop` で停止する

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Dockerのポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
