---
title: 'Cloudflare PagesのGitHub自動デプロイが動かない時の対処法'
date: '2026-05-04'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'git pushしてもCloudflare Pagesに変更が反映されない原因と解決方法を解説。GitHub連携の確認やビルドコマンドの見直しポイントを紹介します。'
---

## やりたかったこと

記事を更新してgit pushしたのに、Cloudflare Pagesのサイトに変更が全然反映されなかった。いつもは1〜2分で更新されるのに、30分待っても何も変わらない。Deploymentsタブを開いたら新しいデプロイが一切来ておらず、最後のデプロイが昨日のままになっていた。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

という黄色いバナーがプロジェクトのトップに表示されていた。「May cause」と書いてあるので軽い警告だと思ってしばらく無視していたが、実際には完全にデプロイが止まっていた。

自動デプロイが止まる原因は複数あって、「ビルドが来ない」「ビルドは来るが失敗する」「デプロイは成功するがサイトに反映されない」の3パターンに分けて考えると原因を絞り込みやすかった。最初にこの分類を知っていれば、診断にかかった1時間が半分以下で済んだと思う。

なお、「自動デプロイが動かない」という問題にはDeploymentsタブの状態によって2つの全然違う原因がある。「Deploymentsタブが静かなまま何もない」状態と「DeploymentsタブにビルドはあるがFailed」状態では、見るべき場所がまったく違う。最初にDeploymentsタブを開いて「ビルドが来ているかどうか」だけ確認する一手間が、診断時間を大幅に短縮する。

自動デプロイが1時間以上反応しない場合、まず疑うべきは「GitHubとCloudflareのOAuth接続が切れていないか」だった。直感的には「ビルド設定が壊れた」と考えがちだが、実際には接続切断が一番多い原因だった。GitHubにpushできているのにCloudflareが反応しない場合は、接続の問題を最初に調べる方が結果的に速い。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub（private/publicどちらでも発生）
- Astro 5.2.3
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

まず「何か変なコードを入れたか？」と思ってgit diffで確認したが、問題になりそうなコードはなかった。ローカルで`npm run build`したら正常に通った。コードの問題ではないとわかったが、では何が原因なのか見当がつかなかった。

次にCloudflareのDeploymentsタブを全部見直したが、「Failed」のビルドがあるわけではなく、そもそも新しいビルドが全く来ていなかった。ビルドエラーがあれば原因を探せるが、ビルドが始まっていない状態ではどこを見ればいいかわからなかった。「ビルドが失敗している」と「ビルド自体が来ていない」は全く別の問題で、診断の入口が変わってくる。

「もう一度pushすれば直るかも」と思って`git push --force`まで試したが何も起きなかった。GitHubのリポジトリにはちゃんとコミットが積まれているのに、Cloudflareがそれを全く検知していなかった。

Cloudflareのプロジェクト設定に問題があるかと思って「Settings」タブを全部確認した。「Build & deployments」の設定でProduction branchが`main`になっていてGitHubのデフォルトブランチも`main`だったので、ブランチ設定のズレではないとわかった。Environment variablesの設定も問題なかった。設定画面を隅々まで確認して「設定ファイルは全部正しい」とわかった後で「じゃあなぜビルドが来ないのか」という状況だった。

GitHubのリポジトリSettings → Webhooksを確認したら、Cloudflare Pagesが登録しているWebhookのdeliveryを確認できた。直近のdeliveryを開いてレスポンスを見たら、HTTPステータスが`401 Unauthorized`になっていた。

```
POST https://api.cloudflare.com/client/v4/pages/webhooks/deploy/...
Response: 401
{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]}
```

これはCloudflareとGitHubの認証が切れているサインだとわかった。CloudflareがGitHubのWebhookを受け取り拒否している状態で、OAuthトークンの有効期限が切れていた。

別のケースでは、ビルドは来ているのに「Deploymentsタブに新しいビルドは来るが、本番サイトが更新されない」という状況も経験した。原因を調べたら、本番ブランチの設定が`main`のままなのに、作業していたブランチが`master`だったことが判明した。Cloudflareは指定されたブランチのpushしかデプロイのトリガーにしないので、ブランチ名が合っていないとビルド自体が来ない。

git logでコミット履歴を確認したら`master`ブランチにはpushできていたが、Cloudflareの設定が`main`を監視しているため完全に無視されていた。`git branch`でカレントブランチを確認したら確かに`master`だった。`git checkout main`と`git merge master`でmainにマージしてから`git push origin main`したらDeploymentsタブにビルドが来た。ブランチ名の不一致というシンプルな原因だったが、気づくまでに30分かかった。

また別の機会に、ビルドは来るし「Success」になるのにサイトが更新されないという現象もあった。ブラウザのキャッシュではなく、CloudflareのCDNキャッシュが古いものを返し続けていたのが原因だった。CloudflareのキャッシュはDeploymentsが成功してもすぐには更新されないことがあって、「Purge Cache」を手動で実行したら解決した。Cloudflareダッシュボードの「Caching」→「Configuration」→「Purge Everything」で全キャッシュを削除できる。

さらに、Cloudflare PagesがGitHubのWebhookを受け付けているかを確認する前に、Cloudflareのステータスページ（`cloudflarestatus.com`）でサービス障害がないかも確認した。稀にCloudflare Pages自体が一時的な障害中のことがあり、その場合はしばらく待つだけで解決する。自分の場合は障害ではなかったが、診断の最初に確認しておくことで無駄な作業を省けた。

## 解決策

原因は3パターンある。「Deploymentsタブにビルドが来ているか来ていないか」を最初に確認して、上から順に確認していくのが早い。

### 原因1：CloudflareとGitHubの接続が切れている

**Deploymentsタブにビルドが全く来ていない場合はほぼこれ。** プロジェクトのトップに黄色いバナーが出ている場合も同様。

Cloudflareダッシュボードでプロジェクトを開き、「Settings」タブ（上部メニュー）→「Git repository」セクションの「Manage」をクリックする。GitHubのOAuth認証画面が開くのでログインしてアクセスを許可する。

再認証後は空のコミットをpushして強制的にデプロイをトリガーする。再認証しただけでは過去のコミットが遡ってデプロイされない。

```bash
git commit --allow-empty -m "force deploy"
git push
```

これでDeploymentsタブにビルドが来て解決した。GitHubのSettings → Applications → Authorized OAuth Appsも確認して、Cloudflareのエントリが「Revoked」になっていないか確認しておく。

再認証後にDeploymentsタブでビルドが来ない場合は、GitHubのWebhooksページで「Recent Deliveries」の最新エントリを確認する。`200`が返っているか確認して、`401`や`403`が返っている場合はまだ認証が通っていない。

GitHubのWebhook設定画面の「Ping」ボタンを押して、その場でCloudflareへの疎通確認ができる。Pingを送った後のDelivery結果に`200`が返ってくれば接続は復旧している。`401`が返ってくれば再認証が不完全なので、Authorize OAuth Appsのページを確認してCloudflareのエントリが「Revoked」ではなく正常な権限を持っているかを見直す。

詳細な切断・再接続の手順は[Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)にまとめた。

### 原因2：監視ブランチの設定が合っていない

Cloudflare Pagesは特定のブランチのpushしか監視しない。デフォルトは`main`ブランチだが、作業ブランチが違う場合はデプロイが走らない。

```bash
git branch  # 現在のブランチを確認
git status  # どのブランチにいるか確認
```

別ブランチで作業している場合はmainにマージしてpushする。

```bash
git checkout main
git merge 作業ブランチ名
git push origin main
```

または、Cloudflare PagesのSettings → Buildsで「Production branch」の設定を確認して、実際にpushしているブランチ名と一致しているか確認する。`main`でpushしているのに`master`と設定されていると動かない。

リポジトリのデフォルトブランチ名はGitHubのSettings → Default branchから確認できる。ローカルとCloudflareとGitHubのすべてで同じブランチ名になっているか確認するのが確実。

ブランチ名の確認は以下でも確認できる。

```bash
git remote show origin
```

`HEAD branch:`の行に表示されるブランチ名がリモートのデフォルトブランチ名。これがCloudflareの設定と合っているかを見る。

### 原因3：ビルドエラーが出ている

Deploymentsタブにビルド自体は来ているが「Failed」になっている場合は、ビルドエラーが原因。

Deploymentsタブ→該当ビルド→「View build logs」でエラー内容を確認する。よくあるエラーと対処法：

```
Error: Cannot find module '@astrojs/sitemap'
```
→ `package.json`のdependenciesに含まれているか確認。devDependenciesに入れてしまうと本番ビルド時にインストールされない。

```
Error: Build failed with exit code 1
```
→ ビルドコマンドやNode.jsのバージョンを確認。「Settings」→「Environment variables」で`NODE_VERSION`を`20`に指定する。

```
× Rendering /posts/xxx...
  Error: Cannot read properties of undefined
```
→ Astroのレンダリングエラー。該当ページのMarkdownやコンポーネントの記述ミスが原因のことが多い。ローカルで`npm run build`して同じエラーが再現するか確認する。ローカルで再現すれば原因のファイルが特定できる。

```
Build exceeded the time limit of 20 minutes
```
→ ビルド時間超過。画像の最適化処理や大量ページのビルドで発生することがある。`npm run build`のローカル実行時間を計測して、異常に時間がかかるページを探す。

```
error Failed to load config from /opt/buildhome/repo/vite.config.ts
```
→ Viteの設定ファイルのパスが解決できない。Cloudflare Pagesのビルド環境でのパス解決が問題になっていることがある。`vite.config.ts`のalias設定を確認する。

### ビルドログの見方

Deploymentsタブ→対象ビルドのリンクをクリック→「Build logs」タブを開くと、ビルドの全ログが確認できる。

```
Installing dependencies...
npm warn deprecated xxx
...
✓ Completed
Building Astro site...
  → 26 pages built in 3.21s
✓ Build completed in 4.5s
```

この形で「Build completed」が出れば成功。途中でエラーが出ている行を探すと原因を特定しやすい。ビルドログは下から上に読むと最終的なエラーメッセージが先に見つかることが多い。

ビルドが途中で止まってログが「Timed out waiting for build to start」になっている場合は、Cloudflare側のビルドキューが詰まっていることがある。数分後に「Retry deployment」ボタンで再試行してみる。

ビルドログが大量に出る場合は「Download logs」でローカルに落としてテキストエディタで検索するのが速かった。ブラウザでスクロールしながら探すより`Error:`で全文検索した方が圧倒的に早い。

### CDNキャッシュの問題

ビルドが「Success」でも本番サイトが更新されていないように見える場合は、CDNキャッシュが残っていることがある。

- Shift+Reload（ブラウザのハードリロード）でブラウザキャッシュをクリアして確認
- それでも変わらなければCloudflareのキャッシュを削除する

Cloudflareダッシュボードでドメインを選択→「Caching」→「Configuration」→「Purge Cache」→「Purge Everything」でCDNキャッシュを全削除できる。Purge後は次のアクセス時にオリジン（Cloudflare Pagesのサーバー）から新しいコンテンツを取得する。

「Purge Everything」はサイト全体のキャッシュを削除するので、Purge直後は全てのページで通常より少しレスポンスが遅くなる。頻繁にPurgeするとCDNの効果が薄れるので、本当に「Success」なのにサイトが更新されない場合にだけ使うほうがよかった。特定のページだけ怪しい場合は「Custom Purge」でURLを指定して部分削除する方法もある。

### 問題が再発しないようにする

自動デプロイが止まるのは一度経験すると「また止まってないか」と不安になる。以下の対策をとっておくと早期発見できる。

Cloudflare PagesのNotifications機能でビルド失敗のメール通知を設定する。「Workers & Pages」→プロジェクト→「Settings」→「Notifications」で設定できる。ビルドが失敗した時に即座にメールが届くので、長時間気づかずに放置する状況を防げる。

GitHubにpushした後は毎回Deploymentsタブを確認する習慣をつける。慣れてくると「2分でビルドが来るはず」という感覚が身につくので、来ない場合にすぐ気づけるようになる。プッシュしたら必ずブラウザでDeploymentsタブを一度開いてビルドが走り始めているのを確認してからターミナルを閉じる、という習慣が予防になった。

## ハマったポイント

- 空のコミットのpushが最も確実な強制デプロイ方法。`--allow-empty`オプションを知らなくて最初は1文字だけ追加したファイルをコミットしてはpushという無駄な作業をしていた
- ビルドが「来ていない」のか「来ているが失敗している」のかで原因が全然違う。Deploymentsタブを最初に開いて状態を確認するのが一番早い診断だった。「Failed」が来ていれば原因3、何も来ていなければ原因1か2
- Settings → Git repositoryの「Manage」ボタンは分かりにくい場所にある。Settingsタブを開いてかなり下にスクロールした先にある。プロジェクトのトップ画面では見えない
- 再認証後に「GitHubにもうpush済みだから大丈夫」と思い込んでいたが、Cloudflareは認証復旧後に過去のコミットを遡ってビルドしてくれない。認証回復後に空コミットpushが別途必要だと気づくまで20分以上待ち続けた
- GitHubのWebhookのdeliveryログを見ると、Cloudflareへの通知が成功しているか失敗しているかがわかる。Settings → Webhooksから各deliveryのレスポンスを確認できる。`401`が出ていたらOAuth切れ、`200`が出ていたらCloudflare側のビルド設定の問題
- GitHubのWebhook設定画面にある「Ping」ボタンを使えばその場で疎通確認ができた。再認証後にPingを送ってレスポンスが200かどうかを確認するのが、deliveryの一覧を眺めるより速かった。このボタンの存在に気づくまでPingの使い方を知らなかった
- デプロイが止まったタイミングと最後にGitHubのセキュリティ設定を変更したタイミングが一致していた。2段階認証の設定変更後にOAuth接続が切れることがあるので、セキュリティ設定を変えた後はCloudflareのデプロイを確認する
- `master`ブランチで作業してpushしていたのに、CloudflareのProduction branchが`main`に設定されていてデプロイが走らなかったことがあった。ブランチ名の不一致は気づきにくいので、接続時に設定したブランチ名を定期的に確認しておくといい
- デプロイ「Success」なのにサイトが更新されない場合はCDNキャッシュが原因のことがある。ブラウザのハードリロードで変わらなければCloudflareのPurge Cacheで解決した。「ビルドはできているのに反映されない」という現象はキャッシュを真っ先に疑う
- Cloudflare自体のサービス障害が原因のことも稀にある。`cloudflarestatus.com`を最初に確認すると、自分のアカウントの問題かCloudflare全体の問題かをすぐに切り分けられる。障害中であれば自分で何をしても解決しないので待つだけでいい
- ビルドログが大量にあって「Build completed」の行を探すのに5分かかったことがあった。「Download logs」でテキストファイルとして保存して`Build completed`を検索するのが一番速い確認方法だった。ブラウザ上のログビューアをスクロールする方法はログが1000行を超えると現実的ではなかった

そもそもAstroをCloudflare Pagesに繋いでいない場合は[AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)を参考に初期設定を確認してほしい。環境変数が足りていてビルドが失敗している場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参照。

## 関連記事

- [Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)

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
