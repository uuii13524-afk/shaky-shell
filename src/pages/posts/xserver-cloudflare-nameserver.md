---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインのネームサーバーをCloudflareに変更する手順を解説。Cloudflareへのドメイン追加・ネームサーバー設定の確認方法を紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインに設定しようとした。Cloudflare Pagesのプロジェクトで「Custom domains」→「Set up a custom domain」を開いてドメインを入力したら「ネームサーバーをCloudflareに変更してください」という画面になった。

Cloudflareが指定する2つのネームサーバーのアドレスはわかった。問題は「それをXserverのどこに入力すればいいのか」が全くわからなかったことだ。

```
vera.ns.cloudflare.com
bob.ns.cloudflare.com
```

「ネームサーバー」という言葉自体なじみがなく、「DNSと同じもの？」「変えたら今のサイトが壊れる？」という不安が先行した。さらにネットで調べても「Xserverのサーバーパネルで変更する」と書いている記事と「アカウントパネルで変更する」と書いている記事が混在していて、どちらが正しいかわからなかった。

実際に手を動かしてから「サーバーパネルには設定がない」と気づくまで30分かかった。

作業前に、今のDNS設定をスクリーンショットで全部保存した。Xserverのアカウントパネルのネームサーバー設定画面と、DNS設定の一覧画面を撮影してフォルダに保存した。「変更したら元の設定がわからなくなる」という不安が強かったので、これをやっておいたことで作業中に余計なプレッシャーを感じずに済んだ。特にMXレコードの値はテキストファイルにも転記しておいた。これが後で役に立った。

ネームサーバーとDNSの違いも最初わかっていなかった。「ネームサーバー＝DNSを管理するサーバーをどこにするか」「DNS設定＝そのサーバーの中でAレコードやMXレコードをどう設定するか」という関係で、XserverのネームサーバーをCloudflareに変えるということはDNS管理の権限をXserverからCloudflareに渡すことだった。この整理ができてから作業の全体像がやっと見えた。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

**Xserverサーバーパネルを1時間探した → ネームサーバー設定はなかった**

最初にXserverのサーバーパネル（`https://secure.xserver.ne.jp/xapanel/server/`）にログインしてネームサーバー設定を探した。「ドメイン」メニュー配下を全部クリックしたが「ドメイン設定」「サブドメイン設定」「DNS設定」「ドメイン移管」しかなく、ネームサーバーの変更はどこにもなかった。「DNS設定」を開いてみたが、これはAレコードやCNAMEを編集する画面でネームサーバー自体を変更するものではなかった。「DNS設定＝ネームサーバーを変更する場所」だと思い込んでいた。

XserverのサポートページをやっとAを見つけたら「ネームサーバー変更はXserverアカウント（旧インフォパネル）から行う」とあった。サーバーパネルとは別のURLにある別の管理画面だった。これを知らずに40分以上探した。

**Cloudflareが表示するネームサーバーのアドレスを間違えた → 30分何も起きなかった**

ネットの記事に「`ns1.cloudflare.com`を入力する」と書いてあったので、Xserverの入力欄にそのアドレスを入れた。30分待っても何も変わらなかった。調べたらCloudflareのネームサーバーはアカウントごとに異なる割り当てになっていて、自分のダッシュボードに表示されたアドレス（`vera.ns.cloudflare.com`など）以外は使えないことがわかった。自分のCloudflareダッシュボードに表示された正しいアドレスに入力し直したら先に進めた。

**変更直後にnslookupで確認した → 古い情報が返ってきてパニックになった**

ネームサーバーを変更してフォームを送信した直後に確認しようとした。

```bash
nslookup -type=NS yourdomain.com
```

結果はXserverの古いネームサーバーのままで、Cloudflareのアドレスが一切出てこなかった。「入力が間違っていたのか」と焦ってXserverの管理画面を何度も見直したが、設定画面には正しいアドレスが保存されていた。TTLのキャッシュが残っているだけで、1時間後に再確認したらCloudflareのアドレスが返ってくるようになっていた。変更直後に「反映されていない」と判断するのは早計だった。

さらに「I updated my nameservers」ボタンをCloudflare側で押し忘れていたのも時間のロスだった。このボタンを押してからCloudflareが確認プロセスを開始する仕組みになっている。30分間ひたすら画面をリロードし続けていた。

## 解決策

Cloudflareが指定するネームサーバー2つをXserverアカウントパネルに登録する。

### 1. Cloudflareでドメインを追加してネームサーバーを確認する

Cloudflareダッシュボード（`dash.cloudflare.com`）にログインして「Websites」→「Add a site」でドメインを追加する。Freeプランを選択して「Continue」→「Continue to activation」と進むと2つのネームサーバーのアドレスが表示される。

```
vera.ns.cloudflare.com  ← アカウントごとに異なる
bob.ns.cloudflare.com
```

このアドレスはアカウントごとに違う。ネット上の記事に書いてある`ns1.cloudflare.com`は他人のアカウント用なので使えない。

このタイミングでCloudflareが既存のDNSレコードをスキャンする。**メールを使っている場合はここでMXレコードが表示されるか確認する**。表示されていなければネームサーバー変更後にCloudflareのDNS設定で手動追加が必要。XserverのMXレコードは以下のような形式になる。

```
Type: MX
Name: @
Mail server: mail.xserver.ne.jp
Priority: 10
```

事前にスクリーンショットを撮っておいたMXレコードの値を手元に用意しておくと、後から手動追加する時に正確な値がわかって助かる。

### 2. Xserverアカウントパネルでネームサーバーを変更する

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする。サーバーパネルとは別のURL（`/server/`なしの方がアカウントパネル）。

「ドメイン」→「ドメイン設定一覧」→対象ドメインの「ネームサーバー設定」を開く。「Xserver指定のネームサーバー」から「その他のサービスで利用する」に切り替えて、Cloudflareのネームサーバーを2つ入力し「確認」→「設定する」で保存する。

「その他のサービスで利用する」に切り替えてもXserverのサーバー上のファイルやデータベースは消えない。ただし**ドメインの向き先がCloudflareに変わるので、Xserverでホスティングしているサイトはそのままでは表示されなくなる**。

### 3. CloudflareでActiveになるまで待つ

Cloudflareのダッシュボードに戻って「I updated my nameservers」ボタンを押す。**このボタンを押さないとCloudflareが確認を開始しない。**

```bash
nslookup -type=NS yourdomain.com
```

Cloudflareのネームサーバーが返ってくるようになるまで待つ。だいたい30分〜1時間。

```
yourdomain.com  nameserver = vera.ns.cloudflare.com
yourdomain.com  nameserver = bob.ns.cloudflare.com
```

Windowsでキャッシュが古い場合は`ipconfig /flushdns`でクリアしてから再確認する。`dnschecker.org`で世界各地からの解決結果を確認すると、ローカルのキャッシュ問題か実際の伝播待ちかが切り分けられる。

### 4. ネームサーバー変更後にDNSレコードを確認する

ActiveになったらCloudflareのDNS設定画面でレコードを確認する（「Websites」→ドメイン→「DNS」→「Records」）。

**MXレコードのプロキシ（オレンジの雲アイコン）がオンになっている場合は必ずオフにする。** MXレコードをプロキシ経由にするとメールが届かなくなる。

SPFレコード（TXTレコード）がインポートされているかも確認する。Xserverのメール用のSPFレコード（`v=spf1 include:xserver.ne.jp ~all`のようなTXTレコード）が引き継がれていない場合、メール送信時にSPF認証失敗で迷惑メール扱いされることがある。

### 5. Activeになったらカスタムドメイン設定へ

Activeになってから[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)の手順でカスタムドメインを設定する。ネームサーバーの変更だけではカスタムドメインの設定は完了していない。Active後にCloudflare Pagesのプロジェクト設定でもう一度操作が必要になる。

## ハマったポイント

- ネームサーバーの変更場所はXserver「サーバーパネル」ではなく「Xserverアカウント（アカウントパネル）」にある。URLが `xapanel/server` ではなく `xapanel` で終わる方が正解。「ドメイン管理はサーバーパネルにある」という思い込みで1時間以上探し続けた
- Cloudflareのダッシュボードに表示されるネームサーバーのアドレスはアカウントごとに異なる。ネット上の記事に書いてある`ns1.cloudflare.com`を入力してしまうと、30分待っても何も変わらない。必ず自分のダッシュボードに表示されたアドレスを使う
- 変更直後に`nslookup`で確認して「古いアドレスが返ってきた」とパニックになったが、TTLのキャッシュが残っているだけだった。最低でも30分〜1時間待ってから確認するのが正しく、変更直後の`nslookup`結果で「失敗した」と判断するのは早計
- 「I updated my nameservers」ボタンをCloudflare側で押し忘れていると、ずっとPendingのままになる。このボタンを押してからCloudflareが確認を開始する仕組みなので、最初に必ず押す
- CloudflareのDNS設定でMXレコードのプロキシがオンになっていると、メールが届かなくなる。MXレコードはプロキシをオフ（グレーの雲）にしておく必要があった。Cloudflareがインポートしたレコードが全部プロキシオンになっていたので、MXレコードだけオフに切り替えた

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
