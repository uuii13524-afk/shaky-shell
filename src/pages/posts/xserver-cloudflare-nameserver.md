---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインのネームサーバーをCloudflareに変更する手順を解説。Cloudflareへのドメイン追加・ネームサーバー設定の確認方法を紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定しようとした。まずCloudflare Pagesのプロジェクトで「Custom domains」→「Set up a custom domain」を開いてドメインを入力したら、「ネームサーバーをCloudflareに変更してください」という画面が出てきた。指定された2つのネームサーバーのアドレスはわかったが、それをXserverのどこに入力すればいいのかが全くわからなかった。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

最初、CloudflareのダッシュボードでWorkers & Pages→プロジェクト→「Custom domains」から「Set up a custom domain」を試みた。ドメインを入力して進むと「Please update your nameservers」という画面になった。2つのネームサーバーのアドレスが表示されていたが、「どこに入力すれば...」という状態だった。Cloudflareの画面には「Go to your domain registrar」と書いてあるだけで、Xserverの具体的な操作方法は何も書いていなかった。

次にXserverのサーバーパネル（`https://secure.xserver.ne.jp/xapanel/server/`）にログインしてネームサーバーの設定を探した。「ドメイン」メニューはあったが、「ネームサーバー」に関する設定が見当たらなかった。「DNS設定」というメニューはあったが、これはドメインのDNSレコードを編集するもので、ネームサーバー自体を変更するものではなかった。サーバーパネルを30分以上探し回ったが見つからず詰まった。

「ネームサーバー設定はXserverアカウント（旧インフォパネル）の方にある」という情報をやっと見つけた。ただしこちらにログインしても「その他のサービスで利用する」という選択肢に切り替えることで本当にXserver側のサービスが全部使えなくなるのでは、という不安があって躊躇した。メールサービスや他の機能が壊れないか心配でしばらく踏み切れなかった。

## 解決策

Cloudflareが指定するネームサーバー2つをXserverアカウントパネルに登録する。

### 1. Cloudflareでドメインを追加してネームサーバーを確認する

Cloudflareダッシュボード（`dash.cloudflare.com`）にログインして左サイドバーの「Websites」を開く。「Add a site」ボタンをクリックしてドメイン名（`example.com`の形式で、`https://`なし）を入力する。

プランを選択する画面が出るのでFreeを選択して「Continue」。Cloudflareが現在のDNSレコードをスキャンする画面が出るのでそのまま「Continue to activation」を押す。次の画面で2つのネームサーバーのアドレスが表示される。

```
vera.ns.cloudflare.com  ← ※実際に表示されるアドレスは各アカウントで異なる
bob.ns.cloudflare.com
```

このアドレスはアカウントごとに異なるので、自分のダッシュボードに表示されたものを必ずメモしておく。

### 2. Xserverアカウントパネルでネームサーバーを変更する

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする。サーバーパネルとは別のURLなので注意。

「ドメイン」メニュー→「ドメイン設定一覧」を開く。対象ドメインが一覧に表示されているので右端の「ネームサーバー設定」リンクをクリックする。

ネームサーバーの選択画面が開く。「Xserver指定のネームサーバー」が最初から選ばれているが、「その他のサービスで利用する」に切り替える。2つのネームサーバー入力欄が表示されるので、Cloudflareから取得した2つのアドレスをそれぞれ入力して「確認」→「設定する」で保存する。

「その他のサービスで利用する」に切り替えても、Xserverのサーバー上にあるファイルやデータベースは消えない。ただし**ドメインの向き先がCloudflareに変わるので、Xserver上でホスティングしているサイトはそのままでは表示されなくなる**。今回はCloudflare Pagesでホスティングするので問題ない。

### 3. CloudflareでActiveになるまで待つ

Cloudflareのダッシュボードに戻って「I updated my nameservers」ボタンを押す。ステータスが「Pending Nameserver Update」から「Active」になるまで待つ。だいたい30分〜1時間で反映されるが、最大72時間かかることもある。

Activeになったらメールで「Cloudflare is now protecting your site」という通知が届く。

コマンドラインで確認する場合：

```bash
nslookup -type=NS yourdomain.com
```

Cloudflareのネームサーバーが返ってくるようになればDNSへの反映完了。

```
Server:  ...
Address: ...

Non-authoritative answer:
yourdomain.com  nameserver = vera.ns.cloudflare.com
yourdomain.com  nameserver = bob.ns.cloudflare.com
```

### 4. Activeになったらカスタムドメイン設定へ

Activeになってから[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)の手順でカスタムドメインを設定する。Active前に進もうとすると「Pending」のままで先に進めない。

## ハマったポイント

- ネームサーバーの設定はXserverの「サーバーパネル」ではなく「Xserverアカウント（アカウントパネル）」にある。URLが`xapanel/server`ではなく`xapanel`で終わる方が正解。これを知らずにサーバーパネルを1時間以上探し続けた
- Xserverアカウントのドメインメニューにある「DNS設定」は、Aレコードやサブドメインの編集画面で、ネームサーバーそのものを変更する画面ではない。「DNS設定」ではなく「ネームサーバー設定」が目的の画面だった
- 「その他のサービスで利用する」を選んでもXserverのサーバーデータは消えない。ただしドメインの向き先がXserverからCloudflareに変わるので、Xserverでホスティングしていたサイトは表示されなくなる。「切り替えたら全部消える」と勘違いして踏み切れない時間が長かった
- Active待ちの間にCloudflareのダッシュボードをリロードし続けたが、Pending→Activeへの変化は自動では変わらない。「I updated my nameservers」ボタンを押してもすぐに変わらないことがあり、メールを待つのが一番確実だった
- Activeになってから「もうカスタムドメインの設定は完了している」と思い込んだが、Activeはあくまでネームサーバーの変更が反映されただけだった。Cloudflare Pages側でもう一度「Custom domains」から設定する2段階の手順になっていた
- Cloudflareが表示するネームサーバーのアドレスはアカウントごとに異なる。ネット上の記事に書いてある`ns1.cloudflare.com`や`ns2.cloudflare.com`は自分のアカウントでは使えない。必ず自分のCloudflareダッシュボードに表示されたアドレスを入力する

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
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
