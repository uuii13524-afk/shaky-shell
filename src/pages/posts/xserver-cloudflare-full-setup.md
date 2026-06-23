---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-05'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインをCloudflare Pagesのカスタムドメインに設定する全手順を解説。ネームサーバー変更からDNS設定・HTTPS化まで紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesで公開しているAstroサイトのカスタムドメインに設定したかった。`*.pages.dev`のURLから独自ドメインに変えるのが目的だったが、手順が複数ステップにわたっていて全体像がつかめなかった。

さらに複雑にしていたのが、同じXserverの同じドメインで以前からWordPressサイトを運営していた点だ。「ネームサーバーをCloudflareに変えたらWordPressは動かなくなるのか」という不安があり、それを確認しながら進める必要があった。結論から言うと、ネームサーバーをCloudflareに変えた時点でXserver上のWordPressは表示されなくなった。事前にWordPressのデータをエクスポートしておいたのは正解だった。

「ネームサーバーの変更」と「Cloudflare PagesのCustom domainsでActivate」が2段階になっているのを知らず、1段階目で終わったと思って待ち続けた時間があった。設定が全部完了するまでに実作業は30分程度でも、Active待ちや確認の手間を含めると半日近くかかった。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

**ネームサーバー変更前にCustom domainsでActivateしようとした → Pendingのまま**

最初、Cloudflare PagesのプロジェクトからCustom domainsで直接ドメインを入力して進もうとした。「とりあえず先に進めるかも」と「Activate domain」を押したが、ステータスがずっと「Pending」のままで先に進めなかった。ネームサーバーを変更していないから当然だが、最初はその順番がわかっていなかった。Activeになってから改めてCustom domainsの設定に戻る必要があるとわかるまで30分近く無駄にした。

**ネームサーバーのActiveだけで設定が完了したと思っていた → 独自ドメインで見えなかった**

ネームサーバーをCloudflareに変更してActiveになった。「これでカスタムドメインの設定は完了した」と思って独自ドメインでブラウザを開いたが、Cloudflare Pagesのサイトは表示されなかった。「ActiveになったらPagesの設定に戻って改めて『Activate domain』を押す」という2段階が必要だとわかるまで30分待ち続けた。ネームサーバーのActive≠カスタムドメインの有効化、という2段階構造が最初わかっていなかった。

**Activateしても522エラーが続いた → 古いAレコードが残っていた**

Pagesで「Activate domain」を押したのに「522 Connection Timed Out」エラーが数分続いた。「失敗した」と思ってもう一度Activateを押したが変わらなかった。CloudflareのDNS設定画面を開いたら、ネームサーバースキャン時に取り込んだXserverのAレコード（`192.168.xxx.xxx`のような形式）がそのまま残っていた。そのAレコードがCloudflare PagesのCNAMEより優先されてXserverの旧IPに向いていたのが原因だった。Aレコードを削除したら数分後に正常に表示されるようになった。

## 解決策

全体の流れを先に把握しておくと迷わない。

```
① CloudflareでネームサーバーのアドレスをConfirm
    ↓
② XserverのネームサーバーをCloudflareに変更
    ↓
③ CloudflareがActiveになるまで待つ（30分〜1時間）
    ↓
④ Cloudflare PagesのCustom domainsでドメインをActivate
    ↓
⑤ HTTPSが有効になって完了
```

### 1. CloudflareにドメインをConnectしてネームサーバーを確認

Cloudflareダッシュボード（`dash.cloudflare.com`）にログインして左サイドバー「Websites」→「Add a site」をクリック。ドメイン名を入力してFreeプランを選択。

「Continue to activation」を押すと**2つのネームサーバーのアドレスが表示される**。

```
※このアドレスはアカウントごとに異なる
vera.ns.cloudflare.com
bob.ns.cloudflare.com
```

インターネット上の記事に書いてある`ns1.cloudflare.com`などは自分のアカウントでは使えない。必ず自分の画面に表示されたアドレスを使う。

このタイミングでCloudflareがスキャンした既存DNSレコードを確認する。Xserverのメールを使っていた場合、MXレコードが正しくインポートされているか確認しておく。

### 2. XserverでネームサーバーをCloudflareに変更

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする。サーバーパネル（`xapanel/server`）とは別のURLなので注意。

「ドメイン」→「ドメイン設定一覧」→対象ドメインの「ネームサーバー設定」を開く。「その他のサービスで利用する」を選択して、Cloudflareのネームサーバー2つを入力して保存する。

この時点でXserverでホスティングしているサイトは表示されなくなる（ドメインの向き先がCloudflareに変わるため）。今回はCloudflare Pagesに完全移行するので問題ない。

詳細な手順は[XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)にまとめた。

### 3. CloudflareでActiveを確認する

Cloudflareに戻って「I updated my nameservers」ボタンを押す。**このボタンを押し忘れるとCloudflareが確認を開始しないので必ず押す。** ステータスが「Pending Nameserver Update」から「Active」に変わるまで待つ。だいたい30分〜1時間。

Activeになったら「Cloudflare is now protecting your site」というメールが届く。コマンドラインでも確認できる。

```bash
nslookup -type=NS yourdomain.com
```

Cloudflareのネームサーバーが返ってくればOK。手元のDNSキャッシュが古い場合はWindowsで`ipconfig /flushdns`を実行してから再確認する。

### 4. Cloudflare PagesのCustom domainsでドメインを有効化

**ActiveになってからPagesの設定に進む。Activeになる前に進もうとしてもPendingのままで進めない。**

1. Cloudflare「Workers & Pages」→ プロジェクトを選択
2. 「Custom domains」タブを開く
3. 「Set up a custom domain」ボタンをクリック
4. ドメイン名（`example.com`）を入力して「Continue」
5. DNS設定の確認画面が出たら内容を確認して「Activate domain」をクリック

Activateボタンを押した後、数分でHTTPSが有効になってカスタムドメインでサイトが見えるようになった。

Activateボタンを押した直後は「522 Connection Timed Out」が出ることがある。この時点でDNSに古いAレコードが残っているケースを疑う。CloudflareのDNS設定画面（「Websites」→ドメイン→「DNS」→「Records」）を開いてXserverのIPを指すAレコードが残っていれば削除する。削除後に数分待てば解消する。

### 5. HTTPSの確認

ブラウザで`https://yourdomain.com`にアクセスして鍵マークが表示されていれば完了。

Cloudflare SSL/TLSのEncryption Modeは「Flexible」ではなく「Full」に設定する。「Flexible」のままにしておくとCloudflare→オリジン間がHTTPになり、Cloudflare Pagesがさらにリダイレクトしようとして無限ループが発生することがある。SSL/TLSの設定はCloudflareダッシュボードの左メニュー「SSL/TLS」から確認できる。

詳細な確認方法は[Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)を参照。

### 6. wwwありURLの設定

`www.yourdomain.com`でもアクセスできるようにしたい場合は、Custom domainsに`www.yourdomain.com`も追加する。どちらかに統一するRedirect Rulesを設定しないと、www有り・無しで別々にインデックスされる可能性がある。

wwwなしに統一する場合のRedirect Rules（「Rules」→「Redirect Rules」）:

```
If: Hostname equals www.yourdomain.com
Then: Dynamic redirect to https://yourdomain.com${uri}（301）
```

`${uri}`を含めることでパスごとのリダイレクトが正しく動く。設定後は記事ページのURLでもリダイレクトが正しく動くか確認する。

### 7. Search ConsoleをカスタムドメインURLで登録

`*.pages.dev`のURLはカスタムドメイン設定後も引き続きアクセスできる。Search Consoleにはカスタムドメインの`https://yourdomain.com`で登録する。`*.pages.dev`で登録してしまうと本来のドメインのインデックス状況が別管理になってしまう。

## ハマったポイント

- ネームサーバーがActiveになる前にCustom domainsでドメインをActivateしようとしても「Pending」のまま何も進まない。「①ネームサーバーのActive → ②PagesのCustom domainsでActivate」という2段階になっているとは知らなかった。1段階目が完了しても独自ドメインでは見えないまま、2段階目の操作が別途必要だった
- Xserverのネームサーバー設定はサーバーパネル（`xapanel/server`）ではなくアカウントパネル（`xapanel`）にある。「ドメイン管理はサーバーパネル」という思い込みで1時間近く探し続けた。URLの末尾が`/server`ではなくドメインが`xapanel`で終わる方が正解だった
- Cloudflareの「I updated my nameservers」ボタンを押し忘れるとずっとPendingのままになる。画面内に目立たないリンクとして表示されているが、このボタンを押してからCloudflareが確認を開始する仕組みになっている。30分待っても変わらない場合はまずこのボタンを押したか確認する
- Activateボタンを押した直後の「522 Connection Timed Out」は一時的なものだと思って5分待ったが、5分以上続いた場合はCloudflareのDNS設定に古いAレコードが残っているのが原因だった。XserverのIPを指すAレコードがCNAMEより優先されていたため522が続いた。DNS設定画面でAレコードを削除したら即座に解消した
- Encryption Modeを「Flexible」のままにしていたら無限リダイレクトが起きた。「Flexible」ではCloudflare→オリジン間がHTTPになるが、Cloudflare Pagesがさらにリダイレクトしようとしてループが発生する。「Full」に変えたら即座に解消した。Cloudflare Pagesを使う場合は「Full」に設定しておくのが正しい

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
