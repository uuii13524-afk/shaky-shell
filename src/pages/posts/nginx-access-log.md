---
title: 'nginxのアクセスログとエラーログの確認方法'
date: '2026-05-28'
category: 'nginx'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['nginx', 'ログ', 'Linux', 'サーバー管理', 'トラブルシューティング']
en_tags: ['nginx', 'access log', 'error log', 'Linux', 'server management']
description: 'nginxのアクセスログとエラーログの場所・確認方法・フォーマットの読み方をまとめた。tail/grepを使ったリアルタイム監視も解説。'
---
## やりたかったこと
nginxが正常に動いているか確認したかった。
アクセスが来ているのにページが表示されない時に、ログを追いかけて原因を特定した。

## ログファイルの場所
nginxのログは通常ここにある。

```bash
/var/log/nginx/access.log   # アクセスログ
/var/log/nginx/error.log    # エラーログ
```

設定ファイルで確認もできる。

```bash
grep log /etc/nginx/nginx.conf
```

## アクセスログの確認方法
### リアルタイムで監視する

```bash
tail -f /var/log/nginx/access.log
```

### 直近100行だけ見る

```bash
tail -n 100 /var/log/nginx/access.log
```

### 特定IPのアクセスを絞り込む

```bash
grep "192.168.1.1" /var/log/nginx/access.log
```

### 404エラーだけ抽出する

```bash
grep " 404 " /var/log/nginx/access.log
```

### アクセス数の多いURLを集計する

```bash
awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

## エラーログの確認方法
### エラーログをリアルタイム監視する

```bash
tail -f /var/log/nginx/error.log
```

### errorレベル以上のログだけ見る

```bash
grep "\[error\]" /var/log/nginx/error.log
```

エラーの種類はこんな感じ：

| レベル | 内容 |
|--------|------|
| notice | 通常動作の通知 |
| warn   | 警告（動作には問題なし） |
| error  | エラー（要確認） |
| crit   | 深刻なエラー |

## アクセスログのフォーマットを読む
デフォルトのアクセスログはこんな形式だった。

```
192.168.1.1 - - [28/May/2026:10:00:00 +0900] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
```

左から順に：
- クライアントIP
- リモートユーザー（基本は`-`）
- 認証ユーザー（基本は`-`）
- アクセス日時
- リクエスト内容
- ステータスコード
- レスポンスサイズ（バイト）
- リファラー
- ユーザーエージェント

## ログローテーションの確認

```bash
ls -la /var/log/nginx/
```

古いログは`access.log.1`や`access.log.2.gz`のような名前で残っている。
nginxはデフォルトでlogrotateが設定されていることが多い。

## ハマったポイント
- ログが空の場合はnginxが起動していないか、パスが違う可能性がある
- `systemctl status nginx`でnginxの状態を確認してからログを見ると原因が特定しやすかった
- 権限がなくて`Permission denied`になる場合は`sudo`をつけると読めた
- 大量アクセスのサーバーでは`tail -n`で行数を絞らないとターミナルが固まることがあった
- エラーログに`connect() failed`が出た場合はリバースプロキシのバックエンドが落ちているサインだった

## 関連記事
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [nginx 502 Bad Gatewayエラーの原因と解決方法](/posts/nginx-502-bad-gateway)
- [nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）](/posts/nginx-reverse-proxy)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
