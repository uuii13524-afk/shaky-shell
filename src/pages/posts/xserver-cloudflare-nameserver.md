---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインのネームサーバーをCloudflareに変更する手順を解説。Cloudflareへのドメイン追加・ネームサーバー設定の確認方法を紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定しようとしたら、まずネームサーバーをCloudflareに向け直す必要があった。Xserverのドメイン管理画面でどこを触ればいいのかわからず詰まった。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

最初、CloudflareのダッシュボードでWorkers & Pages→プロジェクト→「Custom domains」から「Set up a custom domain」を試みた。ドメインを入力して進むと「ネームサーバーを変更してください」という画面になったが、どのネームサーバーをどこに入力すればいいのかわからなかった。

次にXserverのサーバーパネル（サーバー管理画面）を探してみたが、ドメインの設定はサーバーパネルではなく「Xserverアカウント（旧インフォパネル）」の方にあった。同じ会社なのに管理画面が2つあって混乱した。サーバーパネルをいくら探してもネームサーバー設定が出てこないので、調べてようやく別画面だとわかった。

Xserverアカウントにログインしてから「ドメイン」→「ネームサーバー設定」に進んだが、「Xserver指定のネームサーバー」が最初から選ばれていた。「その他のサービスで利用する」という選択肢があったが、これを選ぶとXserverの機能（メールなど）が使えなくなるのではないかと思って躊躇した。

## 解決策

Cloudflareが指定するネームサーバー2つをXserverに登録する。手順は以下の通り。

### 1. Cloudflareでネームサーバーを確認する

Cloudflareダッシュボードにログインして左メニューの「Websites」から「Add a site」でドメインを追加する。プランを選択する画面が出るが、Freeで問題ない。進むと2つのネームサーバーが表示される。

```
ns1.cloudflare.com  ← ※実際に表示されるアドレスは各アカウントで異なる
ns2.cloudflare.com
```

この2つのアドレスをメモしておく（画面によって異なるので必ず自分のアカウントで確認する）。

### 2. Xserverアカウントでネームサーバーを変更する

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインして、「ドメイン」→「ドメイン設定一覧」→対象ドメインの「ネームサーバー設定」をクリックする。

「その他のサービスで利用する」を選択して、Cloudflareから取得したネームサーバー1・2を入力して保存する。

### 3. CloudflareでActiveになるまで待つ

Cloudflareのダッシュボードに戻って「I updated my nameservers」ボタンを押す。ステータスが「Pending」から「Active」になるまで待つ。数十分〜最長72時間かかるが、だいたい1時間以内には反映された。

```bash
# 反映確認コマンド（ターミナルから）
nslookup -type=NS yourdomain.com
```

Cloudflareのネームサーバーが返ってくればOK。

### 4. Activeになったらカスタムドメイン設定へ

Activeになってからでないとカスタムドメインの設定が進められない。Activeを確認してから[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)の手順でカスタムドメインを設定する。

## ハマったポイント

- CloudflareにはWorkers用のダッシュボードとPages用のダッシュボードが別にあって、最初どこから設定するのか迷った。ネームサーバーの取得はCloudflareの「Websites」セクションから行う
- Xserverはサーバーパネルとアカウントパネルが2つ存在していて、ネームサーバー設定はアカウントパネル（旧インフォパネル）の方にある。これを知らずに1時間サーバーパネルを探し続けた
- 「その他のサービスで利用する」を選ぶとXserverのメール機能やFTP機能が使えなくなるのかと思ったが、Xserverでホスティングしているサイトのデータはそのままで、ドメインの向き先だけ変わるだけだった
- Active待ちの間に焦ってリロードを繰り返したが、Pending→Activeへの変化は自動で反映されるので待つしかない
- Activeになってから「もうカスタムドメインの設定は完了している」と勘違いしたが、Activeはあくまでネームサーバーの変更が反映されただけで、Cloudflare Pages側のカスタムドメイン設定は別途必要だった

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
