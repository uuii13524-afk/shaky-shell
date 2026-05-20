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

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [nginxの基本的な設定ファイルの書き方](/posts/nginx-basic-config)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
