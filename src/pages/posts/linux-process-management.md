---
title: 'Linuxでプロセスを確認・終了する方法（ps/kill）'
date: '2026-05-19'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
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

## おすすめのVPS

Linuxを本番環境で使うなら、VPSが手軽です。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
