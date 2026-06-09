---
title: 'Cloudflare PagesがGitHubと切断された時の対処法'
date: '2026-05-01'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare PagesとGitHubの連携が切断された時の症状と再接続する手順を解説。pushが反映されない場合の確認ポイントも紹介します。'
---

## やりたかったこと

Astroサイトのコードを修正してgit pushしたのに、Cloudflare Pagesに変更が反映されなかった。いつもなら1〜2分でデプロイが走るのに、5分待っても10分待っても何も起きない。ダッシュボードを開いたら以下のメッセージが出ていた。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub
- Astro 5.2.3
- Node.js 20.11.0
- Windows 11

## 試したこと・うまくいかなかったこと

最初はブラウザのキャッシュかと思ってCloudflareダッシュボードをリロードしてみたが、メッセージは消えなかった。

次に「Retry deployment」ボタンを探したが、そもそも新しいデプロイがDeploymentsタブに来ていないので押せるものがなかった。「ビルドエラーかな」とDeploymentsの一番上を確認したら、最後のデプロイは1時間前のもので、その後は完全に止まっていた。

もう一度pushすれば直るかと思って`git push`を再実行したが、やはり何も起きなかった。GitHubのリポジトリ側には正しくコミットが積まれているのに、Cloudflareがそれを検知していない状態だった。

## 解決策

CloudflareとGitHubのOAuth接続が切れていたのが原因だった。GitHubのトークンが期限切れになったり、アクセス許可が変わったりすると自動的に切断される。

### 1. GitHubを再認証する

Cloudflareダッシュボードで該当プロジェクトを開き、「Settings」タブに移動する。「Git repository」のセクションに「Manage」ボタンがあるのでクリックする。GitHubのOAuth認証画面が開くので、ログインして権限を再付与する。

### 2. 空のコミットで強制デプロイ

再認証しただけでは最新コミットがデプロイされないことがある。空のコミットをpushして強制的にデプロイをトリガーする。

```bash
git commit --allow-empty -m "force deploy"
git push
```

これでDeploymentsタブに新しいビルドが来て、1〜2分でデプロイが完了した。

## ハマったポイント

- 「Retry deployment」で再試行しようとしたが、そもそも新しいデプロイが来ていないので押すものがないと気づくまで時間がかかった
- 切断のメッセージはページ上部にうっすら出ているだけで、最初は見落としていた。Deploymentsタブが空欄なのに気づいてから遡って発見した
- GitHubのリポジトリ自体には問題なくpushできていたので、Cloudflare側の問題だと最初わからなかった。GitHubとCloudflareは別の接続を使っていると理解するまで1時間くらい溶かした
- 再認証後に「もうpushしてあるから大丈夫」と油断したら、古いコミットのままだった。空のコミットで改めてトリガーが必要だった
- OAuth接続の期限は明示されていない。長期間放置したプロジェクトや、GitHubのセキュリティ設定を変更した後に起きやすい

デプロイが反映されない時はまずDeploymentsタブのログを確認する。ビルドログの読み方については[Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)が参考になる。

## 関連記事

- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
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
