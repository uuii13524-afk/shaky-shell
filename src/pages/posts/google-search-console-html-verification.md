---
title: 'Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順'
date: '2026-05-04'
category: 'SEO'
layout: '../../layouts/PostLayout.astro'
description: 'Google Search ConsoleにAstro+Cloudflare Pagesのサイトを登録するHTMLファイル認証の手順を解説。ファイルの設置方法から確認まで紹介します。'
---

## やりたかったこと

Astro + Cloudflare Pagesで公開したブログをGoogle Search Consoleに登録しようとした。プロパティの追加画面でドメイン認証とHTMLファイル認証の2種類が出てきて、最初は**ドメイン認証（DNS TXTレコード方式）**を試した。

ドメイン認証はwwwあり・なし・httpとhttpsをまとめて一つのプロパティで管理できると書いてあって、「これで全部まとめられる」と思って先に試した。CloudflareのDNS設定でTXTレコードを追加してSearch Consoleの「確認」ボタンを押したのだが、「所有権を確認できませんでした」が何度押しても出続けた。

後から気づいたのだが、CloudflareはデフォルトでTXTレコードにもプロキシ設定の影響が及ぶ場合があって、Googleが期待するDNS TXTレコードの値が正しく解決されないことがあった。特に自分はCloudflareのProxy設定をいくつかのレコードに対して広く有効にしていたため、TXTレコードの確認がCloudflareのプロキシを通過してしまっていたのが原因だった。「TXTレコードを追加したのに認証が通らない」という状態が1時間続いて、結局DNSの方法を諦めてHTMLファイル認証に切り替えた。

HTMLファイル認証はDNS操作が不要でファイルを1個置くだけなので手順が明確だった。認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をダウンロードしてAstroのプロジェクトに置こうとしたが、どこに置けば本番URLでアクセスできるのかわからなかった。`src/`の中に置いたら404になった。「なぜページが404になるのか」「Astroはどのフォルダをそのままコピーするのか」を理解するまでに2回デプロイを無駄にした。

Astroのファイル配置のルールを理解していなかったのが根本の原因で、`src/pages/`に置けばどんなファイルもURLでアクセスできると思い込んでいた。実際にはAstroが処理できるファイル形式（`.astro`・`.md`・`.mdx`）以外は`public/`に置く必要があった。`.html`ファイルはAstroが「ページとして変換する対象」として扱うので、`src/pages/`に置くとAstroのレイアウトで囲まれてしまう。

Search Consoleに登録することそのものは5分で終わる作業のはずが、ファイルの設置場所を間違えたせいで3回デプロイし直すことになった。「public/に置けばよかった」とわかったのは2回失敗した後で、最初からこれを知っていれば15分で完了できた。

認証が完了した後も落とし穴があった。認証ファイルを「もう不要」と思って削除したら、1ヶ月後に「所有権を確認できなくなりました」というメールが届いた。Googleは認証後も定期的に認証ファイルにアクセスして所有権を継続確認しているので、一度認証が通っても削除してはいけない。この事実を知らずに削除してしまった経験が、自分の中で一番痛かった失敗だった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Google Search Console（2026年5月時点）
- Windows 11
- Node.js 20.11.0

## 試したこと・うまくいかなかったこと

最初、認証ファイル（`googleXXXXXXXXXXXXXXXX.html`）をAstroの`src/pages/`に置いてみた。ローカルで`npm run dev`して`http://localhost:4321/googleXXXXXXXXXXXXXXXX.html`にアクセスしたら「404 Page not found」が返ってきた。Astroのページは`.astro`拡張子じゃないといけないのかと思って、`.html`ファイルをそのまま置けるのかどうか調べ始めた。

実は`src/pages/`に`.html`ファイルを置いてもビルドには含まれる。ただし**Astroがそのファイルを自分のレイアウトやコンポーネントで処理してしまう**ので、Google が期待するファイルの内容と変わってしまう。Search Consoleの認証ファイルには`google-site-verification`のmetaタグが含まれているが、Astroのレイアウトで囲まれると認証コードの判定が狂う。`<head>`タグや`<body>`タグが二重になったり、レイアウトのナビゲーションが挿入されたりする。

「とりあえずデプロイしてから確認してみよう」と`src/pages/`に置いたままCloudflare Pagesにpushした。デプロイ完了後にSearch Consoleの「確認」ボタンを押したら「所有権を確認できませんでした」と出た。ブラウザで認証ファイルのURLにアクセスしたら、完全なHTMLページになっていて（Astroのレイアウトが適用された状態）、ファイルの内容が変わっていたのが原因だった。

Google側が期待するレスポンスは1行のシンプルなテキスト。

```
google-site-verification: googleXXXXXXXXXXXXXXXX.html
```

Astroのレイアウトが適用された状態では完全なHTMLページが返ってきてしまい、Google側が「このファイルは認証用ではない」と判定して失敗した。

2回デプロイしてようやく「public/」フォルダが正解だとわかった。

2回目に失敗したときは、ファイルを`public/`に移した後にDeploymentsタブで「Success」を確認する前に認証ボタンを押してしまったのが原因だった。まだCloudflareのCDNにファイルが届いていない状態でGoogleが確認に来ても当然失敗する。「デプロイ成功」→「少し待つ」→「確認ボタンを押す」という順番を守るだけで解決した。

ここでさらに1つ詰まった。デプロイは「Success」になったし、ブラウザで直接URLを開いたら認証ファイルの内容も正しく表示されていた。念のためCLIからも確認しようと`curl`で叩いてみた。

```bash
curl https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html
```

レスポンスは正しい1行のテキストだった。「これで絶対通る」と思ってSearch Consoleの「確認」ボタンを押したら、また「所有権を確認できませんでした」が出た。ブラウザでも`curl`でも正しい内容が返っているのに、なぜSearch Consoleだけ失敗するのか全く理解できなくて30分近く混乱した。

原因はCloudflareのCDNキャッシュだった。Googlebotが認証ファイルにアクセスしたとき、CDNキャッシュに**古いバージョン**（ファイルが存在しなかった404レスポンス、または`src/pages/`に置いていた時のレイアウト適用版）がまだ残っていて、Googlebotにはキャッシュが返されていた。ブラウザや`curl`でアクセスした時は最新版が返っているが、Googlebotが踏んだのはキャッシュだったという状況だった。Cloudflareの「Purge Cache」→「Purge Everything」でキャッシュを全削除してから再度「確認」ボタンを押したら通った。

3回目の試みで正しい手順を踏んでようやく成功した。「src/pages/」「デプロイ前に確認ボタン」という2つのミスで合計3回デプロイを無駄にした。手順を整理してからやり直せば最短1回で終わる作業だった。

認証成功後に「確認ファイルはもういらないだろう」と削除してしまったことがあった。1ヶ月後に「Googleはあなたのサイトの所有権を確認できなくなりました」というメールが届いた。定期的に認証ファイルのURLにアクセスして存在確認しているため、削除すると所有権が失効する。この失敗を一度やってから、認証ファイルは「削除禁止」のルールを自分で作った。

さらに、Search Consoleの「確認」ボタンを押しても「所有権を確認できませんでした」が続いてなかなか通らないケースもあった。ブラウザで認証ファイルのURLに直接アクセスしたら正しい内容が表示されていたのに、Search Consoleだけ失敗した。Cloudflareのキャッシュが原因で、GooglebotはCloudflareのCDNを通じてアクセスするため、CDNキャッシュに古いコンテンツが残っているとファイルが正常なのにGooglebotには古い（認証前の）内容が届いていた。Cloudflareの「Purge Cache」→「Purge Everything」でキャッシュを削除してから再確認で通った。

## 解決策

認証ファイルは`public/`フォルダに置く。`public/`に置いたファイルはAstroのビルド処理を通らずそのまま`dist/`にコピーされるので、ファイルの内容が一切変更されない。

### 1. Google Search Consoleで認証ファイルをダウンロード

1. `https://search.google.com/search-console` を開く
2. 左上の「プロパティを選択」→「プロパティを追加」
3. 「URLプレフィックス」にサイトのURL（`https://yourdomain.com`、末尾スラッシュなし）を入力して「続行」
4. 確認方法の一覧から「HTMLファイル」を選択
5. 認証用HTMLファイルをダウンロード（`googleXXXXXXXXXXXXXXXX.html` という名前）

「URLプレフィックス」と「ドメイン」の2種類の登録方法がある。ドメインプロパティはwwwあり・なし・httpとhttpsを1つのプロパティでまとめて管理できるが、CloudflareのDNS管理画面でTXTレコードを追加する手順が必要になる。最初はHTMLファイル認証で始めて、慣れてからドメインプロパティに移行するのがわかりやすかった。

「URLプレフィックス」で登録すると、`https://yourdomain.com`と`https://www.yourdomain.com`は別プロパティとして扱われる。将来的にwwwなしに統一するならwwwなしのURLで登録しておく方が管理が楽だった。

認証ファイルのダウンロードリンクはHTMLファイル選択後の画面に表示される。ファイル名は`googleXXXXXXXXXXXXXXXX.html`という形式で、`XXXXXXXXXXXXXXXX`の部分がサイトごとのユニークな識別子になっている。このファイルはサイトごとに異なるので、他のサイトの認証ファイルを流用することはできない。

### 2. publicフォルダに配置する

プロジェクトのルートにある`public/`フォルダにダウンロードしたファイルをそのまま置く。

```
my-astro-site/
├── public/
│   └── googleXXXXXXXXXXXXXXXX.html  ← ここに置く
├── src/
│   └── pages/
└── astro.config.mjs
```

`src/pages/`ではなく`public/`に置くのが唯一の正解。

`public/`フォルダがまだない場合は作成する。

```bash
mkdir public
```

Astroプロジェクト作成時に`public/`はデフォルトで作られているが、テンプレートによっては存在しないこともある。

### 3. ローカルで動作確認してからpush

ビルドして`dist/`に認証ファイルが含まれているか確認してからpushする。

```bash
npm run build
ls dist/google*.html
```

`dist/`に認証ファイルが出ていれば正しい設置場所。出ない場合はファイルが`public/`以外に置かれている。

ローカルで`npm run preview`を起動してブラウザで確認する方法もある。

```bash
npm run preview
# ブラウザで http://localhost:4321/googleXXXXXXXXXXXXXXXX.html を開く
```

1行のテキストが表示されればOK。完全なHTMLページが表示されてしまう場合は`public/`ではなく`src/pages/`に置いてしまっている。

```bash
git add public/googleXXXXXXXXXXXXXXXX.html
git commit -m "add google search console verification file"
git push
```

### 4. Cloudflare Pagesのデプロイ完了後に確認

Deploymentsタブでビルドの「Success」を確認してからSearch Consoleの「確認」ボタンを押す。まだデプロイ中にボタンを押すと確認に失敗する。

ボタンを押す前に、ブラウザで直接認証ファイルのURLにアクセスして内容を確認する。

`https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html` にアクセスして、以下のような1行だけのテキストが表示されればOK。

```
google-site-verification: googleXXXXXXXXXXXXXXXX.html
```

完全なHTMLページが表示されてしまう場合は`public/`ではなく`src/pages/`に置いてしまっている。

ブラウザで確認したあと、CLIからも`curl -I`でレスポンスヘッダーを確認しておくとキャッシュ問題の予防になった。

```bash
curl -I https://yourdomain.com/googleXXXXXXXXXXXXXXXX.html
```

レスポンスヘッダーの`cf-cache-status`フィールドを確認する。`HIT`と表示されているならCloudflareのCDNキャッシュが返されている状態で、`MISS`なら直接オリジンから取得している。

```
HTTP/2 200
content-type: text/html
cf-cache-status: HIT   ← キャッシュが返されている
```

`cf-cache-status: HIT`の場合、Googlebotにもキャッシュが返される可能性がある。Search Consoleの確認前に `Purge Cache` でキャッシュを削除してから押すと確実だった。

Cloudflareには数分のキャッシュがあるので、デプロイ成功直後でもCDNのエッジに届いていないことがある。Deploymentsタブに「Success」が出た後、1〜2分待ってからブラウザでファイルのURLを確認するとより確実。

ブラウザで確認した時にファイルの内容が正しく表示されているのに、Search Consoleの「確認」ボタンを押しても失敗し続ける場合は、Cloudflareのキャッシュが原因の可能性がある。Cloudflareダッシュボードで「Caching」→「Purge Cache」→「Purge Everything」でキャッシュを削除してから再度確認ボタンを押す。

### 5. 認証が通らない場合のさらなる確認

「確認」ボタンを押しても失敗する場合、Googlebot側でのアクセスに問題があるケースがある。Search Consoleの「URL検査」ツールで認証ファイルのURLを直接検査すると、GooglebotがそのURLにアクセスできているか確認できる。

「URL検査」でURLを入力すると「Googleでテスト」ボタンが出る。これを押すとGooglebotがそのURLにアクセスして取得したレスポンスが確認できる。ここで「認証ファイルの内容が表示されている」なら認証が通るはずで、「404」や「ページが取得できない」ならCloudflareのデプロイに問題がある。

もう一つの原因として、`robots.txt`で`Disallow: /google*.html`のような設定になっていてGooglebotが認証ファイルにアクセスできていないケースがある。`robots.txt`に認証ファイルをブロックする設定が含まれていないか確認する。通常は`Disallow`の設定は不要なので、もし書いてあれば削除する。

### 6. 所有権確認後にサイトマップを送信する

所有権確認が完了したら、左メニュー「サイトマップ」で`sitemap-index.xml`を入力して「送信」をクリックする。AstroにサイトマッププラグインとサイトマップはデフォルトでこのURLで生成される。`sitemap.xml`ではなく`sitemap-index.xml`が正しいファイル名なので注意。

サイトマップを事前に設定していない場合は[Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)で設定してから送信する。

サイトマップ送信後に「ステータス：成功」になっても、最初は「検出されたURL：0」と表示されることが多い。Googleがサイトマップを処理してインデックスに登録するまで数日〜1週間かかることがあるので、焦らず数日後に再確認する。

Search ConsoleのURL検査ツールで個別のURLのインデックス状況も確認できる。上部の検索バーにページのURLを入力して「Googleでテスト」を押すと、Googleがそのページをクロールできるかリアルタイムで確認できる。インデックス登録申請もこの画面からできる。インデックス申請後は通常数時間〜数日でインデックスされることが多かった。

### 7. 認証ファイルを削除しない

所有権確認が完了した後も、`public/google*.html`ファイルを削除してはいけない。

Googleは定期的に認証ファイルのURLにアクセスして所有権を継続確認している。ファイルを削除すると数週間〜1ヶ月後に「サイトの所有権を確認できなくなりました」というメールが届いて、Search Consoleのプロパティが無効になってしまう。

「確認が完了したしもう不要だろう」と思って削除してしまい、1ヶ月後にメールが届いてプロパティが無効になった経験があった。認証ファイルは`.gitignore`には絶対に追加しない。`.gitignore`に誤って追加しないよう、認証ファイルのファイル名をメモしておくと安心だった。

所有権が失効してしまった場合は、もう一度Search Consoleで「プロパティを追加」から手順をやり直す。プロパティ自体が削除されるわけではなく「所有権未確認」状態になるだけなので、再認証すれば過去のデータも引き続き確認できる。ただし所有権が失効している間のデータは欠損するので、長期間放置しないように注意が必要だった。

## ハマったポイント

- ドメイン認証（DNS TXTレコード方式）を先に試したが、CloudflareのDNS設定のプロキシ周りの影響でGoogleのTXTレコード確認が通らなかった。1時間試した末に諦めてHTMLファイル認証に切り替えたら15分で終わった。CloudflareのプロキシがTXTレコードの解決に影響する場合があるので、素直にHTMLファイル認証から始める方が確実だった
- ブラウザで認証ファイルのURLを開いたら正しい内容が表示されていて、`curl`コマンドで確認しても同じく正しい内容が返ってきた。なのにSearch Consoleの「確認」ボタンを押すと失敗し続けた。Cloudflare CDNキャッシュに古いバージョンが残っていて、Googlebotにはキャッシュが返されていたのが原因だった。「curl正常 → GSC失敗」という状態はキャッシュを真っ先に疑う
- HTMLファイルは必ず`public/`に置く。`src/pages/`に置くとAstroが内容をレイアウトやコンポーネントで囲んでしまい、Googleの所有権確認が失敗する。この間違いに気づくまで2回デプロイを無駄にした
- デプロイ完了前に「確認」ボタンを押しても必ず失敗する。Cloudflare PagesのDeploymentsタブで「Success」になってから少なくとも1〜2分待ってから押す。「デプロイが終わったのにボタンを押してもなかなか成功しない」と思ったら、実はまだCloudflareのCDNにファイルが伝播していなかった
- 確認後も認証HTMLファイルを削除してはいけない。Search ConsoleはURLにアクセスできるかを定期的に確認しているので、削除すると後日「所有権を確認できなくなりました」というメールが届いて確認が無効になる。1ヶ月後に気づいても遅い
- 「URLプレフィックス」と「ドメイン」の2種類の登録方法があって、ドメイン認証はwwwあり・なし両方をまとめて管理できるが、CloudflareのDNS設定でTXTレコードを追加する手順が必要。HTMLファイル認証はDNS操作が不要なので手順が明確だった
- サイトマップのURLをSearch Consoleに送信する時、`sitemap.xml`と入力したら「フェッチできませんでした」というエラーが出た。Astroが生成するのは`sitemap-index.xml`なのでこちらを入力する必要があった
- `dist/`の中身を確認せずにpushして「何度ボタンを押しても失敗する」と悩むくらいなら、先に`npm run build && ls dist/google*.html`で確認するのが正解。ビルド後に`dist/`にファイルが存在しなければ設置場所が間違っている。ローカル確認で済む問題をデプロイ後に調べると時間が余計にかかる
- Search Consoleに登録した後、実際にインデックスされるまでに時間がかかる。「登録したのに記事がGoogle検索に出ない」と数日で焦るのは早い。サイトマップ送信から1〜2週間様子を見てから判断するくらいがちょうどよかった
- Cloudflareのキャッシュがある場合、ブラウザではファイルが正常に見えているのにSearch Consoleの確認が失敗し続けることがある。GooglebotがCloudflareのキャッシュを通じてアクセスした場合も同様。Purge Cacheを試して解決した
- `robots.txt`でGooglebotが認証ファイルにアクセスできない設定になっていると確認が通らない。`User-agent: *`に対して`Disallow`が広すぎる設定になっていないか確認した。認証ファイルのURLパターン（`/google*.html`）が意図せずブロックされていることがあった
- Search ConsoleのURL検査ツールで認証ファイルのURLを直接テストすると、Googlebotからの視点でアクセスできているかが確認できた。ブラウザから見て正常でもURL検査で「取得できない」になっている場合はCloudflareの設定に問題がある。このツールを使うと「ブラウザとGooglebotで見え方が違う」という問題を素早く切り分けられた
- 所有権が失効してしまっても、プロパティ自体は削除されない。「再確認」の手順を踏めば過去のデータにアクセスできる状態に戻せた。ただし失効中のデータは欠損するので、「消えた」と思って焦る前にまず再確認を試みるのが正解だった

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroでrobots.txtとsitemapを自動生成する方法](/posts/astro-sitemap-robots)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
