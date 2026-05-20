---
title: 'Cloudflare Pagesのビルドログの見方とエラーの対処法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Cloudflare Pagesのデプロイが失敗した時にビルドログを読んで原因を特定したかった。

## 環境

- Cloudflare Pages

## ビルドログの開き方

1. Cloudflareダッシュボード→「Workers & Pages」
2. 対象プロジェクトをクリック
3. 「Deployments」タブを開く
4. 対象のデプロイをクリック
5. 「View build logs」をクリック

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

```
TypeError: Astro2.glob is not a function
```

Astro 5以降で廃止。`import.meta.glob()` に書き換える。

### Cannot find module

```
Error: Cannot find module '@astrojs/sitemap'
```

```
npm install @astrojs/sitemap
```

### 古いコミットがデプロイされている

```
HEAD is now at 3218655 first commit
```

```
git commit --allow-empty -m "force deploy"
git push
```

## ハマったポイント

- `Failed` が出た行の直前にエラーの原因が書いてある
- ブラウザの検索（Ctrl+F）で「ERROR」を検索すると原因を見つけやすい

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [XservorドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
