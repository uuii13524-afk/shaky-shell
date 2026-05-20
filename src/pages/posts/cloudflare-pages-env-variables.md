---
title: 'Cloudflare Pagesで環境変数を設定する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Cloudflare PagesでAPIキーなどの秘密情報を環境変数として管理したかった。
コードに直接書くのはセキュリティ上よくないので環境変数を使う。

## 環境

- Cloudflare Pages
- Astro / Next.js など

## 設定手順

### 1. Cloudflareダッシュボードで設定

1. Cloudflareダッシュボード→「Workers & Pages」
2. 対象プロジェクトをクリック
3. 「Settings」→「Variables and Secrets」
4. 「Add variable」をクリック
5. 変数名と値を入力して保存

### 2. コードから参照する

**Astroの場合**

```javascript
const apiKey = import.meta.env.MY_API_KEY;
```

**Next.jsの場合**

```javascript
const apiKey = process.env.MY_API_KEY;
```

## 本番環境と開発環境で分ける

### 本番環境（Cloudflare Pages）

Cloudflareダッシュボードで設定する。

### 開発環境（ローカル）

プロジェクトルートに `.env` ファイルを作成する。

```
MY_API_KEY=ローカル用のキー
```

`.env` は `.gitignore` に追加してGitHubにpushしない。

```
# .gitignore
.env
.env.local
```

## ハマったポイント

- 環境変数を追加したら再デプロイが必要
- `VITE_` または `PUBLIC_` プレフィックスがないとクライアント側から参照できない（Astroの場合は `PUBLIC_`）
- `.env` ファイルをGitHubにpushしないよう注意
- 変数名は大文字とアンダースコアで書くのが慣例

## 関連記事

- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
