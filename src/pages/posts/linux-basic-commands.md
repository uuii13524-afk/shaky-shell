---
title: 'Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ'
date: '2026-05-10'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
description: 'Linuxのls・cd・mkdir・rm・cpなどファイル操作に必要な基本コマンドの使い方をまとめました。初心者向けにオプションもわかりやすく解説します。'
---

## ファイル・フォルダの確認

```bash
ls          # 一覧
ls -la      # 詳細（隠しファイル含む）
pwd         # 現在のフォルダ
```

## フォルダの移動

```bash
cd /home/user    # 絶対パス
cd ..            # 1つ上
cd ~             # ホーム
```

## 作成・削除

```bash
mkdir newfolder      # フォルダ作成
touch newfile.txt    # ファイル作成
rm file.txt          # ファイル削除
rm -rf folder/       # フォルダを強制削除
```

## ファイルの中身を確認

```bash
cat file.txt         # 全内容
less file.txt        # スクロール表示（qで終了）
tail -f logfile.log  # リアルタイム表示
```

## ハマったポイント

- `rm -rf` は元に戻せない
- Linuxはファイル名の大文字小文字を区別する

ファイルの中身を検索したい場合は[Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)も覚えておくと便利だ。

## ConoHa VPSでDockerを本番環境で使う

ローカルでDockerを動かせるようになったら、次は本番サーバーへの展開です。
ConoHa VPSならDockerがすぐに使える環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4YQYYA" rel="nofollow">ConoHa VPSを見てみる →</a>
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4YQYYA" alt="">

## XServer VPSで本番環境を用意する

ローカルでの動作確認ができたら、次は本番サーバーへの展開です。
XServer VPSなら高性能な環境を低コストで用意できます。

<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" rel="nofollow">エックスサーバーのVPSサーバー</a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25ES2Q" alt="">

## 関連記事

- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)


## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
