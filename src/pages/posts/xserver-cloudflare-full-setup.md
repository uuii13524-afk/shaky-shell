---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定したかった。

## 環境

- Xserverドメイン
- Cloudflare Pages
- Astro

## 全体の流れ

```
Cloudflareでネームサーバーを確認
↓
XserverでネームサーバーをCloudflareに変更
↓
CloudflareでActive確認
↓
Cloudflare PagesにカスタムドメインをActivate
```

## 手順

### 1. CloudflareにドメインをConnect

1. 「Workers & Pages」→プロジェクト→「Custom domains」
2. 「Set up a custom domain」→ドメイン入力→「Continue」
3. 「Begin DNS transfer」→「Continue to activation」
4. Cloudflareのネームサーバーが2つ表示される

### 2. XserverでネームサーバーをCloudflareに変更

1. Xserverドメイン管理画面にログイン
2. 「ネームサーバー設定」→「その他のサービスで利用する」
3. ネームサーバー1・2にCloudflareのアドレスを入力して保存

### 3. Cloudflareで確認・Active待ち

1. 「I updated my nameservers」を押す
2. 数十分〜1時間待つ
3. ステータスが「Active」になったら完了

### 4. カスタムドメインをActivate

1. 「Custom domains」→ドメイン入力→「Continue」
2. 「Activate domain」を押す

## ハマったポイント

- ネームサーバー変更前にカスタムドメインを設定しようとしても進めない
- Activeを確認してから改めてCustom domainsの設定をする（2段階）
- ネームサーバーアドレスは公開情報なので知られても問題ない

## 関連記事

- [XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
