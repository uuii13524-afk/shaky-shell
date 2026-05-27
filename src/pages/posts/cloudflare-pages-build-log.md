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

デプロイが全く来ない場合はビルドエラーではなくGitHubとの接続切れが原因のこともある。その場合は[Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)を確認してほしい。

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
