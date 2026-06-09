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

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub（private/publicどちらでも発生）
- Astro 5.2.3
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

まず「何か変なコードを入れたか？」と思ってgit diffで確認したが、問題になりそうなコードはなかった。ローカルで`npm run build`したら正常に通った。

次にCloudflareのDeploymentsタブを全部見直したが、「Failed」のビルドがあるわけではなく、そもそも新しいビルドが来ていなかった。ビルドエラーなら原因を探せるが、ビルドが始まっていないという状態でどこを見ればいいか最初わからなかった。

「もう一度pushすれば直るかも」と空のコミット無しで`git push --force`まで試したが何も起きなかった。GitHubのリポジトリにはちゃんとコミットが積まれているのに、Cloudflareがそれを検知していないのだった。

## 解決策

原因は3パターンある。上から順に確認していくのが早い。

### 原因1：CloudflareとGitHubの接続が切れている

これが一番多い。Cloudflareダッシュボードでプロジェクトを開き、「Settings」→「Git repository」の「Manage」をクリックする。GitHubの再認証画面が開くのでログインしてアクセスを許可する。

再認証後は空のコミットをpushして強制的にデプロイをトリガーする。

```bash
git commit --allow-empty -m "force deploy"
git push
```

これでDeploymentsタブにビルドが来て解決した。

### 原因2：古いコミットが対象になっている

Cloudflare Pagesは`main`ブランチのpushを監視している。別ブランチで作業してmainに向けていない場合はデプロイが走らない。

```bash
git branch  # 現在のブランチを確認
git checkout main
git merge 作業ブランチ名
git push origin main
```

### 原因3：ビルドエラーが出ている

Deploymentsタブにビルド自体は来ているが「Failed」になっている場合は、ビルドエラーが原因。

Deploymentsタブ→該当ビルド→「View build logs」でエラー内容を確認する。よくあるエラーと対処法：

```
Error: Cannot find module '@astrojs/...'
```
→ `package.json`に依存が含まれているか確認。Cloudflare側でも`npm install`が走るが、devDependenciesに入っていると本番環境でインストールされないことがある。

```
Error: Build failed with exit code 1
```
→ ビルドコマンドやNode.jsのバージョンを確認。「Settings」→「Build configuration」で`NODE_VERSION`環境変数を明示的に指定する。

## ハマったポイント

- 空のコミットのpushが最も確実な強制デプロイ方法。`--allow-empty`オプションを知らなくて最初は意味のない1文字を追加してはコミットという無駄な操作をしていた
- ビルドが「来ていない」のか「来ているが失敗している」のかで原因が全然違う。Deploymentsタブを最初に見ることが時間節約になる
- 「Settings」の「Git repository」セクションに切断を示すバナーが出ているが、画面上部のプロジェクト概要画面を見ていると気づかないことがある。Settingsタブを開いて確認する習慣をつけた
- 再認証だけでは足りなくて、空のコミットpushが別途必要だったことに最初気づかなかった。再認証後に「もうGitHubにpush済みだから大丈夫」と思い込んでいたが、Cloudflareは認証復旧後に遡ってビルドを走らせてくれるわけではない
- GitHubのOAuth許可設定を確認したらCloudflareへのアクセスが「Revoked」になっていた。GitHub側のSettings→Applications→Authorized OAuth Appsでも確認できる

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
