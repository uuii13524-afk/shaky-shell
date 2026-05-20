---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定したかった。
単純に見えるが、手順が複数ステップに分かれており、順番を間違えると詰まる。

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

1. Cloudflareダッシュボードで左メニュー「Workers & Pages」を開く
2. 該当プロジェクトをクリック
3. 「Custom domains」タブを開く
4. 「Set up a custom domain」をクリック
5. ドメイン名を入力して「Continue」
6. 「Begin DNS transfer」をクリック
7. 「Continue to activation」をクリック
8. Cloudflareのネームサーバーが2つ表示される（例：brenda.ns.cloudflare.com / seth.ns.cloudflare.com）
9. この2つをメモする

### 2. XserverでネームサーバーをCloudflareに変更

1. Xserverドメイン管理画面にログイン
2. 対象ドメインの「ネームサーバー設定」を開く
3. 「その他のサービスで利用する」を選択
4. ネームサーバー1・2にCloudflareのネームサーバーを入力
5. 「確認画面へ進む」→「設定する」で保存

### 3. Cloudflareで確認・Active待ち

1. Cloudflareに戻り「I updated my nameservers」を押す
2. 数十分〜1時間程度待つ
3. Cloudflareダッシュボードでドメインのステータスが「Active」になったら完了

### 4. カスタムドメインをActivate

1. 再度「Workers & Pages」→プロジェクト→「Custom domains」を開く
2. 「Set up a custom domain」→ドメインを入力→「Continue」
3. DNS recordの確認画面が出るので「Activate domain」を押す
4. 数分でカスタムドメインが有効になる

## ハマったポイント

- ネームサーバー変更前にカスタムドメインを設定しようとしても進めない
- Cloudflareには「Workers用」と「Pages用」の画面が別にある。Custom domainsはPages用の画面から設定する
- ネームサーバーのActiveを確認してから改めてCustom domainsの設定をする必要がある（2段階）
- ネームサーバーアドレス自体は公開情報なので知られても問題ない。変更できるのはXserverにログインした人だけ

## 補足

ネームサーバー変更後、古いDNS情報がキャッシュされている場合は反映に時間がかかることがある。
焦らず待つのが正解。
