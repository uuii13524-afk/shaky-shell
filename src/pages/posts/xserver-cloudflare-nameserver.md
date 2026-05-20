---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Cloudflare PagesにXserverで取得したカスタムドメインを設定したかった。

## 環境

- Xserverドメイン
- Cloudflare Pages
- Astro

## 手順

1. Cloudflareダッシュボードで「Workers & Pages」を開く
2. 該当プロジェクトの「Custom domains」タブを開く
3. 「Set up a custom domain」をクリック
4. ドメインを入力すると「Begin DNS transfer」が表示される
5. Cloudflareのネームサーバーが2つ発行される
6. Xserverドメインの管理画面を開く
7. 「ネームサーバー設定」→「その他のサービスで利用する」を選択
8. 発行されたネームサーバーを1・2に入力して保存
9. Cloudflareに戻り「I updated my nameservers」を押す
10. 数十分〜1時間程度でActiveになる

## ハマったポイント

- CloudflareにWorkers用とPages用の画面が別にあって迷った
- ネームサーバーの反映に数十分〜1時間かかるので焦らず待つ
- Activeになってから改めてCustom domainsでドメインを設定する必要がある

## 補足

ネームサーバーのアドレス自体は公開情報なので知られても問題ない。
設定を変更できるのはXserverのアカウントにログインした人だけ。