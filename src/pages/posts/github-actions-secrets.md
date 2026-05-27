---
title: 'GitHub ActionsでSecretsを使って秘密情報を管理する方法'
date: '2026-05-13'
category: 'GitHub Actions'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub ActionsでSecretsにAPIキーなどの秘密情報を登録してワークフロー内で安全に使う方法を解説。登録手順と参照方法を紹介します。'
---

## Secretsの設定手順

1. GitHubリポジトリ→「Settings」→「Secrets and variables」→「Actions」
2. 「New repository secret」→Name・Secretを入力

## ワークフローから参照する

```yaml
steps:
  - name: デプロイ
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: echo "APIキーを使った処理"
```

## ハマったポイント

- Secretsの値はログにマスクされる
- 一度登録すると値を確認できない（上書きのみ）
- フォークされたリポジトリからのPRではSecretsは使えない

Cloudflare Pagesで同様に環境変数を管理したい場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)を参照。`.gitignore` で `.env` ファイルを除外しておくことも重要で、[Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)が参考になる。

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
