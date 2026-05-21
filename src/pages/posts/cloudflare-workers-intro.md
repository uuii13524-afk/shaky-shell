---
title: 'Cloudflare Workers入門：サーバーレス関数を作る方法'
date: '2026-05-21'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Cloudflare Workersでサーバーレスな関数を作りたかった。
サーバーを用意せずにAPIエンドポイントやリダイレクト処理を実装できる。

## 環境

- Cloudflare Workers
- Wrangler CLI

## Cloudflare Workersとは

- サーバーレスの実行環境
- 世界中のCloudflareエッジサーバーで動く
- 無料枠：1日10万リクエストまで
- コールドスタートがほぼない

## 手順

### 1. Wranglerをインストール

```bash
npm install -g wrangler
wrangler --version
```

### 2. Cloudflareにログイン

```bash
wrangler login
```

### 3. プロジェクトを作成

```bash
npm create cloudflare@latest my-worker
cd my-worker
```

### 4. Workerのコード（src/index.js）

```javascript
export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === '/api/hello') {
      return new Response(JSON.stringify({ message: 'Hello from Worker!' }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

### 5. ローカルで動作確認

```bash
wrangler dev
```

http://localhost:8787 で確認できる。

### 6. デプロイ

```bash
wrangler deploy
```

## よくある使い方

### リダイレクト処理

```javascript
export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/old-page') {
      return Response.redirect('https://example.com/new-page', 301);
    }
    return fetch(request);
  },
};
```

### CORSヘッダーを追加

```javascript
export default {
  async fetch(request) {
    const response = await fetch(request);
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');
    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
```

## ハマったポイント

- Workersは Node.js ではなくWeb標準APIを使う
- `wrangler dev` でローカルテストができる
- 無料枠でも十分な用途が多い

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)
- [Cloudflareでリダイレクトルールを設定する方法](/posts/cloudflare-redirect-rules)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
