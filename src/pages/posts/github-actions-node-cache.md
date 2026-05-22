---
title: 'GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法'
date: '2026-05-15'
category: 'GitHub Actions'
layout: '../../layouts/PostLayout.astro'
---

## キャッシュありの設定

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'      # これだけでキャッシュが有効
  - run: npm ci
  - run: npm run build
```

## npm install と npm ci の違い

| | npm install | npm ci |
|--|--|--|
| 速度 | 普通 | 速い |
| package-lock.json | 更新することがある | 更新しない |
| 用途 | 開発環境 | CI/CD環境 |

## ハマったポイント

- `cache: 'npm'` を設定するだけで自動的にキャッシュされる
- `package-lock.json` が変わるとキャッシュが無効になる

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
