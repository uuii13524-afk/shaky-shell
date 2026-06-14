---
title: 'XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順'
date: '2026-05-05'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインをCloudflare Pagesのカスタムドメインに設定する全手順を解説。ネームサーバー変更からDNS設定・HTTPS化まで紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesで公開しているAstroサイトのカスタムドメインに設定したかった。`*.pages.dev`のURLから独自ドメインに変えるのが目的だったが、手順が複数ステップにわたっていて全体像がつかめなかった。

ネームサーバーの変更・Active待ち・カスタムドメインの有効化が別々の作業として必要で、どこまで済んでいてどこが残っているかわからなくなった。特に「ネームサーバーの変更」と「Custom domainsでのActivate」が2段階になっているのを知らず、1段階目で終わったと思って待ち続けた時間があった。

設定が全部完了するまでに実作業は30分程度でも、Active待ちや確認の手間を含めると半日近くかかった。「なぜまだ見えないのか」を何度も調べていたので、最初から手順の全体像を把握していればもっと短く終わったと思う。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

最初、Cloudflare PagesのプロジェクトからCustom domainsで直接ドメインを入力して進もうとした。ドメイン名を入力して「Continue」を押したら「Please update your nameservers」という画面になった。「とりあえず先に進めるかも」と「Activate domain」を押したが、ステータスがずっと「Pending」のままで先に進めなかった。ネームサーバーを変更していないから当然なのだが、最初はその順番がわかっていなかった。

次にネームサーバーをXserverで変更しようとしたが、サーバーパネルのどこを探してもネームサーバーの設定が見つからなかった。「DNS設定」というメニューはあったが、これはAレコードやCNAMEを編集するもので、ネームサーバー自体の変更ではなかった。Xserverのサポートページを調べてようやく「Xserverアカウント（旧インフォパネル）という別の管理画面」にあることがわかった。

ネームサーバーをCloudflareに変更してActive待ちの間、「これでカスタムドメインの設定は完了したのでは」と思っていたが、実はActiveになってから**もう一度Cloudflare PagesのCustom domainsで操作が必要**だとわかって、作業が2段階になっているとは最初知らなかった。

Activeになって独自ドメインでアクセスしてみたら「Cloudflare 522 Connection Timed Out」のエラーページが出た。「PagesのCustom domains設定が終わっていない」が原因で、Cloudflareがトラフィックを受け取ったが転送先（Cloudflare Pages）が設定されていない状態だった。Custom domainsでActivateボタンを押してから5分後に再アクセスしたら正常に表示された。

「HTTPSにするには証明書が必要では？」とも悩んだ。Cloudflareのデフォルトが「Flexible SSL」なのか「Full SSL」なのかわからず、設定を間違えるとサイトにアクセスできなくなるのではと心配した。実際にはCustom domainsの設定が完了した時点でHTTPSは自動で有効になって、SSLの設定を別途触る必要はなかった。ただしEncryption Modeが「Flexible」のままだとセキュリティ的に望ましくないので、「Full」に変更した。

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

Cloudflareダッシュボード（`dash.cloudflare.com`）にログインして左サイドバー「Websites」→「Add a site」をクリック。ドメイン名（`example.com`の形式、`https://`なし）を入力してFreeプランを選択。

「Continue」で進むとCloudflareが現在のDNSレコードをスキャンする画面が出る。「Continue to activation」を押すと**2つのネームサーバーのアドレスが表示される**。

```
※このアドレスはアカウントごとに異なる
vera.ns.cloudflare.com
bob.ns.cloudflare.com
```

このアドレスをメモする。インターネット上の記事に書いてある`ns1.cloudflare.com`などは自分のアカウントでは使えないので、必ず自分の画面に表示されたアドレスを使う。

このタイミングでCloudflareがスキャンした既存DNSレコードを確認する。Xserverのメールを使っていた場合、MXレコードが正しくインポートされているか確認しておく。消えていた場合は手動で追加する。XserverのSPFレコード（TXTレコード）があればそれもインポートされているか確認しておくと、ネームサーバー変更後のメール送受信が安定する。

### 2. XserverでネームサーバーをCloudflareに変更

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする。サーバーパネル（`xapanel/server`）とは別のURLなので注意。

「ドメイン」→「ドメイン設定一覧」→対象ドメインの「ネームサーバー設定」を開く。

「その他のサービスで利用する」を選択。入力欄が2つ表示されるので、Cloudflareで確認したネームサーバー1・2のアドレスをそれぞれ入力して「確認」→「設定する」で保存する。

この時点でXserverでホスティングしているサイトは表示されなくなる（ドメインの向き先がCloudflareに変わるため）。今回はCloudflare Pagesに完全移行するので問題ない。

詳細な手順は[XserverドメインのネームサーバーをCloudflareに変更する方法](/posts/xserver-cloudflare-nameserver)にまとめた。

### 3. CloudflareでActiveを確認する

Cloudflareに戻って「I updated my nameservers」ボタンを押す。**このボタンを押し忘れるとCloudflareが確認を開始しないので必ず押す。** ステータスが「Pending Nameserver Update」から「Active」に変わるまで待つ。だいたい30分〜1時間で変わるが、DNS伝播には最長72時間かかることもある。

Activeになったら「Cloudflare is now protecting your site」というメールが届く。

コマンドラインでも確認できる。

```bash
nslookup -type=NS yourdomain.com
```

以下のようにCloudflareのネームサーバーが返ってくればOK。

```
yourdomain.com  nameserver = vera.ns.cloudflare.com
yourdomain.com  nameserver = bob.ns.cloudflare.com
```

手元のDNSキャッシュが古い場合は正確な結果が出ない。Windowsの場合は`ipconfig /flushdns`でキャッシュをクリアしてから再確認する。

外部のDNS確認サービス（`dnschecker.org`など）で世界各地からの解決結果を確認すると、ローカルのキャッシュ問題かどうかの切り分けができる。

### 4. Cloudflare PagesのCustom domainsでドメインを有効化

**ActiveになってからPagesの設定に進む。Activeになる前に進もうとしてもPendingのままで進めない。**

1. Cloudflare「Workers & Pages」→ プロジェクトを選択
2. 「Custom domains」タブを開く
3. 「Set up a custom domain」ボタンをクリック
4. ドメイン名（`example.com`）を入力して「Continue」
5. DNS設定の確認画面が出たら内容を確認して「Activate domain」をクリック

数分でHTTPSが有効になってカスタムドメインでサイトが見えるようになった。

ステータスが「Active」になったことをCustom domainsのページで確認する。「Initializing」や「Pending」のままの場合は数分待ってからページをリロードする。

Activateボタンを押した後にDNSレコードがCloudflareのDNS設定に自動追加される。Cloudflare PagesのプロジェクトはIPアドレスではなくCNAMEレコードを使って接続する。`yourdomain.com`に対してCloudflare Pagesのアドレス（`プロジェクト名.pages.dev`）を向けるCNAMEが自動作成される。

### 5. HTTPSの確認

ブラウザで`https://yourdomain.com`にアクセスして鍵マークが表示されていれば完了。

`http://`でアクセスしても`https://`にリダイレクトされるのを確認しておく。HTTP→HTTPSの自動リダイレクトはCloudflareのSSL/TLS設定でデフォルトで有効になっている。

Cloudflare SSL/TLSのEncryption Modeは「Flexible」と「Full」がある。Cloudflare PagesではデフォルトでHTTPSが有効なので「Full」に設定するのが正しい。「Flexible」のままにしておくとセキュリティ上の問題が出ることがある。SSL/TLSの設定はCloudflareダッシュボードの左メニュー「SSL/TLS」から確認できる。

「Full (strict)」はオリジンに有効な証明書が必要で、Cloudflare Pages自体は正式な証明書を持っているので「Full (strict)」に設定しても問題ない。「Flexible」→「Full」→「Full (strict)」の順で厳格になる。迷ったら「Full」でOK。

詳細な確認方法は[Cloudflareで独自ドメインのSSL設定を確認する方法](/posts/cloudflare-ssl-check)を参照。

### 6. wwwありURLの設定

`www.yourdomain.com`でもアクセスできるようにしたい場合は、Custom domainsに`www.yourdomain.com`も追加する。追加するとCloudflare側でCNAMEレコードが自動設定される。

ただし`www.yourdomain.com`を追加した場合、どちらを正規URLにするかを決めておく必要がある。Search Consoleにはどちらか一方のURLで登録して、もう一方はリダイレクト設定にするのが一般的。Cloudflare Pages側ではどちらも同じコンテンツを返すだけなので、Cloudflareのリダイレクトルールで`www`なし→`www`あり（またはその逆）を設定する。

wwwなしに統一する場合のRedirect Rulesの設定（Cloudflareダッシュボード→「Rules」→「Redirect Rules」）:

```
If: Hostname equals www.yourdomain.com
Then: Dynamic redirect to https://yourdomain.com${uri}（301）
```

### 7. Search ConsoleをカスタムドメインURLで登録

`*.pages.dev`のURLはカスタムドメイン設定後も引き続きアクセスできる。2つのURLが共存する状態になるが、Search Consoleにはカスタムドメインの`https://yourdomain.com`で登録する。`*.pages.dev`で登録してしまうと本来のドメインのインデックス状況が別管理になってしまう。

## ハマったポイント

- ネームサーバーが「Active」になる前にCustom domainsでドメインを設定しようとしても「Pending」のまま何も進まない。「Active後に改めてCustom domainsの設定をする」という2段階になっているとは最初知らなかった。Activeになってからもう一度Pagesの設定に戻る手順がある
- Xserverはサーバーパネル（`xapanel/server`）とアカウントパネル（`xapanel`）が別々の管理画面で、ネームサーバー設定はアカウントパネルの方にある。「ドメイン管理はサーバーパネルにある」という思い込みで1時間以上無駄にした
- 「その他のサービスで利用する」に切り替えるとXserver上のWebサイトが表示されなくなる。Xserverでホスティングしている別のサイトがある場合は注意が必要。今回はCloudflare Pagesに完全移行するので問題なかった
- Activeになった後にCloudflare Pagesのプロジェクトで「Custom domains」からもう一度「Activate domain」を押す必要があった。「Activeになったのになぜ独自ドメインで見えないのか」と30分近く悩んだが、Pages側のCustom domainsの設定が別途必要だった。その間「522 Connection Timed Out」が出続けていた
- Cloudflare SSL/TLSのEncryption Modeが「Flexible」になっていると、HTTPSが有効のように見えても実際はCloudflare→オリジン間がHTTPになる問題がある。Cloudflare PagesはフルHTTPSなので「Full」に設定しておく
- `*.pages.dev`のURLはカスタムドメイン設定後も引き続きアクセスできる。2つのURLが共存する状態になる。Search ConsoleにはカスタムドメインのURLで登録する
- ネームサーバーのアドレスはCloudflareアカウントごとに割り当てが異なる。他の記事に書いてある`ns1.cloudflare.com`などを入力しても動かない。自分のCloudflareダッシュボードに表示されたアドレスを使う必要があった
- www付きとwwwなしの両方でアクセスできるが、Googleはどちらかを正規URLとして扱う。どちらに統一するかをRedirect Rulesで設定しないと、www有り・無しで別々にインデックスされる可能性がある。設定が完了したら`https://www.yourdomain.com`と`https://yourdomain.com`の両方でアクセスして期待通りにリダイレクトされるか確認した
- Cloudflareに「I updated my nameservers」ボタンがあることを見落とすと、ずっとPendingのままになる。画面内に小さく表示されているボタンで、押さないとCloudflareが確認を開始しない

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
