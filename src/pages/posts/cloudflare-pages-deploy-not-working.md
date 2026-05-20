---
title: 'Cloudflare PagesのGitHub自動デプロイが動かない時の対処法'
date: '2026-05-04'
category: 'Cloudflare'
---

## 症状

git pushしてもCloudflare Pagesに変更が反映されない。
Deploymentsタブに新しいデプロイが来ない。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## 環境

- Cloudflare Pages
- GitHub
- Astro

## 原因1：CloudflareとGitHubの接続が切れている

### 解決方法

1. 「Git repository」の「Manage」をクリック
2. GitHubアカウントを再認証する
3. 空のコミットをpushして強制デプロイ

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因2：古いコミットがデプロイされている

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因3：ビルドエラーが発生している

Deploymentsタブ→「View build logs」でエラー内容を確認する。

## ハマったポイント

- 空のコミットpushが最も確実な強制デプロイ方法
- ビルドログを最初に確認する習慣をつける

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
