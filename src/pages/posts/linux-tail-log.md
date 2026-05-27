---
title: 'Linuxでログをリアルタイム監視するtail -fの使い方'
date: '2026-05-17'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## 基本的な使い方

```bash
tail -f /var/log/nginx/error.log   # エラーログを監視
tail -n 100 -f ファイル名           # 末尾100行から監視
```

`Ctrl + C` で終了する。

## grepと組み合わせてエラーだけ監視

```bash
tail -f /var/log/nginx/error.log | grep "error"
```

## Dockerのログを監視

```bash
docker logs -f コンテナID
docker logs -f --tail 100 コンテナID
```

## よく監視するログファイル

```
/var/log/nginx/error.log     # nginxエラーログ
/var/log/syslog              # システムログ
/var/log/auth.log            # 認証ログ
```

特定のキーワードだけを絞り込んで監視したい場合は、`tail -f` のパイプ先で[Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)を組み合わせると効率よくエラーを確認できる。

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
