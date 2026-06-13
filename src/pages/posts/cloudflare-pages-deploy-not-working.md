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

自動デプロイが止まる原因は複数あって、「ビルドが来ない」「ビルドは来るが失敗する」「デプロイは成功するがサイトに反映されない」の3パターンに分けて考えると原因を絞り込みやすかった。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub（private/publicどちらでも発生）
- Astro 5.2.3
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

まず「何か変なコードを入れたか？」と思ってgit diffで確認したが、問題になりそうなコードはなかった。ローカルで`npm run build`したら正常に通った。コードの問題ではないとわかったが、では何が原因なのか見当がつかなかった。

次にCloudflareのDeploymentsタブを全部見直したが、「Failed」のビルドがあるわけではなく、そもそも新しいビルドが全く来ていなかった。ビルドエラーがあれば原因を探せるが、ビルドが始まっていない状態ではどこを見ればいいかわからなかった。「ビルドが失敗している」と「ビルド自体が来ていない」は全く別の問題で、診断の入口が変わってくる。

「もう一度pushすれば直るかも」と思って`git push --force`まで試したが何も起きなかった。GitHubのリポジトリにはちゃんとコミットが積まれているのに、Cloudflareがそれを全く検知していなかった。

GitHubのリポジトリSettings → Webhooksを確認したら、Cloudflare Pagesが登録しているWebhookのdeliveryを確認できた。直近のdeliveryを開いてレスポンスを見たら、HTTPステータスが`401 Unauthorized`になっていた。

```
POST https://api.cloudflare.com/client/v4/pages/webhooks/deploy/...
Response: 401
{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]}
```

これはCloudflareとGitHubの認証が切れているサインだとわかった。CloudflareがGitHubのWebhookを受け取り拒否している状態で、OAuthトークンの有効期限が切れていた。

別のケースでは、ビルドは来ているのに「Deploymentsタブに新しいビルドは来るが、本番サイトが更新されない」という状況も経験した。原因を調べたら、本番ブランチの設定が`main`のままなのに、作業していたブランチが`master`だったことが判明した。Cloudflareは指定されたブランチのpushしかデプロイのトリガーにしないので、ブランチ名が合っていないとビルド自体が来ない。

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

## ハマったポイント

- 空のコミットのpushが最も確実な強制デプロイ方法。`--allow-empty`オプションを知らなくて最初は1文字だけ追加したファイルをコミットしてはpushという無駄な作業をしていた
- ビルドが「来ていない」のか「来ているが失敗している」のかで原因が全然違う。Deploymentsタブを最初に開いて状態を確認するのが一番早い診断だった。「Failed」が来ていれば原因3、何も来ていなければ原因1か2
- Settings → Git repositoryの「Manage」ボタンは分かりにくい場所にある。Settingsタブを開いてかなり下にスクロールした先にある。プロジェクトのトップ画面では見えない
- 再認証後に「GitHubにもうpush済みだから大丈夫」と思い込んでいたが、Cloudflareは認証復旧後に過去のコミットを遡ってビルドしてくれない。認証回復後に空コミットpushが別途必要だと気づくまで20分以上待ち続けた
- GitHubのWebhookのdeliveryログを見ると、Cloudflareへの通知が成功しているか失敗しているかがわかる。Settings → Webhooksから各deliveryのレスポンスを確認できる。`401`が出ていたらOAuth切れ、`200`が出ていたらCloudflare側のビルド設定の問題
- デプロイが止まったタイミングと最後にGitHubのセキュリティ設定を変更したタイミングが一致していた。2段階認証の設定変更後にOAuth接続が切れることがあるので、セキュリティ設定を変えた後はCloudflareのデプロイを確認する
- `master`ブランチで作業してpushしていたのに、CloudflareのProduction branchが`main`に設定されていてデプロイが走らなかったことがあった。ブランチ名の不一致は気づきにくいので、接続時に設定したブランチ名を定期的に確認しておくといい

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
