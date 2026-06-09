---
title: 'Cloudflare PagesがGitHubと切断された時の対処法'
date: '2026-05-01'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare PagesとGitHubの連携が切断された時の症状と再接続する手順を解説。pushが反映されない場合の確認ポイントも紹介します。'
---

## やりたかったこと

2ヶ月ほど手をつけていなかったAstroサイトを久しぶりに更新しようと思って、記事を1本追加してgit pushした。GitHubのリポジトリにはちゃんとコミットが積まれているのを確認したのに、5分待っても10分待っても何も起きない。いつもなら1〜2分でCloudflare PagesのDeploymentsタブに新しいビルドが来るはずなのに、画面は昨日のままだった。

おかしいと思ってCloudflareのダッシュボードを開いたら、プロジェクトのトップに薄いオレンジのバナーが表示されていた。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

「May cause」という表現だったので最初は軽く見ていたが、実際にはこのメッセージが出ている状態ではpushを検知すらしていなかった。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub
- Astro 5.2.3
- Node.js 20.11.0
- Windows 11

## 試したこと・うまくいかなかったこと

最初はブラウザのキャッシュかと思ってCloudflareダッシュボードをハードリロード（Ctrl+Shift+R）してみた。バナーのメッセージは消えなかった。

次に「Retry deployment」ボタンを探したが、そもそも新しいデプロイがDeploymentsタブに来ていないので押せるものがなかった。「ビルドエラーかな」とDeploymentsの一番上を確認したら、最後のデプロイは2ヶ月前のもので、その後は完全に止まっていた。Failedのビルドがあるわけでもなく、ビルドが始まっていないという状態だった。

「もう一度pushすれば直るかも」と思って`git push`を再実行したが、GitHubのリポジトリには正しくコミットが積まれているのにCloudflareは全く反応しなかった。

「Cloudflare側のシステム障害かも」とCloudflare Status（`cloudflarestatus.com`）を確認したが、すべてOperationalだった。

次にGitHubのリポジトリ設定でWebhooksを確認した。Settings → Webhooks に行くと、Cloudflare Pagesが登録しているWebhookが一覧に出てくる。最近のdeliveryを見たら、最後のdeliveryが2ヶ月前で、それ以降は「pushはされているがWebhookが届いていない」か「Webhookが削除されている」かのどちらかだとわかった。Webhookの一覧を確認するとCloudflare Pagesのエントリが残っていたが、最後のdeliveryステータスが失敗になっていた。

GitHubのSettings → Applications → Authorized OAuth Apps でCloudflareのエントリを確認したら、アクセスの状態が変わっていた。

## 解決策

CloudflareとGitHubのOAuth接続が切れていたのが原因だった。GitHubのOAuthトークンには有効期限があり、長期間放置したプロジェクトや、GitHubのセキュリティ設定を変更した後は自動的に切断される。

### 1. GitHubを再認証する

Cloudflareダッシュボードで該当プロジェクトを開き、「Settings」タブ（上部のタブ、左サイドバーではない）に移動する。ページ内の「Git repository」セクションまでスクロールすると「Manage」ボタンがある。

「Manage」をクリックするとGitHubのOAuth認証画面が開く。GitHubにログインしたまま開くと「Authorize Cloudflare Pages」の画面が表示されるので「Authorize」を押す。

認証が完了するとCloudflareのダッシュボードに戻る。このタイミングでバナーメッセージが消えていれば再接続成功。

### 2. 空のコミットで強制デプロイ

再認証しただけでは直近のコミットがデプロイされない。認証が切れていた間にpushしたコミットはCloudflareが受け取っていないので、空のコミットをpushして強制的にデプロイをトリガーする必要がある。

```bash
git commit --allow-empty -m "force deploy"
git push
```

これでDeploymentsタブに新しいビルドが来て、1〜2分でデプロイが完了した。

### 3. 再認証できない場合の対処

「Manage」を押しても認証画面が開かない、または認証後にまた同じバナーが出る場合は、プロジェクトのGitHubとの接続を一度完全に切断して再設定する方法がある。

Cloudflare PagesのSettings → Git repositoryで「Disconnect Git repository」を探す。切断後に「Connect to Git」から改めてGitHubのリポジトリを選択して接続し直す。この方法は接続設定が完全にリセットされるので確実に直る。ただし本番ブランチの設定なども再設定が必要になる。

## ハマったポイント

- 「Retry deployment」で再試行しようとしたが、そもそも新しいデプロイが来ていないので押すものがなかった。Deploymentsタブに何も来ていない状態こそが切断のサインだった
- 切断のバナーはプロジェクトのトップページに薄い色で表示されている。DeploymentsタブやSettingsを直接開いていると見落とす。プロジェクトのOverview画面を最初に確認する習慣が大切だった
- GitHubのリポジトリ自体には問題なくpushできていたので、「Gitの問題」ではなく「CloudflareとGitHubの間の接続の問題」だと理解するまでに時間がかかった
- 再認証後に「もうpushしてあるから大丈夫」と思って待っていたら何も起きなかった。再認証はあくまで接続の修復で、過去のコミットをCloudflareが遡って処理してくれるわけではなかった。空のコミットを追加でpushするのが必要だった
- GitHubのSettings → Applications → Authorized OAuth Appsでもアクセス状況を確認できる。ここでCloudflareのエントリが「Revoked」になっていたら再認証が必要なサインだった
- 長期間放置したプロジェクトで起きやすい。月に1回以上触っているプロジェクトではほとんど起きないが、数ヶ月単位で放置するとOAuthトークンが期限切れになることがある

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
