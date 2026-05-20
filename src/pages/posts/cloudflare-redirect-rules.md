---
title: 'Cloudflareでリダイレクトルールを設定する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

CloudflareでURLのリダイレクトを設定したかった。
サーバー側の設定なしにCloudflareだけでリダイレクトできる。

## 環境

- Cloudflare

## リダイレクトルールの設定手順

1. Cloudflareダッシュボード→対象ドメイン
2. 左メニュー「Rules」→「Redirect Rules」
3. 「Create rule」をクリック

## よくある設定例

### HTTPをHTTPSにリダイレクト

**条件：**
```
URIフル → 含む → http://
```

**アクション：**
```
動的リダイレクト
https://${uri}
ステータスコード：301
```

ただしCloudflareのSSL設定で「Always Use HTTPS」をオンにすれば自動でリダイレクトされる。

### wwwあり→なしにリダイレクト

**条件：**
```
ホスト名 → 等しい → www.example.com
```

**アクション：**
```
動的リダイレクト
https://example.com${uri.path}
ステータスコード：301
```

### 旧URLから新URLにリダイレクト

**条件：**
```
URIパス → 等しい → /old-page
```

**アクション：**
```
静的リダイレクト
https://example.com/new-page
ステータスコード：301
```

## ステータスコードの使い分け

| コード | 意味 | 用途 |
|--------|------|------|
| 301 | 恒久的なリダイレクト | URLを完全に変更する場合 |
| 302 | 一時的なリダイレクト | 一時的に別URLに転送する場合 |

SEO的には301を使うことが多い。

## ハマったポイント

- ルールの順番が重要。上のルールから順番に評価される
- 無料プランではリダイレクトルールは10個まで
- `Always Use HTTPS` がオンならHTTP→HTTPSのリダイレクトルールは不要

## 関連記事

- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
