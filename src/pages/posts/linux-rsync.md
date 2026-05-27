---
title: 'rsyncでファイルを同期・バックアップする方法'
date: '2026-05-25'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'rsync', 'バックアップ', 'SSH']
en_tags: ['Linux', 'rsync', 'backup', 'SSH']
---

## やりたかったこと

VPSのファイルをローカルにバックアップしたかった。
`scp`は毎回全ファイルをコピーするので、差分だけ転送できる`rsync`を使うことにした。

## 基本的な使い方

```bash
rsync -av ソース/ 宛先/
```

- `-a`: アーカイブモード（パーミッション・タイムスタンプ・シンボリックリンクを保持）
- `-v`: 転送ファイルを表示

### ローカル間のコピー

```bash
rsync -av /var/www/html/ /backup/html/
```

末尾のスラッシュに注意。`ソース/`（スラッシュあり）はディレクトリの中身をコピー、`ソース`（スラッシュなし）はディレクトリごとコピーする。

## リモートサーバーとの同期

### ローカル → リモート

```bash
rsync -av -e ssh /var/www/html/ user@example.com:/var/www/html/
```

### リモート → ローカル（バックアップ）

```bash
rsync -av -e ssh user@example.com:/var/www/html/ /backup/html/
```

## よく使うオプション

```bash
# 削除も同期する（宛先にしかないファイルを削除）
rsync -av --delete /var/www/html/ /backup/html/

# ドライラン（実際にはコピーせず確認だけ）
rsync -av --dry-run /var/www/html/ /backup/html/

# 圧縮して転送（帯域節約）
rsync -avz -e ssh user@example.com:/var/www/ /backup/

# 特定のファイルを除外
rsync -av --exclude='*.log' --exclude='.git' /var/www/html/ /backup/html/

# 進捗を表示
rsync -av --progress /var/www/html/ /backup/html/
```

## Cronで定期バックアップ

```bash
crontab -e
```

```
# 毎日午前2時にバックアップ
0 2 * * * rsync -az -e ssh user@example.com:/var/www/html/ /backup/html/ >> /var/log/rsync.log 2>&1
```

## ハマったポイント

- ソースパスの末尾スラッシュの有無で動作が変わるので必ず確認する
- `--delete`は強力なので、最初は`--dry-run`で確認してから実行する
- SSHの公開鍵認証が設定されていないとCronでの自動実行が止まる
- rsyncはデフォルトで変更のないファイルをスキップするので、自動的に差分転送になる

SSHの公開鍵認証が未設定の場合は[LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)の `~/.ssh/config` の設定も合わせて確認してほしい。

## 関連記事

- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [LinuxでCronジョブを設定して定期実行する方法](/posts/linux-cron-setup)
- [Linuxのファイルパーミッションの基本](/posts/linux-file-permissions)
- [Linuxの基本コマンドまとめ](/posts/linux-basic-commands)

## おすすめのVPS／ドメイン

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
