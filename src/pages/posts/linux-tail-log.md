---
title: 'Linuxでログをリアルタイム監視するtail -fの使い方'
date: '2026-05-20'
category: 'Linux'
---

## やりたかったこと

サーバーのログをリアルタイムで監視したかった。
`tail -f` を使うとログが追加されるたびに自動で表示される。

## 環境

- Linux（Ubuntu / Debian）
- Mac
- WSL2

## 基本的な使い方

```bash
tail -f /var/log/nginx/access.log    # アクセスログを監視
tail -f /var/log/nginx/error.log     # エラーログを監視
tail -f /var/log/syslog              # システムログを監視
```

`Ctrl + C` で終了する。

## よく使うオプション

```bash
tail -f ファイル名           # リアルタイム監視
tail -n 100 ファイル名       # 末尾100行を表示
tail -n 100 -f ファイル名    # 末尾100行を表示してから監視
tail -f ファイル1 ファイル2  # 複数ファイルを同時監視
```

## grepと組み合わせてエラーだけ監視

```bash
tail -f /var/log/nginx/error.log | grep "error"
tail -f app.log | grep -i "ERROR\|WARN"
```

## Dockerのログを監視

```bash
docker logs -f コンテナID           # コンテナのログを監視
docker logs -f --tail 100 コンテナID # 末尾100行から監視
```

## よく監視するログファイル

```
/var/log/nginx/access.log    # nginxアクセスログ
/var/log/nginx/error.log     # nginxエラーログ
/var/log/syslog              # システムログ
/var/log/auth.log            # 認証ログ
/var/log/apt/history.log     # aptインストール履歴
```

## ハマったポイント

- `tail -f` は `Ctrl + C` で終了する
- ログファイルのパーミッションが制限されている場合は `sudo` が必要
- Dockerの場合は `docker logs` コマンドを使う
- `journalctl -f` でsystemdのログをリアルタイム監視できる

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Dockerの基本コマンドまとめ](/posts/docker-basic-commands)
