---
title: 'Cloudflare Pagesで環境変数を設定する方法'
date: '2026-05-13'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## 設定手順

1. Cloudflareダッシュボード→プロジェクト→「Settings」→「Variables and Secrets」
2. 「Add variable」→変数名と値を入力して保存

## コードから参照する

```javascript
// Astroの場合
const apiKey = import.meta.env.MY_API_KEY;
```

## 開発環境（ローカル）

`.env` ファイルを作成する。

```
MY_API_KEY=ローカル用のキー
```

`.env` は `.gitignore` に追加する。

## ハマったポイント

- 環境変数を追加したら再デプロイが必要
- `.env` をGitHubにpushしないよう注意

## 関連記事

- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
