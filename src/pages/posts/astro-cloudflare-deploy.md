---
title: 'AstroをCloudflare Pagesにデプロイする手順'
date: '2026-05-03'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'AstroサイトをCloudflare Pagesにデプロイする手順を解説。GitHubとの連携設定・ビルドコマンドの指定・カスタムドメインの設定方法までわかりやすく紹介します。'
---

## やりたかったこと

Astroで作ったブログサイトをCloudflare Pagesで公開しようとした。これまでVercelしか使ったことがなかったが、Cloudflareの方がCDNの速度が良いと聞いて移行を考えた。Cloudflare PagesのUIがVercelと全然違って、最初どこから設定を始めればいいのかわからなかった。

「Workers & Pages」を開いたらWorkers用の画面しか見当たらず、Pagesの設定に入る場所が見つけにくくて詰まった。Vercelだと「New Project」を押してGitHubリポジトリを選ぶだけで全部繋がるのに、Cloudflareは同じノリでやったら全然違う画面が出てきた。結果的に最初のデプロイ完了まで3時間近くかかったが、2回目以降は5分でできるようになった。

Vercelとの比較で一番戸惑ったのは、Cloudflare Pagesの「Pages」という概念がWorkers & Pagesという一つの項目にまとまっていることだった。Vercelなら「Deploy」ボタンが一番目立つ場所にあるが、Cloudflareは「Create application」を押してからさらに「Pages」の画面を探す必要があった。

初回デプロイが成功するまでのトラブルは、大きく分けると「UI上でPageの設定に入れない」「ビルドコマンドの設定ミス」「環境依存のビルドエラー」の3段階に分かれていた。最初にこの3段階を理解していたら、もっと短時間で解決できたと思う。

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- GitHub（リポジトリ作成済み）
- Cloudflare Pages（Freeプラン）

## 試したこと・うまくいかなかったこと

最初、Cloudflareのダッシュボードにログインして「Workers & Pages」→「Create application」を押したら、「Create a Worker」という画面が出てきた。「Connect to Git」のようなボタンが見当たらず、Pagesの設定がどこにあるのかわからなかった。Workersの設定画面でAstroのリポジトリを繋ごうと右往左往した。

左側のサイドバーをすべて確認したが、「Pages」という独立したメニューはなかった。「Workers & Pages」が両方を兼ねているとわかるまで10分以上かかった。「Create application」を押した後の画面に**小さく**「Looking to deploy Pages? Get started here」というリンクがあって、それをクリックしないとPages用の画面に入れない作りだった。このリンクは画面の下の方にあって、上部だけ見ていると絶対に気づかない。

ビルドコマンドの設定で手動入力しようとして`npm run build`と`dist`を入れたが、Framework presetで「Astro」を選べば自動で入力されることを後から知った。手動でも問題ないが、Astroのpresetを使わないと`NODE_VERSION`などの推奨環境変数が設定されず、Cloudflare側のNode.jsバージョンが古くてビルドが失敗することがあった。

最初のビルドが`Error: Cannot find module`で失敗したが、ログをよく見たら`node_modules`が正しくインストールされていなかった。ローカルでは`npm install`済みなのに、Cloudflareは毎回クリーンな状態からビルドするのでリポジトリの`package.json`に書かれた依存が正しくないと失敗する。ローカルで`npm run build`が通るからCloudflareでも通ると思っていたが、Node.jsのバージョンが違うと同じコードでもエラーになることがあった。

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'sharp'
```

このエラーが出た時は`sharp`を`dependencies`ではなく`devDependencies`に入れていたのが原因だった。本番ビルドでは`devDependencies`はインストールされないので、使うパッケージは必ず`dependencies`に入れる必要があった。

さらに詰まったのが、Cloudflare PagesのGitHub認証画面で「Only select repositories」を選んでいたこと。後から新しいリポジトリを別に作ってCloudflareに接続しようとしたら、リポジトリの一覧に出てこなかった。「All repositories」に変更するか、GitHubのSettings → Applications → Cloudflare Pages → Repositoriesから個別に追加する必要があった。

ビルドログをDL（Download logs）して確認していたら、別のエラーが見つかった。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```

ローカルでは`site`を設定していなくても動いていたが、Cloudflare上でビルドすると`@astrojs/sitemap`プラグインが`site`の設定を要求してビルドが止まった。ローカルのdevモードとCloudflareのproductionビルドで動きが違う箇所がいくつかあって、ローカルテストだけでは見つけられないバグがあった。

また、gitリポジトリに`.gitignore`を作る前に`git add .`を実行してしまい、`node_modules/`がリポジトリに含まれた状態でpushしてしまった。Cloudflare側のビルドには直接影響しないが、リポジトリサイズが膨大になってpushに数分かかるようになった。この失敗から、最初に`.gitignore`を確認してから`git add .`することを必ず守るようにした。

## 解決策

### 1. Astroをインストールして動作確認

```bash
npm create astro@latest
cd プロジェクト名
npm run dev
```

`http://localhost:4321` でAstroの画面が出れば成功。

### 2. GitHubにpush

GitHubへの初回pushが初めての場合は、[GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)も参考に。

```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

pushする前に`.gitignore`に`node_modules/`と`.env`が含まれているか確認しておく。`node_modules`をpushしてしまうとCloudflareのビルドに時間がかかる上、ローカルとCloudflare側の環境差異で意図しない動作になることがある。

`.gitignore`の確認は以下のコマンドで。

```bash
cat .gitignore
```

`node_modules/`、`.env`、`dist/`が含まれていればOK。なければ追加してから`git add .gitignore && git commit -m "add gitignore"`する。

### 3. Cloudflare PagesにGitHubリポジトリを接続する

1. Cloudflareダッシュボードで「Workers & Pages」を開く
2. 「Create application」ボタンを押す
3. **画面下部**にある「Looking to deploy Pages? Get started here」をクリック（これを見落としやすい）
4. 「Import an existing Git repository」→「Get started」
5. GitHubアカウントを認証してリポジトリを選択
6. ビルド設定でFramework presetを「**Astro**」に変更する

Framework presetでAstroを選ぶと以下が自動入力される。

```
Build command: npm run build
Build output directory: dist
```

7. 「Save and Deploy」でデプロイ開始

初回ビルドは2〜3分かかる。Deploymentsタブでビルドログをリアルタイムで確認できる。

### 4. ビルドが失敗した時の対処

初回デプロイでビルドエラーになる場合は、Deploymentsタブ→該当ビルド→「View build logs」でエラー内容を確認する。ビルドログは量が多い場合は「Download logs」でテキストファイルとして保存してから`Error:`で検索すると原因が見つけやすい。

よくあるエラー：

```
Error: Cannot find module 'sharp'
```
→ `package.json`のdependenciesに`sharp`が入っているか確認する。`devDependencies`に入れてしまうと本番ビルドで読み込めない。

```
error: No matching version found for node@xx.x.x
```
→ Node.jsのバージョン不一致。Settings → Environment variablesで`NODE_VERSION`を`20`に指定する。

```
Build failed: 'astro' is not recognized
```
→ `npm install`が失敗している可能性。`package.json`の内容をローカルと比較して依存が正しいか確認する。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
```
→ `astro.config.mjs`に`site`プロパティがない。`site: 'https://yourdomain.com'`を追加する。

```
Build exceeded the time limit of 20 minutes
```
→ ビルド時間超過。画像の最適化処理が重い場合に起きやすい。`sharp`による画像変換を無効にするか、ビルドするページ数を絞る。

環境変数を設定したい場合はSettings → Environment variablesで追加する。`NODE_VERSION=20`は最初から設定しておくと安定する。

```
Environment variables:
NODE_VERSION = 20
```

Cloudflare PagesはデフォルトのNode.jsバージョンが古めに設定されていることがある。Astroは新しいNode.jsのAPIを使う箇所があるので、`NODE_VERSION`を明示的に指定するのがトラブル防止の基本だった。

### 5. ビルドログを効率よく読む方法

Cloudflare Pagesのビルドログは量が多くて読みにくい。効率よく原因を探すには以下の方法が役立った。

「Download logs」でローカルにテキストとしてダウンロードして、テキストエディタで`Error:`や`error`で検索する。ブラウザのログビューアでスクロールしながら探すよりも圧倒的に速い。

ログの末尾付近に実際のエラーが出ていることが多い。ビルドの最後の方で失敗するエラー（レンダリングエラーや設定エラー）はログの後半に書いてある。逆に、依存インストールで失敗する場合はログの前半を見る。

```
Installing dependencies...   ← ここでエラーが出れば依存問題
Building Astro site...       ← ここでエラーが出ればビルド設定問題
  → rendering pages...       ← ここでエラーが出ればページ内容の問題
```

この3段階を意識してログを読むと、どのフェーズで失敗しているかがすぐにわかる。

### 6. デプロイ完了後の確認

Deploymentsタブで「Success」になったら`*.pages.dev`のURLが発行される。ブラウザで開いてサイトが表示されれば成功。

カスタムドメインを設定したい場合は[XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)を参照。環境変数が必要な場合は[Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)も参考になる。

### 7. プレビューデプロイの活用

Cloudflare Pagesは`main`ブランチ以外のpushに対しても自動でプレビューURLを発行する。`feature/`ブランチでコードを書いてpushすると、本番とは別の`xxxxxxxx.プロジェクト名.pages.dev`という形のURLでプレビューが確認できる。

```bash
git checkout -b feature/add-new-section
# 変更を加えた後
git push origin feature/add-new-section
```

プレビューURLはDeploymentsタブの該当ビルドから確認できる。本番デプロイ前に見た目を確認できるので、大きな変更時に使うと安心だった。プレビュー環境では本番の環境変数は引き継がれないので注意。必要に応じてSettings → Environment variables で「Preview」環境向けの値を別途設定する。

### 8. 以降のpushの流れ

一度設定が完了すれば、あとは`git push`するだけで自動デプロイが走る。

```bash
# 記事を追加・編集した後
git add src/pages/posts/new-post.md
git commit -m "add new post"
git push
```

pushから1〜2分でDeploymentsタブに新しいビルドが来て、2〜3分でデプロイ完了する。ビルドが来ない場合は[Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)を確認する。

### 9. 直前のデプロイに戻したい場合

デプロイ後にサイトが壊れた場合、CloudflareのDeploymentsタブから以前のデプロイに戻せる。

1. Deploymentsタブを開く
2. 戻したいデプロイの右側「…」→「Rollback to this deployment」を選択
3. 確認ダイアログで「Rollback」をクリック

1〜2分で以前のビルドが本番に反映される。コードを修正してpushし直す時間が取れない緊急時に助かった。Rollbackはデプロイを「特定のビルドの状態に戻す」操作で、GitのコミットやブランチはそのままになるのでGit側の作業は不要だった。

### 10. Freeプランの制限を把握しておく

Cloudflare PagesのFreeプランは月500回のビルド・月500GBの帯域幅が上限になっている（2026年5月時点）。ブログサイトを個人で運営する分にはほとんど気にならない上限だが、毎日何度もpushするような開発フローでは消費が早まる。Deploymentsタブの「Build count」でその月の残りビルド回数を確認できる。

## ハマったポイント

- 「Create application」を押すとWorkers用の画面が出る。Pages用は**画面下部**の「Looking to deploy Pages? Get started here」という目立たないリンクから入る。ページの上部だけ見ていると絶対に見つからない。Vercelとは全く違うUI設計だった
- Framework presetで「Astro」を選ぶとビルド設定が自動入力されるだけでなく、推奨のNode.jsバージョンも適用される。手動で`npm run build`と`dist`を入れても一応動くが、Node.jsのバージョン差異でビルドが失敗しやすい。最初から「Astro」を選んでおけば避けられる失敗だった
- GitHubの認証ページで「Only select repositories」を選ぶと、後から新しいリポジトリを追加した時にCloudflareの一覧に出てこない。その場合はGitHubのSettings → Applications → Cloudflare Pages → Repositoriesから追加できる。「なぜ新しいリポジトリが出てこないのか」と20分悩んだことがあった
- ローカルで`npm run build`が通るのに、Cloudflare側で失敗するのはNode.jsのバージョン違いが多い。ローカルはNode.js 20でもCloudflareのデフォルトが16や18の可能性がある。Environment variablesで`NODE_VERSION=20`を指定すると一致させられた
- `devDependencies`に入れたパッケージはCloudflareの本番ビルドでインストールされない。ローカルでは`npm install`で全部入っているので気づかないが、Cloudflare側では`dependencies`のみが対象。Astroのintegrationなど実行時に必要なものは`dependencies`に入れる
- デプロイ後に`*.pages.dev`のURLが発行されるが、ブラウザでアクセスしたら「522 Connection timed out」が出ることがある。数分待ってからリロードすると直った。デプロイ直後はまだDNSが伝播中のことがある。5分待っても出ない場合はDeploymentsタブのビルドログを再確認する
- ローカルのdevモードでは正常に動いていても、Cloudflareのproductionビルドで初めて発覚するエラーがある。`@astrojs/sitemap`の`site`オプション未設定エラーがその一つで、devモードではスキップされてもビルド時に必須になる。全てのAstroプラグインのドキュメントにある「Required for production」の項目は最初から確認しておくべきだった
- `node_modules/`を`.gitignore`に追加する前に`git add .`してしまうと、リポジトリに何千ものファイルが含まれてしまう。Cloudflareのビルド自体は通るが、pushに何分もかかるようになる。`git rm -r --cached node_modules`で追跡から除外してから`.gitignore`に追加し直す必要があった
- ビルドログは「Download logs」でローカルに保存してからテキスト検索する方が、ブラウザのスクロールで探すより圧倒的に速かった。ログの量が多い時は特に有効で、`Error:`で検索するだけで原因が一発で見つかることが多かった

## 関連記事

- [XserverドメインをCloudflare Pagesのカスタムドメインに設定する全手順](/posts/xserver-cloudflare-full-setup)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)

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
