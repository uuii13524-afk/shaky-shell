---
title: 'Linuxでディスク使用量を確認する方法（df/du）'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Linuxサーバーのディスク使用量を確認したかった。
dfとduを使うとディスクの空き容量やフォルダのサイズを確認できる。

## df：ディスク全体の使用量を確認

```bash
df -h                    # 人間が読みやすい形式で表示
df -h /                  # ルートのみ表示
df -h /var               # 特定のパスを指定
```

### 出力例

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
```

## du：フォルダのサイズを確認

```bash
du -sh フォルダ名         # フォルダの合計サイズ
du -sh /*                # ルート直下の各フォルダ
du -sh /var/log/*        # ログフォルダの中身
du -h --max-depth=1 /var # 1階層だけ表示
```

## ディスクが満杯になった時の対処

### 大きいファイルを探す

```bash
find / -size +100M -type f 2>/dev/null
```

### ログファイルを削除する

```bash
sudo journalctl --vacuum-size=100M    # systemdログを100MB以下に
sudo find /var/log -name "*.log" -mtime +30 -delete  # 30日以上前のログを削除
```

### Dockerの不要なデータを削除する

```bash
docker system prune -a
```

## ハマったポイント

- `df` はファイルシステム全体、`du` は特定フォルダのサイズを調べる
- `-h` オプションで人間が読みやすい形式（GB/MB）になる
- Dockerを使っている場合は `/var/lib/docker` が大きくなりやすい

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
