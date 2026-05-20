---
title: 'Linuxでプロセスを確認・終了する方法（ps/kill）'
date: '2026-05-19'
category: 'Linux'
---

## プロセスの確認

```bash
ps aux                    # 全プロセスを表示
ps aux | grep nginx       # nginxのプロセスを検索
top                       # リアルタイム監視（qで終了）
```

## プロセスの終了

```bash
kill PID                  # 正常終了を要求
kill -9 PID               # 強制終了
pkill nginx               # プロセス名で終了
```

## ポートを使っているプロセスを確認

```bash
lsof -i :8080
ss -tlnp | grep 8080
```

## ハマったポイント

- `kill` だけで終了しない場合は `kill -9` で強制終了
- `kill -9` は最終手段

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Dockerでポートが既に使用中エラーが出た時の対処法](/posts/docker-port-already-in-use)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
