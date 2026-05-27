---
title: 'Linuxのファイルパーミッション（chmod/chown）完全ガイド'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Linuxのファイルパーミッションを理解して正しく設定したかった。

## パーミッションとは

ファイル・フォルダに対して「誰が何をできるか」を定義する設定。

```
-rwxr-xr-x
```

| 文字 | 意味 |
|------|------|
| r | 読み取り（4） |
| w | 書き込み（2） |
| x | 実行（1） |
| - | 権限なし（0） |

## chmodでパーミッションを変更

### 数値で指定

```bash
chmod 755 ファイル名    # rwxr-xr-x
chmod 644 ファイル名    # rw-r--r--
chmod 600 ファイル名    # rw-------
chmod 777 ファイル名    # rwxrwxrwx（全員フルアクセス・危険）
```

### よく使う設定

```
755 → Webサーバーのディレクトリ
644 → 通常のファイル
600 → SSHキー・設定ファイル
755 → 実行可能なスクリプト
```

### シンボルで指定

```bash
chmod +x script.sh      # 実行権限を追加
chmod -x script.sh      # 実行権限を削除
chmod u+w file.txt      # 所有者に書き込み権限を追加
chmod o-r file.txt      # その他から読み取り権限を削除
```

## chownで所有者を変更

```bash
chown ユーザー名 ファイル名
chown ユーザー名:グループ名 ファイル名
chown -R ユーザー名 フォルダ名   # 再帰的に変更
```

## ハマったポイント

- SSHキーは必ず `chmod 600` にする（600でないと接続拒否される）
- Webサーバーのファイルは777にしない（セキュリティリスク）
- `chmod -R` で再帰的に変更する時は慎重に

パーミッション設定後もアクセスできない場合は[Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)で所有者の設定も確認してほしい。

## 関連記事

- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
