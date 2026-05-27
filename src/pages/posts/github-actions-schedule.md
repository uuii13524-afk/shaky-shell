---
title: 'GitHub Actionsでスケジュール実行（定期実行）を設定する方法'
date: '2026-05-19'
category: 'GitHub Actions'
layout: '../../layouts/PostLayout.astro'
---

## 基本的な設定

```yaml
on:
  schedule:
    - cron: '0 9 * * *'    # 毎日9時（UTC）
```

## よく使うcron設定例

```
0 9 * * *       # 毎日9時（UTC）
0 0 * * 1       # 毎週月曜日0時
0 9 1 * *       # 毎月1日9時
*/30 * * * *    # 30分ごと
```

## JSTに変換する

GitHubのcronはUTCなので9時間の差がある。

```
JSTの9時 = UTCの0時 → cron: '0 0 * * *'
```

## 手動実行も可能にする

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
```

## ハマったポイント

- cronはUTCなのでJSTと9時間ずれる
- リポジトリにアクティビティがないと無効化されることがある

Linuxのcronジョブとの使い分けについては[LinuxでCronジョブを設定して定期実行する方法](/posts/linux-cron-setup)も参考にしてほしい。GitHub Actionsのスケジュールはリポジトリへのアクセスが必要な処理に、サーバー側の処理はcronで使い分けるのが一般的だ。

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
