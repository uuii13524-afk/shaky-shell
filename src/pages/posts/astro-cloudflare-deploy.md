---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-20'
category: 'Cloudflare'
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

ターミナルで以下を実行する。

```
npm create astro@latest
```

プロジェクト名を入力してインストールを完了させる。

### 2. ローカルで動作確認

```
cd プロジェクト名
npm run dev
```

ブラウザで http://localhost:4321 を開いてAstroの画面が出れば成功。

### 3. GitHubにpush

```
git init
git add .
git commit -m "first commit"
git remote add origin GitHubのURL
git push -u origin main
```

### 4. Cloudflare Pagesに接続

1. Cloudflareダッシュボードで「Workers & Pages」を開く
2. 「Create application」→画面下部の「Looking to deploy Pages? Get started」をクリック
3. 「Import an existing Git repository」→「Get started」
4. GitHubアカウントを連携してリポジトリを選択
5. ビルド設定でFramework presetを「Astro」に設定
6. 「Save and Deploy」を押す

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は画面下部の「Get started」から入る
- Framework presetでAstroを選ぶとビルド設定が自動で入力される
- デプロイ完了まで2〜3分かかる

## 結果

デプロイ成功後は `プロジェクト名.pages.dev` というURLでアクセスできる。
