---
title: 'Cloudflare PagesのGitHub自動デプロイが動かない時の対処法'
date: '2026-05-04'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'git pushしてもCloudflare Pagesに変更が反映されない原因と解決方法を解説。GitHub連携の確認やビルドコマンドの見直しポイントを紹介します。'
---

## やりたかったこと

記事を更新してgit pushしたのに、Cloudflare Pagesのサイトに変更が全然反映されなかった。いつもは1〜2分で更新されるのに、30分待っても何も変わらない。Deploymentsタブを開いたら新しいデプロイが一切来ておらず、最後のデプロイが昨日のままになっていた。

最初は「自分の回線の問題かも」と思ってスマホのモバイル回線でもサイトを確認した。同じ古い内容が表示されていた。「Cloudflare側がキャッシュを返しているのでは」とも考えたが、サイト自体は問題なく表示されているのでサーバー障害ではないと判断した。ここが最初の判断ミスで、「サイトが表示される＝デプロイが動いている」という思い込みがあった。実際にはキャッシュされた古いバージョンが表示され続けていただけで、デプロイ自体は完全に止まっていた。

プロジェクトのトップを確認したら薄いオレンジのバナーがあった。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

「May cause」という曖昧な書き方だったので深刻に受け止めていなかったが、これが原因だった。

自動デプロイが止まる原因は「ビルドが来ない」「ビルドは来るが失敗する」「デプロイは成功するがサイトに反映されない」の3パターンに分かれる。最初にDeploymentsタブを開いて「ビルドが来ているかどうか」だけ確認する一手間が、診断時間を大幅に短縮する。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub（private/publicどちらでも発生）
- Astro 5.2.3
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

**コードを疑ってローカルでビルド確認 → コードの問題ではなかった**

「変なコードを入れたか？」と思って`git diff`で確認したが問題なし。ローカルで`npm run build`したら正常に通った。コードの問題ではないとわかったが、ではなぜデプロイが来ないのかわからなかった。

次にDeploymentsタブを全部見直したが「Failed」のビルドがあるわけではなく、新しいビルド自体が全く来ていなかった。「ビルドが失敗している」と「ビルドが来ていない」は全く別の問題で、診断の入口が変わってくる。ここで「ビルドが来ていない」のだから接続の問題だとすぐ気づくべきだったが、ビルド設定を疑ってSettings画面を調べ始めてしまった。

**`git push --force`まで試した → 何も起きなかった**

「もう一度pushすれば直るかも」と`git push`を再実行し、最終的に`git push --force`まで試したが、Cloudflareは全く反応しなかった。GitHubとCloudflareの接続が切れているのだから、どんな形でpushしても届かない。pushが成功しても「GitHubにコミットが届いた」というだけで、「Cloudflareがそのpushをトリガーにビルドした」とは別のことだった。

GitHubのWebhook deliveryログを確認したら、最新エントリのHTTPステータスが`401 Unauthorized`になっていた。

```
POST https://api.cloudflare.com/client/v4/pages/webhooks/deploy/...
Response: 401
{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]}
```

これでOAuthトークンの失効が原因だと確定した。

**ブランチ名の不一致でビルドが来なかったケース（別の機会）**

別の日に`master`ブランチで作業してpushしていたのに、CloudflareのProduction branchが`main`に設定されていてデプロイが走らないことがあった。`git branch`でカレントブランチを確認したら確かに`master`だった。`git checkout main`して`git merge master`してから`git push origin main`でビルドが来た。

**ビルド成功なのにサイトが更新されないケース**

ビルドは来るし「Success」になるのにサイトが更新されない現象もあった。CloudflareのCDNキャッシュが古いものを返し続けていたのが原因で、「Purge Cache」を手動で実行したら解決した。Cloudflareダッシュボードの「Caching」→「Configuration」→「Purge Everything」でキャッシュを削除できる。

## 解決策

原因は3パターン。Deploymentsタブの状態を最初に確認して絞り込む。

```
Deploymentsタブを開く
  │
  ├─ 新しいビルドが0件（最後のデプロイが昨日以前）
  │   ├─ プロジェクトトップにオレンジのバナーあり → 原因1（OAuth切断）
  │   └─ バナーなし → GitHubのWebhookを確認 → 401が返っている → 原因1
  │                                             → Deliveryが1件もない → 原因2
  │
  └─ 新しいビルドエントリあり
        ├─ Failed → ビルドログを確認 → 原因3
        └─ Success → サイトが変わっていない → CDNキャッシュ → Purge Cache
```

### 原因1：CloudflareとGitHubの接続が切れている

**Deploymentsタブにビルドが全く来ていない場合はほぼこれ。**

Cloudflareダッシュボードで「Settings」タブ（上部のタブ）→「Git repository」セクションの「Manage」→GitHubのOAuth認証画面で「Authorize Cloudflare Pages」を選択する。

再認証後は空コミットをpushしてデプロイをトリガーする。再認証しただけでは過去のコミットが遡ってデプロイされない。

```bash
git commit --allow-empty -m "force deploy"
git push
```

再認証後にGitHubのWebhooks画面の「Ping」ボタンを押すと疎通確認ができる。Pingのレスポンスが200なら成功、401なら再認証が不完全。

詳細は[Cloudflare PagesがGitHubと切断された時の対処法](/posts/cloudflare-github-disconnect)にまとめた。

### 原因2：監視ブランチの設定が合っていない

```bash
git branch   # 現在のブランチを確認
```

別ブランチで作業している場合はmainにマージしてpushする。

```bash
git checkout main
git merge 作業ブランチ名
git push origin main
```

リモートのデフォルトブランチ名の確認：

```bash
git remote show origin
# HEAD branch: の行に表示されるブランチ名を確認
```

CloudflareのSettings → Buildsで「Production branch」がこのブランチ名と一致しているか確認する。

### 原因3：ビルドエラーが出ている

Deploymentsタブ→該当ビルド→「View build logs」でエラー内容を確認する。よくあるエラーと対処：

```
Error: Cannot find module '@astrojs/sitemap'
```
→ `package.json`の`dependencies`に含まれているか確認。`devDependencies`に入れると本番ビルドでインストールされない。

```
Error: Build failed with exit code 1
```
→ Settings → Environment variablesで`NODE_VERSION=20`を追加する。

```
Build exceeded the time limit of 20 minutes
```
→ 画像の最適化処理や大量ページのビルドで発生。`npm run build`のローカル実行時間を計測して原因箇所を特定する。

ビルドログが大量ある場合は「Download logs」でテキストとして保存してから`Error:`で検索するのが最速。

### CDNキャッシュの問題

ビルドが「Success」でもサイトが更新されないように見える場合は、CDNキャッシュが残っていることがある。

Cloudflareダッシュボードでドメインを選択→「Caching」→「Configuration」→「Purge Cache」→「Purge Everything」でCDNキャッシュを全削除できる。

頻繁にPurgeするとCDNの効果が薄れるので、本当に「Success」なのにサイトが更新されない場合だけ使う。特定ページだけ怪しい場合は「Custom Purge」でURLを指定して部分削除できる。

### 問題が再発しないようにする

Cloudflare PagesのNotifications機能でビルド失敗のメール通知を設定する。「Workers & Pages」→プロジェクト→「Settings」→「Notifications」で設定できる。

pushした後は毎回Deploymentsタブを確認する習慣をつける。「2分でビルドが来るはず」という感覚が身につくと、来ない場合にすぐ気づける。

## ハマったポイント

- サイトが問題なく表示されていたので「回線の問題かも」と最初に疑ったが、Cloudflareのキャッシュが古いバージョンを返し続けていただけだった。「サイトが表示される＝デプロイが動いている」という思い込みを捨てて、まずDeploymentsタブを確認するのが正しかった
- 「ビルドが来ていない」のか「来ているが失敗している」のかで原因が全然違う。Deploymentsタブを最初に開いて状態を確認するのが一番早い診断だった。「Failedが来ていれば原因3、何も来ていなければ原因1か2」という切り分けだけ覚えておけばいい
- 再認証後に「GitHubにもうpush済みだから大丈夫」と思い込んでいたが、Cloudflareは認証復旧後に過去のコミットを遡ってビルドしてくれない。認証回復後に空コミットpushが別途必要だと気づくまで20分以上待ち続けた
- `master`ブランチで作業してpushしていたのに、CloudflareのProduction branchが`main`に設定されていてデプロイが走らなかった。ブランチ名の不一致は気づきにくい。接続時に設定したブランチ名を`git remote show origin`で定期的に確認する習慣が防止になる
- デプロイ「Success」なのにサイトが更新されない場合はCDNキャッシュが原因のことがある。ブラウザのハードリロードで変わらなければCloudflareのPurge Cacheで解決した。「ビルドはできているのに反映されない」という現象はキャッシュを真っ先に疑う

そもそもAstroをCloudflare Pagesに繋いでいない場合は[AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)を参考に初期設定を確認してほしい。

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
