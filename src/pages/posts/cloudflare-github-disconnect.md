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

「May cause」という表現だったので最初は軽く見ていたが、実際にはこのメッセージが出ている状態ではpushを検知すらしていなかった。バナーの色が薄いオレンジで、エラーの赤ではないのが余計に「とりあえず動いているのかも」と思わせる作りになっていて、30分以上見逃していた。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub
- Astro 5.2.3
- Node.js 20.11.0
- Windows 11

## 試したこと・うまくいかなかったこと

最初はブラウザのキャッシュかと思ってCloudflareダッシュボードをハードリロード（Ctrl+Shift+R）してみた。バナーのメッセージは消えなかった。「表示の問題ではなく本当に切断されている」と認識したのはここで初めてだった。

次に「Retry deployment」ボタンを探したが、そもそも新しいデプロイがDeploymentsタブに来ていないので押せるものがなかった。「ビルドエラーかな」とDeploymentsの一番上を確認したら、最後のデプロイは2ヶ月前のもので、その後は完全に止まっていた。Failedのビルドがあるわけでもなく、ビルドが始まっていないという状態だった。「ビルドが失敗しているのか」と「ビルド自体が来ていないのか」は全然違う問題なので、最初にDeploymentsタブで状態確認するのが正しい診断順序だった。

「もう一度pushすれば直るかも」と思って`git push`を再実行したが、GitHubのリポジトリには正しくコミットが積まれているのにCloudflareは全く反応しなかった。さらに`git push --force`も試したが同様。GitHubとCloudflareの間の接続が切れているのだから、どんな形でpushしても届かない。

「Cloudflare側のシステム障害かも」とCloudflare Status（`cloudflarestatus.com`）を確認したが、すべてOperationalだった。自分のアカウントだけの問題だとわかった。

次にGitHubのリポジトリ設定でWebhooksを確認した。Settings → Webhooks に行くと、Cloudflare Pagesが登録しているWebhookが一覧に出てくる。最近のdeliveryを見たら、最後のdeliveryが2ヶ月前で、それ以降のdeliveryが1件もなかった。最新のdeliveryのステータスを展開すると、レスポンスが `401 Unauthorized` になっていた。

```
HTTP/2 401
{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]}
```

GitHubはpushをCloudflareに通知しようとしているが、Cloudflareが「知らないアカウントだ」と401で弾いている状態だった。原因はOAuthトークンの有効期限切れだとここで確信できた。

さらに原因の日時を特定するためにCloudflareの「Audit Log」も確認した。Cloudflareダッシュボード左上のアカウントアイコン → 「Audit Log」で確認できる。2ヶ月前のある日を境にCloudflare PagesのGitHub関連のアクティビティが全て止まっていた。その日付を調べたら、GitHubの2段階認証の設定を変更していた日と一致していた。

GitHubのSettings → Applications → Authorized OAuth Apps でCloudflareのエントリを確認したら、アクセスの状態が「Revoked」になっていた。GitHubのセキュリティ設定で2段階認証を変更した後、OAuthアプリの権限がリセットされていたのが根本原因だった。

## 解決策

CloudflareとGitHubのOAuth接続が切れていたのが原因だった。GitHubのOAuthトークンには有効期限があり、長期間放置したプロジェクトや、GitHubのセキュリティ設定を変更した後は自動的に切断される。

### 1. GitHubを再認証する

Cloudflareダッシュボードで該当プロジェクトを開き、「Settings」タブ（上部のタブ、左サイドバーではない）に移動する。ページ内の「Git repository」セクションまでスクロールすると「Manage」ボタンがある。プロジェクトのOverview画面やDeploymentsタブではなく、「Settings」タブの中段〜下段あたりにある。

「Manage」をクリックするとGitHubのOAuth認証画面が開く。GitHubにログインしたまま開くと「Authorize Cloudflare Pages」の画面が表示されるので「Authorize」を押す。

認証が完了するとCloudflareのダッシュボードに戻る。このタイミングでバナーメッセージが消えていれば再接続成功。Authorizeを押した直後にバナーが消えて「接続できた」と確認できた。

GitHubのSettings → Applications → Authorized OAuth Appsに戻ってCloudflareのエントリを確認すると、今度は「Revoked」ではなく正常なアクセス権限が表示されるようになっているはず。

再認証後、GitHubのWebhooksページにある「Recent Deliveries」タブから失敗したdeliveryを選び「Redeliver」ボタンを押す方法もある。これでそのコミットのWebhookをCloudflareに再送できる。ただし複数回失敗しているdeliveryがある場合は後述の空コミットpushのほうが確実。

### 2. 空のコミットで強制デプロイ

再認証しただけでは直近のコミットがデプロイされない。認証が切れていた間にpushしたコミットはCloudflareが受け取っていないので、空のコミットをpushして強制的にデプロイをトリガーする必要がある。

```bash
git commit --allow-empty -m "force deploy"
git push
```

これでDeploymentsタブに新しいビルドが来て、1〜2分でデプロイが完了した。2ヶ月分の記事の更新がまとめて最新コミットの内容として反映された。

### 3. 再認証できない場合の対処

「Manage」を押しても認証画面が開かない、または認証後にまた同じバナーが出る場合は、プロジェクトのGitHubとの接続を一度完全に切断して再設定する方法がある。

Cloudflare PagesのSettings → Git repositoryで「Disconnect Git repository」を探す。切断後に「Connect to Git」から改めてGitHubのリポジトリを選択して接続し直す。この方法は接続設定が完全にリセットされるので確実に直る。ただし本番ブランチの設定やPreview branchの設定なども再設定が必要になる。

切断後の再接続時、GitHubのリポジトリ一覧にプロジェクトが表示されない場合は、GitHubのSettings → Applications → Cloudflare Pages → Repositoriesから対象リポジトリへのアクセスを許可する。

GitHubのOrganizationリポジトリを使っている場合は、OrganizationのSettings → Third-party Access → OAuth AppsでCloudflare Pagesへのアクセスが承認されているかも確認する。個人リポジトリと違い、Organizationオーナーの承認が別途必要なケースがある。

### 4. 再発防止

GitHubのセキュリティ設定（2段階認証・SSHキー・パスワード変更など）を変えた後は、Cloudflare PagesのDeploymentsタブを必ず確認する癖をつけると早期発見できる。設定変更後に一度テストコミットをpushして、1〜2分以内にビルドが来るかどうか確認するだけでいい。

長期間更新しないプロジェクトが複数ある場合は、月に1回程度Deploymentsタブを眺めておくと切断に早く気づける。2ヶ月以上放置して初めてデプロイが止まっていると気づくのは時間を大きくロスする。

## ハマったポイント

- 「Retry deployment」で再試行しようとしたが、そもそも新しいデプロイが来ていないので押すものがなかった。Deploymentsタブに何も来ていない状態こそが切断のサインだった。「ビルドが失敗している」状態とは全く違う
- 切断のバナーはプロジェクトのトップページに薄いオレンジ色で表示されている。DeploymentsタブやSettingsを直接開いていると見落とす。プロジェクトのOverview画面を最初に確認する習慣が大切だった
- GitHubのリポジトリ自体には問題なくpushできていたので、「Gitの問題」ではなく「CloudflareとGitHubの間の接続の問題」だと理解するまでに時間がかかった。コミット履歴はちゃんと積まれているのにデプロイが動かない場合は、接続の問題を最初に疑う
- 再認証後に「もうpushしてあるから大丈夫」と思って待っていたら何も起きなかった。再認証はあくまで接続の修復で、過去のコミットをCloudflareが遡って処理してくれるわけではなかった。`git commit --allow-empty -m "force deploy" && git push` の空コミットを追加でpushするのが必要だった
- GitHubのWebhookのdeliveryログを確認したら、HTTPレスポンスが `401 Unauthorized` になっていた。CloudflareがGitHubのWebhookを弾いている状態で、これが「OAuthが切れている」の具体的な証拠だった。診断に迷ったらGitHub側のWebhookログを確認すると原因がはっきりする
- GitHubのSettings → Applications → Authorized OAuth Appsでもアクセス状況を確認できる。ここでCloudflareのエントリが「Revoked」になっていたら再認証が必要なサインだった
- CloudflareのAudit Logに切断が発生した日時の記録があった。自分の場合はGitHubの2段階認証を変更した日と一致していて、原因の特定に役立った。「いつから動かなくなったか」がわからない時にAudit Logを確認すると手がかりになる
- 長期間放置したプロジェクトで起きやすい。月に1回以上触っているプロジェクトではほとんど起きないが、数ヶ月単位で放置するとOAuthトークンが期限切れになることがある。GitHubのセキュリティ設定変更後にも起きる

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
