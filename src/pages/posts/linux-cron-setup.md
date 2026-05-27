---
title: 'LinuxでCronジョブを設定して定期実行する方法'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
description: 'LinuxのcrontabでCronジョブを設定してスクリプトを定期実行する方法を解説。cron式の書き方と実行ログの確認方法も紹介します。'
---

## やりたかったこと

Linuxでスクリプトを定期的に自動実行したかった。
Cronを使うと指定した時間にコマンドを自動実行できる。

## 環境

- Linux（Ubuntu / Debian）
- WSL2

## Cronの基本

### crontabを編集する

```bash
crontab -e    # 現在のユーザーのcrontabを編集
crontab -l    # 現在の設定を表示
crontab -r    # crontabを削除
```

### cron式の書き方

```
分 時 日 月 曜日 コマンド
*  *  *  *  *
```

### よく使う設定例

```bash
# 毎日午前2時にバックアップ
0 2 * * * /home/user/backup.sh

# 毎週月曜日の9時に実行
0 9 * * 1 /home/user/weekly.sh

# 毎時0分に実行
0 * * * * /home/user/hourly.sh

# 5分ごとに実行
*/5 * * * * /home/user/check.sh

# 毎月1日の0時に実行
0 0 1 * * /home/user/monthly.sh
```

## 実際の設定例

```bash
crontab -e
```

エディタが開いたら以下を追加する。

```
# ログファイルを毎日削除
0 3 * * * find /var/log/myapp -name "*.log" -mtime +7 -delete

# 毎分スクリプトを実行してログに記録
* * * * * /home/user/script.sh >> /var/log/cron.log 2>&1
```

## Cronのログを確認する

```bash
grep CRON /var/log/syslog
tail -f /var/log/cron.log
```

## ハマったポイント

- Cronはフルパスでコマンドを指定する（`/usr/bin/python3` など）
- 環境変数はCronでは引き継がれない
- `2>&1` をつけるとエラーもログに記録できる
- `*/5` は「5の倍数分ごと」という意味

Cronのログを確認する際は[Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)を使うとリアルタイムで確認できる。

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [GitHub Actionsでスケジュール実行を設定する方法](/posts/github-actions-schedule)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
