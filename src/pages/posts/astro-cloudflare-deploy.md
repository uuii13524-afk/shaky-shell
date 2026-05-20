---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Astroで作ったサイトをCloudflare Pagesで公開したかった。

## 環境

- Windows 11
- Node.js
- Astro
- GitHub
- Cloudflare Pages

## 手順

### 1. Astroをインストール

```
npm create astro@latest
```

### 2. ローカルで動作確認

```
cd プロジェクト名
npm run dev
```

http://localhost:4321 でAstroの画面が出れば成功。

### 3. GitHubにpush

```
git init
git add .
git commit -m "first commit"
git remote add origin GitHubのURL
git push -u origin main
```

### 4. Cloudflare Pagesに接続

1. 「Workers & Pages」→「Create application」
2. 画面下部「Looking to deploy Pages? Get started」をクリック
3. 「Import an existing Git repository」→「Get started」
4. リポジトリを選択
5. Framework presetで「Astro」を選択
6. 「Save and Deploy」

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は画面下部の「Get started」から入る
- Framework presetでAstroを選ぶとビルド設定が自動入力される

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
