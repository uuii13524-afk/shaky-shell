---
title: 'Cloudflare Pagesで環境変数を設定する方法'
date: '2026-05-13'
category: 'Cloudflare'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Cloudflare', '環境変数', 'APIキー', '.env', 'Astro']
description: 'Cloudflare Pagesのダッシュボードで環境変数（APIキーなど）を設定する手順を解説。本番環境とプレビュー環境への設定方法も紹介します。'
---

## ひとことで言うと

```
Cloudflare → Workers & Pages → プロジェクト → Settings → Variables and Secrets
→ Add variable → Save → 空コミットpushで再デプロイ
```

```bash
# 変数設定後は再デプロイが必要
git commit --allow-empty -m "trigger redeploy for env vars"
git push
```

設定しただけでは既存デプロイには反映されない。再デプロイが必要な点を最初に知っておきたかった。

---

## やりたかったこと

AstroサイトでGoogle Maps APIキーを使う機能を追加しようとした。ローカルでは `.env` ファイルにキーを書けば動くのはわかっていたが、Cloudflare Pagesにデプロイすると当然 `.env` ファイルは存在しないので動かなかった。

```
Uncaught ReferenceError: import.meta.env.MAPS_API_KEY is not defined
```

「Cloudflare Pagesで環境変数を設定する画面がどこかにあるはず」とダッシュボードを探したが、設定画面の項目名がわからなくて見つけるのに20分かかった。「Environment variables」という名前だと思っていたが実際は「Variables and Secrets」という名前だった。

---

## 環境

- Windows 11
- Node.js 20.11.0
- npm 10.2.4
- Astro 5.2.3
- Cloudflare Pages（Freeプラン）

---

## 試したこと・うまくいかなかったこと

**`.env` ファイルをGitHubにコミットしようとした → APIキー漏洩リスク**

最初、`.env` ファイルをGitHubにコミットすることを考えた。プライベートリポジトリだったが、Gitの履歴には残るのでキーが漏洩するリスクがあると判断して中止した。一度コミットしたAPIキーは `.gitignore` に追加しても履歴から消えない。`git rm --cached .env` でトラッキングから除外しても、`git log -p` で履歴を見るとキーが丸見えになる。

**`astro.config.mjs` に直接書こうとした → ソースコードで公開状態**

次に `astro.config.mjs` に直接APIキーを書くことを考えた。このファイルはGitHubに入るので同じ問題になる。「ビルド時だけ参照するなら大丈夫では」と一瞬思ったが、ソースコードを見れる人間が全員APIキーを知れる状態になるのでやめた。

**Cloudflareダッシュボードの「Environment variables」が見つからなかった**

Cloudflareダッシュボードのプロジェクト設定を全部見てみたが「Environment variables」という名前の項目が見当たらなかった。実際の項目名は「Variables and Secrets」で、名前が違うせいで「この機能はないのかも」と思い込んで5分ほど無駄にした。「Variables」というキーワードでブラウザのCtrl+Fをしたらすぐ見つかった。

**設定しただけで再デプロイしなかった → undefinedのまま**

設定した後に再デプロイしないと変数が使われないことを知らなかった。「設定したのにコード上で `undefined` のまま」という状況になって10分以上悩んだ。「なぜ設定したのに反映されないのか」とCloudflareのドキュメントを調べ直してから、「環境変数を追加した後は新しいデプロイを走らせないと有効にならない」とわかってから解決した。

---

## 解決策

### Cloudflare Pagesで環境変数を設定する

1. Cloudflareダッシュボード → 「Workers & Pages」 → 対象プロジェクト
2. 上部の「Settings」タブをクリック
3. ページ内をスクロールして「Variables and Secrets」セクションを探す
4. 「Add variable」で変数名と値を入力して「Save」

```
Variable name: MAPS_API_KEY
Value: 実際のAPIキーの値（AIzaSy...のような文字列）
```

「Production」と「Preview」を別々に設定できる。本番用と開発確認用で別のAPIキーを使いたい場合は両方に設定しておく。「Production and Preview」を選ぶと両方に同じ値が入る。

追加したらすぐに「Save」ボタンを押す。Save前にページを離れると設定が消える。

### 環境変数を追加したら再デプロイする

変数を追加・変更しても既存のデプロイには反映されない。空コミットで強制的にデプロイをトリガーする。

```bash
git commit --allow-empty -m "trigger redeploy for env vars"
git push
```

Deploymentsタブに新しいビルドが来て成功すれば、新しい環境変数が使われた状態でデプロイされる。

### Astroのコードから参照する

```astro
---
// src/pages/index.astro または src/components/Map.astro
const apiKey = import.meta.env.MAPS_API_KEY;
---
```

Astroはviteベースなので `import.meta.env.変数名` で参照する。`process.env.変数名` はNode.jsのサーバーサイド専用で、Astroのコードでは動かない。

**クライアントサイドで使う変数は `PUBLIC_` プレフィックスが必要。**

```javascript
// ブラウザのscriptタグ内（クライアントサイド）で使う場合
const token = import.meta.env.PUBLIC_MAP_TOKEN;

// frontmatter（サーバーサイド）でだけ使う場合
const secretKey = import.meta.env.SECRET_KEY;
```

`PUBLIC_` のない変数はfrontmatterでしか使えない。クライアントサイドの `<script>` タグ内で `PUBLIC_` なしの変数を使うとビルド時に `undefined` になる。これはブラウザに秘密情報を送らないためのAstro（Vite）の仕様。

### ローカル開発環境の設定

`.env` ファイルをプロジェクトルートに作成する。

```
MAPS_API_KEY=ローカル開発用のテストキー
PUBLIC_MAP_TOKEN=パブリックに公開してもいいトークン
```

`.env` が `.gitignore` に含まれているか確認する。

```bash
cat .gitignore
```

`.env` がなければ追加してコミットする。

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "add .env to gitignore"
```

### シークレット（Secrets）と変数（Variables）の違い

Cloudflareの「Variables and Secrets」では2種類の保存方法が選べる。

| 種別 | 表示 | 用途 |
|------|------|------|
| Variable | ダッシュボードで値が見える | 機密でない設定値（NODE_VERSION など） |
| Secret | 値が伏せられる | APIキー・DBパスワードなど |

APIキーは「Encrypt」ボタンを押してSecretとして保存する方が安全。一度Secretとして保存すると値を確認できなくなるので、保存前にメモしておく。

---

## ハマったポイント

- 設定の項目名が「Environment variables」ではなく「Variables and Secrets」になっていて見つけるのに時間がかかった。「Variables」という単語でページをCtrl+F検索するとすぐ見つかる。Cloudflareのダッシュボードはたまに項目名が変わるので名前で探すより検索の方が確実だった
- 環境変数をCloudflareで設定しただけでは既存のデプロイには反映されない。設定後に空コミットをpushして再デプロイするまで新しい変数が使われない。「設定したのにundefinedのまま」という状況はほぼこれが原因だった。設定→再デプロイをセットで覚えておく
- クライアントサイドのscriptタグで `import.meta.env.MY_SECRET` を使ったらundefinedになった。ブラウザに公開する変数は `PUBLIC_` プレフィックスが必要で、それのない変数はサーバーサイド（frontmatter）でしか使えない仕様だった。ブラウザのDevToolsでコンソールを確認してわかった
- `process.env.変数名` ではなく `import.meta.env.変数名` で参照する。Node.jsのコードを流用して `process.env` と書いたら動かなかった。AstroはViteベースなのでViteの書き方が正しい。エラーは出ずに `undefined` になるだけなので発見に時間がかかった
- `.env` ファイルをGitにコミットしてしまった場合、`.gitignore` に追加しても履歴からは消えない。`git rm --cached .env` でトラッキングから除外してから `.gitignore` に追記してコミットし直す必要がある。コミットしてしまったAPIキーは即座に無効化して新しいキーを発行するのが正しい対処だった

---

## よくある質問

**Q: 環境変数は何個まで設定できますか？**
Cloudflare Pagesのフリープランでは環境変数に明示的な上限はないが、一般的には数十個以内で使う。各変数の値は最大5,000文字まで。

**Q: EnvironmentによってAPIキーを分けるべきですか？**
本番と開発で別のキーを使えるならその方が安全。本番のAPIキーをローカル開発中に誤って大量リクエストして制限に引っかかるリスクを防げる。Google Maps APIなどは無料枠があるので本番と別のキーを持っておくと事故が起きにくかった。

**Q: 環境変数を削除した場合、古いデプロイはどうなりますか？**
古いデプロイは変数が存在した時点のスナップショットではなく、現在の変数設定を参照している。削除すると次のデプロイから `undefined` になる。Rollbackした場合も同様で、古いコードが現在の変数設定を使う。

**Q: Astroの `import.meta.env.MODE` の値はCloudflareではどうなりますか？**
Cloudflareのビルドは常に `production` モードで実行されるので `import.meta.env.MODE` は `'production'` になる。`import.meta.env.DEV` は `false`、`import.meta.env.PROD` は `true` になる。

---

`.env` ファイルをGitにコミットしてしまわないよう、[Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)で `.env` を除外しておくと安全だ。

## 関連記事

- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
