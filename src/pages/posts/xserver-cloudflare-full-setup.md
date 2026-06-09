---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-05'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインをCloudflare Pagesのカスタムドメインに設定する全手順を解説。ネームサーバー変更からDNS設定・HTTPS化まで紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesで公開しているAstroサイトのカスタムドメインに設定したかった。`*.pages.dev`のURLから独自ドメインに変えるのが目的だったが、ネームサーバーの変更からActive待ち、カスタムドメインの有効化まで手順が複数あって全体像がつかめなかった。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

最初、Cloudflare PagesのプロジェクトからCustom domainsで直接ドメインを入力して進もうとした。ドメイン名を入力して「Continue」を押したら「ネームサーバーを変更してください」という画面になった。「後でネームサーバーを変更すればいいか」と「Activate domain」を押したら、ステータスがずっと「Pending」のままで先に進めなかった。

ネームサーバーをXserverで変更しようとしたが、どこで変更するのかがわからなかった。Xserverのサーバーパネルを探したが見つからず、Xserverアカウント（旧インフォパネル）という別の管理画面にあることを調べてようやくわかった。

変更後にCloudflareが「Active」になるまで何をすればいいのかもわからず、「Active後にもう一度Custom domainsから設定が必要」という2段階の手順になっているとは最初知らなかった。

## 解決策

全体の流れを先に把握しておくと迷わない。

```
① Cloudflareでネームサーバーのアドレスを確認
    ↓
② XserverのネームサーバーをCloudflareに変更
    ↓
③ CloudflareがActiveになるまで待つ（数十分〜1時間）
    ↓
④ Cloudflare PagesのCustom domainsでドメインを有効化
    ↓
⑤ HTTPSが有効になって完了
```

### 1. CloudflareにドメインをConnectしてネームサーバーを確認

Cloudflareダッシュボードにログインして「Websites」→「Add a site」でドメイン名を入力する。プランはFreeを選択。「Continue」で進んでいくと画面に2つのネームサーバーが表示される。このアドレスをメモしておく（例：`vera.ns.cloudflare.com`のような形式）。

### 2. XserverでネームサーバーをCloudflareに変更

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする（サーバーパネルとは別のページ）。

「ドメイン」→「ドメイン設定一覧」→対象ドメインの「ネームサーバー設定」を開く。

「その他のサービスで利用する」を選択して、Cloudflareから取得したネームサーバー1・2を入力して保存する。

### 3. CloudflareでActiveを確認する

Cloudflareに戻って「I updated my nameservers」ボタンを押す。ステータスが「Pending Nameserver Update」から「Active」に変わるまで待つ。だいたい30分〜1時間で変わる。

メールで「Cloudflare is now protecting your site」という通知が来たらActive。

```bash
# コマンドラインで確認する場合
nslookup -type=NS yourdomain.com
```

Cloudflareのネームサーバーが返ってくればOK。

### 4. Cloudflare PagesのCustom domainsでドメインを有効化

**Active確認後に**、Cloudflare PagesのプロジェクトからCustom domainsに進む。

1. 「Workers & Pages」→プロジェクト→「Custom domains」タブ
2. 「Set up a custom domain」→ドメイン名を入力→「Continue」
3. DNS設定の確認画面が出たら「Activate domain」をクリック

数分でHTTPSが有効になってカスタムドメインでサイトが見えるようになった。

### 5. HTTPSの確認

ブラウザで`https://yourdomain.com`にアクセスして、鍵マークが表示されていれば完了。

詳細な確認方法は[Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)を参照。

## ハマったポイント

- ネームサーバーが「Active」になる前にCustom domainsでドメインを設定しようとしても進めない。ステータスがPendingのまま止まる。「Active後に改めてCustom domainsの設定をする」という2段階になっているとは最初知らなかった
- Xserverはサーバーパネルとアカウントパネルが別々の管理画面で、ネームサーバー設定はアカウントパネル（`xapanel`）の方にある。サーバーパネルを1時間探し続けたのは完全に無駄だった
- 「その他のサービスで利用する」に切り替えるとXserver側でのサイト表示ができなくなる。Xserverのホスティングでサイトを動かしている場合は注意が必要（今回はCloudflare Pagesで動かすので問題なし）
- Activeになった後にCloudflare Pagesのプロジェクトでもう一度Custom domainsから「Activate domain」を押す必要がある。これを知らずに「Activeになったのになぜサイトが独自ドメインで見えないのか」と30分悩んだ
- カスタムドメイン設定後、`*.pages.dev`のURLでもサイトが見え続ける。どちらでもアクセスできるが、Search ConsoleにはカスタムドメインのURLで登録する

## 関連記事

- [XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)
- [Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
