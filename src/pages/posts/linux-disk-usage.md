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
