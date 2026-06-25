---
title: 'Cloudflare PagesがGitHubと切断された時の対処法（エラーメッセージ別）'
date: '2026-05-01'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
description: 'Cloudflare PagesとGitHubの連携が切断された6種類のエラーメッセージと、それぞれの解決手順を解説。pushが反映されない場合の確認ポイントも紹介。'
---

## ひとことで言うと

**Cloudflareダッシュボード → Pages → プロジェクト → Settings → Git repository → Manage** を開き、GitHubインテグレーションを再インストールする。ほとんどのケースはこれで2分以内に解決する。

---

## やりたかったこと

2ヶ月ぶりにAstroサイトを更新しようと記事を1本書いてgit pushした。GitHubのリポジトリにはちゃんとコミットが積まれているのに、5分待っても10分待っても Cloudflare PagesのDeploymentsタブに何も来なかった。

おかしいと思ってプロジェクトのトップを開いたら、薄いオレンジのバナーが出ていた。

Cloudflare Pagesが表示するバナーには以下の6種類がある：

- `This project is disconnected from your Git account, this may cause deployments to fail.`
- `Cloudflare Pages is not properly installed on your Git account, this may cause deployments to fail.`
- `The Cloudflare Pages installation has been suspended, this may cause deployments to fail.`
- `The project is linked to a repository that no longer exists, this may cause deployments to fail.`
- `The repository cannot be accessed, this may cause deployments to fail.`
- `There is an internal issue with your Cloudflare Pages Git installation.`

今回出ていたのは最初のメッセージだった：

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

「May cause」という書き方だったので最初は軽く見ていた。だけど実際にはこのバナーが出ている状態ではpushを検知すらしていなくて、バナーを出してから30分以上放置してしまった。

Deploymentsタブを開いて確認したら、最後のデプロイは2ヶ月前のままで、その後のコミットは全部ゼロ。失敗しているわけでもなく、ビルド自体が来ていない状態だった。つまり2ヶ月分の記事追加が全部公開されていなかったことになる。push後にDeploymentsタブを確認する習慣がなかった自分のミスだったが、それにしてもバナーの色が薄くて気づきにくかった。

根本原因はGitHubのOAuthトークンの失効だった。後から調べたら、GitHubの2段階認証設定を変更した時にOAuthアプリの認可がリセットされるケースがあると知った。自分がGitHubのセキュリティ設定を触った日とデプロイが止まった日が一致していた。

GitHubのリポジトリSettings → Webhooksを開いてdeliveryを確認したら、最後のdeliveryのレスポンスが `401 Unauthorized` だった。これでOAuth切れが確定した。

```
HTTP/2 401
{"result":null,"success":false,"errors":[{"code":10000,"message":"Authentication error"}],"messages":[]}
```

Cloudflareにはビルド失敗の記録すら残らないので、再接続するまで完全に止まっていることに気づけない。2ヶ月間も誰かがサイトを見ていたのに気づかなかったのはこれが理由だった。

## 環境

- Cloudflare Pages（2026年5月時点）
- GitHub
- Astro 5.2.3
- Node.js 20.11.0
- Windows 11

## 試したこと・うまくいかなかったこと

**ブラウザのキャッシュ疑い → 関係なかった**

最初はCloudflareダッシュボードをCtrl+Shift+Rでハードリロードしてみた。バナーは消えなかった。次に「Retry deployment」ボタンを探したが、そもそもDeploymentsタブに新しいビルドが来ていないのでRetryする対象自体がなかった。最後のビルドエントリの「…」メニューを開いたら「Retry deployment」はグレーアウトして押せない状態だった。「ビルドが失敗しているなら再試行できるはず」と思い込んでいたが、ビルドが来ていない状態ではRetryの概念自体が成立しないことを理解した。

**git push再実行 → 全く反応なし**

「もう一度pushすれば直るかも」と思って`git push`、さらに`git push --force`まで試したが、GitHubのリポジトリには正しくコミットが積まれているのにCloudflareは無反応のままだった。GitHubとCloudflareの間の接続が切れているのだから、どんな形でpushしてもCloudflareには届かない。

**Cloudflareのサービス障害を疑った → Operational だった**

`cloudflarestatus.com`を開いてシステム障害を確認した。すべてOperationalで、自分のアカウントだけの問題だとわかった。

GitHubのWebhookのdeliveryログを確認したら、最新エントリのレスポンスが `401 Unauthorized` になっていた。これでOAuthトークンの有効期限が切れているのが確定した。GitHubのSettings → Applications → Authorized OAuth Appsを見たら、Cloudflare Pagesのエントリが「Revoked」になっていた。

その後、GitHubのSettings → Applications の「Installed GitHub Apps」タブを確認して「Cloudflareのエントリがある、大丈夫だ」と思ってしまった。実はここはGitHub Apps用のリストで、Cloudflare PagesはOAuth Apps（「Authorized OAuth Apps」タブの方）を使う。この2つのリストを混同して原因の切り分けに30分以上かかった。

## 解決策

CloudflareとGitHubのOAuth接続が切れているのが原因。GitHubのOAuthトークンはGitHubのセキュリティ設定変更（2FA変更・パスワード変更など）後に失効することがある。

### 1. GitHubを再認証する

Cloudflareダッシュボードで該当プロジェクトを開き、「Settings」タブ（上部のタブ、左サイドバーではない）→「Git repository」セクションの「Manage」をクリックする。GitHubのOAuth認証画面が開くので「Authorize Cloudflare Pages」で認証する。

認証後、GitHubのWebhooks画面の「Ping」ボタンを押してその場で疎通確認できる。Pingのレスポンスが200なら再認証成功、401ならまだ切れている。

### 2. 空のコミットで強制デプロイ

再認証しただけでは過去のコミットが遡ってデプロイされない。認証が切れていた間のコミットはCloudflareが受け取っていないので、空コミットをpushして強制的にトリガーする。

```bash
git commit --allow-empty -m "force deploy"
git push
```

pushから1〜2分でDeploymentsタブに新しいビルドが来て、2ヶ月分の記事が最新コミットの状態でまとめて反映された。

### 3. GitHubのWebhookをリデリバリする（補足）

GitHubのSettings → Webhooks → 対象のWebhook → 「Recent Deliveries」タブから、失敗しているdeliveryを「Redeliver」で再送できる。ただし**再認証してから**実行しないと401で再び失敗する。失敗件数が多い時は空コミットpushの方が早い。

### 4. 再認証できない場合の対処

「Manage」を押しても認証画面が開かない場合は、Cloudflareのプロジェクト設定から「Disconnect Git repository」で完全に切断し、「Connect to Git」から接続し直す。ブランチ設定などが初期化されるので、接続後に再設定が必要。

Organizationのリポジトリを使っている場合、Organization側のThird-party Access設定でCloudflare Pagesが「Approved」になっているか別途確認が必要。Organizationオーナーでない場合はオーナーに承認を依頼する。

### 5. 再発防止のポイント

GitHubのセキュリティ設定を変えた後は、Cloudflare PagesのDeploymentsタブで次のpushが正常にビルドされるか確認する習慣をつける。月に1回は「最新のデプロイがいつか」を確認するだけでも、今回のような2ヶ月放置は防げる。

Cloudflareには「Workers & Pages」→プロジェクト→「Settings」→「Notifications」でビルド失敗のメール通知を設定できる。「接続切断」の検知には使えないが、ビルド失敗の早期発見に役立つ。

### 6. 再接続後のチェックリスト

1. Deploymentsタブにビルドが来ているか（空コミットpushから1〜2分後）
2. ビルドが「Success」になっているか
3. 本番サイトが最新の内容になっているか（シークレットモードで確認）
4. GitHubのWebhook deliveryが200を返しているか
5. GitHubのAuthorized OAuth AppsにCloudflareが「Revoked」でなく表示されているか

## エラーメッセージ別の対処法

### "The Cloudflare Pages installation has been suspended"

GitHubの設定でCloudflare PagesアプリがSuspendされている。

1. GitHubのインストール設定を開く
   - 個人アカウント: `https://github.com/settings/installations`
   - Organization: `https://github.com/organizations/組織名/settings/installations`
2. Cloudflare Pagesの「Configure」をクリック
3. ページ下部の「Unsuspend」をクリック

### "The repository cannot be accessed"

GitHub Appのリポジトリアクセスからこのリポジトリがはずれている。

1. 上記のインストール設定を開く
2. 「Repository access」で対象リポジトリを追加、または「All repositories」に変更

### "The project is linked to a repository that no longer exists"

リポジトリが削除または別アカウントに移管された。

- 削除された場合: 新しいリポジトリで新規Pagesプロジェクトを作成
- 移管された場合: 元のアカウントに戻すか、新しい場所のリポジトリで新規プロジェクトを作成

### "There is an internal issue with your Cloudflare Pages Git installation"

Cloudflare内部のエラー。GitHubアプリの再インストールで解消しないなら[Cloudflareサポート](https://support.cloudflare.com/)に問い合わせる。

---

## ハマったポイント

- バナーが薄いオレンジ色で「May cause deployments to fail」という曖昧な表現だったので最初は軽く見ていた。実際にはその時点でデプロイは完全に止まっていた。バナーの色が薄いから「とりあえず動いているのかも」という思い込みが30分以上の放置につながった
- GitHubのSettings → Applicationsには「Installed GitHub Apps」と「Authorized OAuth Apps」の2つのタブがある。「Installed GitHub Apps」にCloudflareのエントリがあるから大丈夫と思ったが、Cloudflare PagesはOAuth Apps側を使う。全然別のリストだとわかるまで20分以上かかった
- 再認証しただけで「あとは待てばいい」と思っていたが、認証が切れていた間のコミットはCloudflareが受け取っていないので遡って処理してくれない。空コミットの`git push`が別途必要だと気づくまで20分待ち続けた
- 「ビルドが来ない」のと「ビルドが来るが失敗する」は全く別の問題。Deploymentsタブを最初に確認して「Failedが来ているか、それとも何も来ていないか」を確認するだけで診断の入口が決まる。何も来ていない場合はOAuth切断かブランチ設定の問題を疑う
- GitHubのWebhook画面の「Ping」ボタンで、その場で接続が復旧しているか確認できる。再認証後にPingを送って200が返れば完了、401なら再認証が不完全。Deliveryの一覧を眺めるより、このPingで確認する方が30秒で終わる

デプロイが反映されない時はまずDeploymentsタブのログを確認する。ビルドログの見方については[Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)が参考になる。

## よくある質問

**Q: なぜCloudflare PagesがGitHubと切断されるのか？**
最も多い原因はOAuthトークンの有効期限切れ。GitHubの2FA設定変更やパスワード変更後に失効することがある。

**Q: Cloudflare PagesをGitHubに再接続する方法は？**
Cloudflareダッシュボード → プロジェクト → Settings → Git repository → Manage → Uninstall → Install で再認証する。

**Q: 再接続後もgit pushがデプロイをトリガーしない。**
空コミットで強制トリガーする: `git commit --allow-empty -m "reconnect" && git push`。それでもダメならSettings内のプロダクションブランチ名が一致しているか確認する。

**Q: GitLabでも同じ手順で直る？**
はい。再接続手順は同じ。GitLabのインストール設定は `https://gitlab.com/-/profile/applications` で確認できる。

---

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
