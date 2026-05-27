---
title: 'Linuxでswapを設定する方法（swapfile・有効化・確認）'
date: '2026-05-24'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'swap', 'VPS']
en_tags: ['Linux', 'swap', 'VPS']
description: 'Linuxでswapfileを作成してスワップを有効化する方法を解説。swapの作成・有効化・永続化・使用量確認までの手順をステップごとに紹介します。'
---

## やりたかったこと

VPSのRAMが1GBしかなく、DockerやNode.jsを動かしたらOOM Killerが発動してプロセスが落ちた。
スワップ領域を追加してメモリ不足を緩和したかった。

## スワップとは

実メモリ（RAM）が不足したとき、ディスクの一部をメモリの代わりに使う仕組み。
RAMより遅いが、プロセスが強制終了されるよりはマシ。

## スワップファイルを作成する

```bash
# 2GBのスワップファイルを作成（bs=1M × count=2048）
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048

# パーミッションを設定（rootのみ読み書き可能）
sudo chmod 600 /swapfile

# スワップ領域としてフォーマット
sudo mkswap /swapfile
```

## スワップを有効にする

```bash
# スワップを有効化
sudo swapon /swapfile

# 有効になっているか確認
sudo swapon --show
```

以下のように表示されれば成功。

```
NAME      TYPE SIZE USED PRIO
/swapfile file   2G   0B   -2
```

## スワップの使用状況を確認する

```bash
# メモリとスワップの使用状況
free -h
```

```
              total        used        free      shared  buff/cache   available
Mem:          980Mi       400Mi       100Mi        10Mi       480Mi       450Mi
Swap:         2.0Gi         0B       2.0Gi
```

```bash
# より詳細な確認
cat /proc/meminfo | grep -i swap
```

## 再起動後も自動でマウントする

このままだと再起動するとスワップが無効になる。`/etc/fstab` に追記して永続化する。

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

設定が正しいか確認する。

```bash
cat /etc/fstab | grep swap
```

```
/swapfile none swap sw 0 0
```

## swappinessを調整する

`swappiness` はRAMとスワップをどれくらい積極的に切り替えるかの設定値（0〜100）。
VPSではデフォルト60になっていることが多いが、サーバー用途では低めにすることが多い。

```bash
# 現在の値を確認
cat /proc/sys/vm/swappiness

# 一時的に変更（再起動で元に戻る）
sudo sysctl vm.swappiness=10

# 永続化
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## スワップを削除したいとき

```bash
# スワップを無効化
sudo swapoff /swapfile

# ファイルを削除
sudo rm /swapfile

# /etc/fstab からも該当行を削除する
sudo vim /etc/fstab
```

## ハマったポイント

- `chmod 600` を忘れると `mkswap` がエラーになる
- `/etc/fstab` に追記しないと再起動のたびにスワップが消える
- スワップのサイズはRAMの1〜2倍が目安（RAM 1GBなら2GBのスワップ）
- SSDのVPSでは書き込み回数を増やすので `swappiness` を低くする（10前後）がおすすめ
- `free -h` で Swap行が `0` のままなら `swapon` ができていない

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxのディスク使用量を確認するコマンド（df/du）](/posts/linux-disk-usage)
- [Linuxのプロセス管理（ps/kill/top）](/posts/linux-process-management)
- [VPSにDockerをインストールして使い始める方法](/posts/vps-docker-setup)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
