---
title: 'curlコマンドの基本的な使い方（APIテストに使える）'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
description: 'curlコマンドでHTTPリクエストを送る基本的な使い方を解説。GET・POST・ヘッダー指定・認証・ファイルダウンロードのオプションをまとめて紹介します。'
---

## やりたかったこと

コマンドラインからHTTPリクエストを送りたかった。
curlを使うとAPIのテストやファイルのダウンロードができる。

## 環境

- Linux / Mac / Windows（Git Bash）

## 基本的な使い方

### GETリクエスト

```bash
curl https://example.com
curl -s https://example.com    # 進捗を非表示
curl -o output.html https://example.com  # ファイルに保存
```

### POSTリクエスト

```bash
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### ヘッダーを確認する

```bash
curl -I https://example.com    # ヘッダーのみ表示
curl -v https://example.com    # 詳細表示
```

### 認証付きリクエスト

```bash
curl -H "Authorization: Bearer トークン" https://api.example.com
```

## APIテストでよく使うオプション

```bash
-X GET/POST/PUT/DELETE   # HTTPメソッドを指定
-H "ヘッダー名: 値"      # ヘッダーを追加
-d "データ"              # リクエストボディ
-o ファイル名            # レスポンスをファイルに保存
-s                       # サイレントモード
-v                       # 詳細表示
-L                       # リダイレクトに従う
```

## ハマったポイント

- Windowsのコマンドプロンプトではシングルクォートが使えない。Git Bashを使う
- `-s` と `-o` を組み合わせると進捗なしでファイルに保存できる
- JSONを整形して表示するには `| python3 -m json.tool` をパイプで繋ぐ

APIテストでレスポンスが正しく返ってくるか確認したら、その結果を[Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)と組み合わせてパイプで絞り込む使い方も覚えておくと便利だ。

## 関連記事

- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
