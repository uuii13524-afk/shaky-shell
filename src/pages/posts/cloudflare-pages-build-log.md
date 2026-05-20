---
title: 'Cloudflare Pagesのビルドログの見方とエラーの対処法'
date: '2026-05-09'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## ビルドログの開き方

1. Cloudflareダッシュボード→「Workers & Pages」
2. 対象プロジェクト→「Deployments」タブ
3. 対象デプロイ→「View build logs」

## 成功時のログの流れ

```
Cloning repository...
Installing project dependencies
Executing user command
Uploading...
Success: Your site was deployed
```

## よくあるエラーと対処法

### Astro.glob is not a function

Astro 5以降で廃止。`import.meta.glob()` に書き換える。

### Cannot find module

```
npm install @astrojs/sitemap
```

### 古いコミットがデプロイされている

```
git commit --allow-empty -m "force deploy"
git push
```

## ハマったポイント

- `Failed` の直前にエラーの原因が書いてある
- Ctrl+F で「ERROR」を検索すると原因を見つけやすい

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
