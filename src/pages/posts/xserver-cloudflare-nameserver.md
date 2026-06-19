---
title: 'XserverドメインのネームサーバーをCloudflareに変更する方法'
date: '2026-05-02'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'XserverのドメインのネームサーバーをCloudflareに変更する手順を解説。Cloudflareへのドメイン追加・ネームサーバー設定の確認方法を紹介します。'
---

## やりたかったこと

Xserverで取得したドメインをCloudflare Pagesのカスタムドメインとして設定しようとした。まずCloudflare Pagesのプロジェクトで「Custom domains」→「Set up a custom domain」を開いてドメインを入力したら、「ネームサーバーをCloudflareに変更してください」という画面が出てきた。

指定された2つのネームサーバーのアドレスはわかったが、それをXserverのどこに入力すればいいのかが全くわからなかった。「ネームサーバー」という言葉自体初めて聞いたレベルで、「DNSと同じもの？」「変えたら今のサイトが壊れる？」と不安が先行して、1時間以上調べ回ってから作業に入ることになった。

さらに手順を調べても「Xserverのサーバーパネルで変更する」と書いている記事と「アカウントパネルで変更する」と書いている記事が混在していて、どちらが正しいかも最初わからなかった。実際に手を動かしてから「サーバーパネルには設定がない」と気づくまで30分かかった。

ネームサーバーとDNSの違いも最初理解できていなかった。ざっくり言うと「ネームサーバー＝DNSを管理するサーバーをどこにするか」で、「DNS設定＝そのサーバーの中でAレコードやMXレコードをどう設定するか」という関係になっている。XserverのネームサーバーをCloudflareに変えるということは、DNS管理の主導権をXserverからCloudflareに渡すということだった。この整理ができてから、作業の全体像がやっと見えた。

メールに関しては特に慎重だった。Xserverのメールアカウント（info@yourdomain.comなど）を使っている場合、ネームサーバーを変更するとMXレコードの管理もCloudflareに移る。Cloudflareのスキャンで既存のMXレコードが自動インポートされることがほとんどだが、もし取り込まれていなかった場合はメールが届かなくなる。「切り替えたらメールが止まった」という状況になった後で気づくのでは遅いので、変更前にMXレコードの確認を習慣にすることにした。

## 環境

- Xserverドメイン（2026年5月時点）
- Cloudflare Pages（Freeプラン）
- Astro 5.2.3
- 使用ドメイン：独自ドメイン（.com）

## 試したこと・うまくいかなかったこと

最初、CloudflareのダッシュボードでWorkers & Pages→プロジェクト→「Custom domains」から「Set up a custom domain」を試みた。ドメインを入力して進むと「Please update your nameservers」という画面になった。2つのネームサーバーのアドレスが表示されていたが、「どこに入力すれば...」という状態だった。Cloudflareの画面には「Go to your domain registrar」と書いてあるだけで、Xserverの具体的な操作方法は何も書いていなかった。

次にXserverのサーバーパネル（`https://secure.xserver.ne.jp/xapanel/server/`）にログインしてネームサーバーの設定を探した。「ドメイン」メニューはあったが、「ネームサーバー」に関する設定が見当たらなかった。「DNS設定」というメニューはあったが、これはAレコードやCNAMEなどのDNSレコードを編集するもので、ネームサーバー自体（＝どのDNSサーバーが管理するか）を変更するものではなかった。「DNS設定とネームサーバー設定は別物」だと理解するまでに30分以上かかった。

Xserverサーバーパネルのどこかにネームサーバー設定がないかと「ドメイン」メニュー配下を全部クリックして確認したが、「ドメイン設定」「サブドメイン設定」「DNS設定」「ドメイン移管」という項目しかなく、ネームサーバーの変更はどこにもなかった。最終的にXserverのサポートページを確認したら「ネームサーバー変更はXserverアカウント（旧インフォパネル）から行う」という記述を見つけた。サーバーパネルを40分以上探してから、それは別の管理画面にあると知った時の徒労感は忘れられない。

「ネームサーバー設定はXserverアカウント（旧インフォパネル）の方にある」という情報をやっと見つけた。ただしこちらにログインしても、「その他のサービスで利用する」という選択肢に切り替えることで、Xserver側のWebサービスが全部使えなくなるのでは、という不安があって躊躇した。Xserverでメールアカウントを使っている場合はメールも届かなくなるのではと心配して、1時間近くその不安と戦った。

Xserverのサポートに問い合わせて確認したところ、「ネームサーバーを変更してもXserverサーバー上のファイルやデータベースは消えない。ドメインの向き先が変わるだけ」という回答だった。これで踏ん切りがついた。ただしメールについては「ネームサーバー変更後はCloudflare側でMXレコードを設定し直す必要がある」という条件があったので、変更前にXserverのMXレコードの値をメモしておいた。

また、「Active待ち最大72時間」という記述を見て「変更したら3日間サイトが見えなくなるかも」とも恐れた。実際には30分〜1時間で変わったが、最悪のケースを想定して二の足を踏んでいた。

もう1つ詰まったのは、Cloudflareが表示するネームサーバーのアドレスが「vera.ns.cloudflare.com」のような形式だった点。ネットの記事には「ns1.cloudflare.com」などと書いてあるものが多く、「どちらが正しいのか」と混乱した。アカウントごとに割り当てが違うので、自分のダッシュボードに表示されたアドレス以外は使えないと後から知った。Xserverの入力欄に「ns1.cloudflare.com」を入力してしまって、30分待っても何も変わらずに「あれ？」となった。自分のダッシュボードに表示された正しいアドレスに入力し直したら解決した。

ネームサーバー変更後、Cloudflareのダッシュボードを30分ごとにリロードして「Pending→Active」への変化を待っていたが、一向に変わらなかった。「I updated my nameservers」ボタンをCloudflare側で押すのを忘れていたのが原因で、このボタンを押してからCloudflareが確認を開始するという流れだった。ボタンの存在に気づいておらず、ただひたすら画面を眺め続けていた。

Cloudflareへのドメイン追加時、「既存のDNSレコードを自動インポートする」というスキャン画面が出た。このスキャンで取り込まれたレコードをよく確認せずに「Continue」を押してしまったため、後からMXレコードが正しくインポートされていないことに気づいて手動で追加する羽目になった。スキャン直後の確認画面は流し読みせず、MXレコードやSPFレコードがちゃんと含まれているかをその場で確認するべきだった。

## 解決策

Cloudflareが指定するネームサーバー2つをXserverアカウントパネルに登録する。

### 1. Cloudflareでドメインを追加してネームサーバーを確認する

Cloudflareダッシュボード（`dash.cloudflare.com`）にログインして左サイドバーの「Websites」を開く。「Add a site」ボタンをクリックしてドメイン名（`example.com`の形式で、`https://`なし）を入力する。

プランを選択する画面が出るのでFreeを選択して「Continue」。Cloudflareが現在のDNSレコードをスキャンする画面が出るのでそのまま「Continue to activation」を押す。次の画面で2つのネームサーバーのアドレスが表示される。

```
vera.ns.cloudflare.com  ← ※実際に表示されるアドレスは各アカウントで異なる
bob.ns.cloudflare.com
```

このアドレスはアカウントごとに異なるので、自分のダッシュボードに表示されたものを必ずメモしておく。ネット上の記事に書いてある`ns1.cloudflare.com`などは他人のアカウント用のアドレスで、自分のアカウントでは使えない。

このスキャン画面で既存のDNSレコード（AレコードやMXレコードなど）がインポートされる。**メールを使っている場合はここでMXレコードが表示されるか確認しておく**。表示されていればネームサーバー変更後もメールは届く。表示されていない場合は手動でMXレコードを追加する必要がある。

XserverのメールサービスのMXレコードは以下のような形式になっている。Cloudflareがスキャン時に取り込めていない場合は、Cloudflareの「DNS」→「Records」で手動追加する。

```
Type: MX
Name: @（ドメインそのもの）
Mail server: mail.xserver.ne.jp
Priority: 10
```

スキャン結果のレコード一覧は後からCloudflareのDNS設定で確認・編集できるので、スキャン直後に完璧でなくても大丈夫だった。

MXレコード以外にも、Xserverのメールではない場合でもSPFレコード（TXTレコード）が設定されていることがある。SPFレコードが引き継がれていないと、変更後にメール送信時に「SPF認証失敗」として迷惑メール判定されるケースがある。スキャン結果でTXTレコードも確認しておくとよかった。

### 2. Xserverアカウントパネルでネームサーバーを変更する

Xserverアカウント（`https://secure.xserver.ne.jp/xapanel/`）にログインする。サーバーパネルとは別のURLなので注意。URLの末尾が `/server/` ではなく `/` で終わる方がアカウントパネル。

「ドメイン」メニュー→「ドメイン設定一覧」を開く。対象ドメインが一覧に表示されているので右端の「ネームサーバー設定」リンクをクリックする。

ネームサーバーの選択画面が開く。「Xserver指定のネームサーバー」が最初から選ばれているが、「その他のサービスで利用する」に切り替える。2つのネームサーバー入力欄が表示されるので、Cloudflareから取得した2つのアドレスをそれぞれ入力して「確認」→「設定する」で保存する。

「その他のサービスで利用する」に切り替えても、Xserverのサーバー上にあるファイルやデータベースは消えない。ただし**ドメインの向き先がCloudflareに変わるので、Xserver上でホスティングしているサイトはそのままでは表示されなくなる**。今回はCloudflare Pagesでホスティングするので問題ない。

Xserverのメールサービス（`info@yourdomain.com` 等）を使っている場合は要注意。ネームサーバーをCloudflareに変更するとMXレコードも含めてDNS管理がCloudflareに移る。Cloudflareがスキャン時に既存のMXレコードを自動インポートしていることが多いが、変更直後にメールの送受信を確認しておく。もしMXレコードが引き継がれていなかった場合はCloudflareのDNS管理画面でXserver側のMXレコードを手動追加する必要がある。

### 3. CloudflareでActiveになるまで待つ

Cloudflareのダッシュボードに戻って「I updated my nameservers」ボタンを押す。このボタンを押さないとCloudflareが確認を開始しないので必ず押す。ステータスが「Pending Nameserver Update」から「Active」になるまで待つ。だいたい30分〜1時間で反映されるが、最大72時間かかることもある。

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

`nslookup`がWindowsにない場合は、`Resolve-DnsName yourdomain.com -Type NS` をPowerShellで実行しても同様に確認できる。

Linuxの場合は`dig NS yourdomain.com`でも確認できる。

```bash
dig NS yourdomain.com +short
```

`vera.ns.cloudflare.com.`と`bob.ns.cloudflare.com.`が返ってきたら伝播完了。

DNS伝播の速度はIPアドレスのTTL（Time to Live）設定に依存する。XserverのデフォルトTTLは3600秒（1時間）に設定されていることが多いので、早くて1時間程度で切り替わる計算になる。焦って何度もnslookupで確認しても最初の30分は結果が変わらないことが多かった。

確認コマンドを実行しても変わらない場合は、ローカルのDNSキャッシュが古いことがある。Windowsなら`ipconfig /flushdns`でキャッシュをクリアしてから再確認する。

```cmd
ipconfig /flushdns
```

それでも古い結果が返る場合は、外部のDNSチェックサービスを使うとDNSが実際に伝播しているかを確認できる。`dnschecker.org`や`whatsmydns.net`でドメインを入力すると、世界各地のDNSサーバーからの解決結果を一度に確認できた。自分のローカル環境のキャッシュ問題なのか、まだ伝播が完了していないのかを切り分けるのに役立った。

### 4. ネームサーバー変更後にDNSレコードを確認する

ネームサーバーがActiveになったら、CloudflareのDNS設定画面でレコードの内容を確認する。「Websites」→ドメインを選択→「DNS」→「Records」で確認できる。

XserverからインポートされたMXレコードがある場合、Cloudflare上でMXレコードのオレンジの雲アイコン（プロキシ）がオンになっていることがある。**MXレコードはプロキシをオフ（グレーの雲）にしておく必要がある**。MXレコードをプロキシ経由にするとメールが届かなくなる。設定を見直して「DNS only」に変更する。

同様に、AレコードやCNAMEのプロキシ設定もCloudflareの動作に影響する。Cloudflare Pagesのカスタムドメインに使うCNAMEはプロキシあり（オレンジの雲）で問題ない。

MXレコードのプロキシオンオフ以外にも確認しておいたほうが良い点がある。Xserverのメール用のSPFレコード（`v=spf1 include:xserver.ne.jp ~all`のようなTXTレコード）が引き継がれているか確認した。SPFレコードが消えていたら手動で追加する。SPFレコードがないとCloudflareを経由してメールを送った際にSPF認証が失敗して迷惑メール扱いになることがあった。

メールの送受信が正常かどうかは、テストメールを自分宛てに送って返信が届くかで確認するのが一番シンプルだった。変更後15分ほどしてからテストメールを送ったら正常に受信できたので、MXレコードが正しく引き継がれていたとわかった。

### 5. Activeになったらカスタムドメイン設定へ

Activeになってから[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)の手順でカスタムドメインを設定する。Active前に進もうとすると「Pending」のままで先に進めない。ネームサーバーの変更だけではカスタムドメインの設定は完了していない。Active後にもう一度Cloudflare Pagesのプロジェクト設定で操作が必要になる。

## ハマったポイント

- ネームサーバーの設定はXserverの「サーバーパネル」ではなく「Xserverアカウント（アカウントパネル）」にある。URLが `xapanel/server` ではなく `xapanel` で終わる方が正解。これを知らずにサーバーパネルを1時間以上探し続けた。「ドメイン管理はサーバーパネルにある」という思い込みがあった
- Xserverアカウントのドメインメニューにある「DNS設定」は、AレコードやCNAMEなどのDNSレコードを編集する画面で、ネームサーバーそのものを変更する画面ではない。「DNS設定」ではなく「ネームサーバー設定」が目的の画面だった。「DNS設定に行けばネームサーバーも変えられる」と思い込んでいた
- 「その他のサービスで利用する」を選んでもXserverのサーバーデータ（ファイル・データベース）は消えない。ただしドメインの向き先がXserverからCloudflareに変わるので、Xserverでホスティングしていたサイトは表示されなくなる。「切り替えたら全部消える」と勘違いして踏み切れない時間が長かった
- Xserverでメールを使っていた場合、切り替え後にCloudflare側でMXレコードが正しく設定されているか確認が必要だった。CloudflareがDNSスキャン時に既存レコードをインポートしてくれることが多いが、必ず確認する。MXレコードが消えるとメールが届かなくなる
- Cloudflareのダッシュボードで「I updated my nameservers」ボタンを押し忘れると、ずっとPendingのままになる。このボタンを押してからCloudflareが確認プロセスを開始する。30分待ち続けてボタンの存在にやっと気づいた
- Cloudflareが表示するネームサーバーのアドレスはアカウントごとに異なる。ネット上の記事に書いてある`ns1.cloudflare.com`を入力してしまって30分何も起きなかった。必ず自分のCloudflareダッシュボードに表示されたアドレスを入力する。これを間違えると一向にActiveにならない
- Activeになってから「もうカスタムドメインの設定は完了している」と思い込んだが、Activeはあくまでネームサーバーの変更が反映されただけだった。Cloudflare Pages側でもう一度「Custom domains」から「Set up a custom domain」→「Activate domain」という操作が別途必要で、2段階の手順になっていた
- DNS伝播の速度はTTLに依存するため、切り替え直後の30分程度は変化が見られないことがある。何度`nslookup`で確認しても同じ結果が返ってきて「切り替えに失敗したかも」と焦ったが、単純に伝播待ちだった。ローカルのDNSキャッシュが原因のこともある。`ipconfig /flushdns`やdnschecker.orgで外部確認すると切り分けができた
- CloudflareのDNS設定でMXレコードのプロキシ設定がオンになっていると、メールが届かなくなる。MXレコードはプロキシをオフ（グレーの雲アイコン）にしておく必要があった。Cloudflareがインポートしたレコードが全部プロキシオンになっていたので、MXレコードだけオフに切り替えた
- SPFレコード（TXTレコード）がインポートされていなかった場合、メールが迷惑メール扱いされることがある。MXレコードの確認と合わせて、SPFレコードのTXTレコードも引き継がれているかを確認しておく必要があった。これに気づいたのはネームサーバー変更後2日経ってから届いていないメールがあると指摘されてからだった
- Active待ちの間にCloudflareのダッシュボードをリロードし続けたが、Pending→Activeへの変化は自動では変わらない。「I updated my nameservers」ボタンを押してもすぐに変わらないことがあり、メールを待つのが一番確実だった。自分の場合は約40分でActiveになった

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
