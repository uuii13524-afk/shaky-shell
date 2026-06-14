---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトに@astrojs/sitemapプラグインでsitemap.xmlを自動生成し、robots.txtを手動で設置する方法を解説します。'
---

## やりたかったこと

AstroサイトをCloudflare Pagesで公開してGoogle Search Consoleに登録したら、サイトマップを送信するよう求められた。`sitemap.xml`は手動でXMLを書くものだと思っていたが、Astroにはプラグインで自動生成できる仕組みがあった。

また`robots.txt`はどこに置けばいいかも最初わからず、`src/pages/`に置いたらAstroがそれを処理してしまって想定外の挙動になった。さらに`astro.config.mjs`の`site`プロパティを書き忘れてビルドが止まるエラーも踏んだ。一通り動くまでに複数の詰まりポイントがあったので、まとめて残しておく。

プラグインをインストールして設定ファイルに2行追加するだけで完結するはずが、実際には「siteプロパティ未設定エラー」「sitemap-index.xmlとsitemap.xmlの混乱」「robots.txtの設置場所間違い」と3つのハマりポイントを踏んで、完成まで2時間かかった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Node.js 20.11.0
- npm 10.2.4

## 試したこと・うまくいかなかったこと

最初、`public/sitemap.xml`にXML形式のファイルを手動で作った。記事のURLを1件ずつ書いていく作業で、10記事くらいまでは良かったが30記事を超えたあたりから管理しきれなくなった。記事を追加するたびにsitemap.xmlも手動で更新しないといけないし、URLを書き間違えることもあった。`<loc>`の中にtypoがあってもGoogleはエラーを教えてくれないので、しばらくURLが間違ったまま放置されていた。

`@astrojs/sitemap`というプラグインがあると知ってインストールしたが、`astro.config.mjs`に`site`プロパティを書かずに追加してビルドしたらエラーになった。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
A site URL is required to generate a sitemap.
```

`site`を追加すればいいとわかったが、今度はローカルURLを書いてしまった。`site: 'http://localhost:4321'`にしてビルドしたら、生成された`sitemap-0.xml`の中のURLが全部`http://localhost:4321/...`になっていた。Search Consoleに送信しても意味がないので本番URLに書き直した。

`robots.txt`は最初`src/pages/robots.txt`として置いた。Astroが処理して`/robots.txt`にアクセスできるようになるかと思ったが、テキストファイルはAstroのページとして認識されなかった。`robots.ts`でエンドポイントを作る方法もあると知って試みたが、静的なファイルを置くだけなら`public/`が正解だとわかってやり直した。

また、Search Consoleにサイトマップを送信する時に`sitemap.xml`と入力したら「フェッチできませんでした」というエラーが出た。`sitemap-index.xml`と`sitemap.xml`は別のファイルで、Astroが生成するのは`sitemap-index.xml`の方だとわかるまで詰まった。

`@astrojs/sitemap`をインストールするだけでサイトマップが生成されると思っていたのも間違いだった。パッケージのインストール後に`astro.config.mjs`の`integrations`配列に追加する設定が別途必要で、この設定を書き忘れると`npm install`後にビルドしても`sitemap-index.xml`は一切生成されない。30分以上「なぜ生成されないのか」を調べてようやく気づいた。

ビルドした後に`dist/sitemap-index.xml`が生成されているかを確認せずにSearch Consoleに送信してしまって、「ステータス：読み取り不可」というエラーが出たことも。「送信したのになぜ読めないのか」と10分悩んだが、そもそもファイルが存在していなかった。作業前に`ls dist/sitemap*.xml`で確認する癖をつければ防げた。

## 解決策

### 1. sitemapプラグインをインストール

```bash
npm install @astrojs/sitemap
```

### 2. astro.config.mjsに追記する

```js
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://yourdomain.com',  // 本番のURLを書く（localhostにしない）
  integrations: [sitemap()],
});
```

`site`には本番環境のURL（`https://`付き）を書く。末尾のスラッシュはあってもなくてもOK。**ここでlocalhostを書いてしまうと生成されるサイトマップのURLが全部localhostになる**ので注意。

特定のページをサイトマップから除外したい場合は`filter`オプションを使う。管理画面やプレビューページなどnoindexにしたいページがある場合に役立つ。

```js
integrations: [
  sitemap({
    filter: (page) => !page.includes('/admin/') && !page.includes('/preview/'),
  }),
],
```

カテゴリページなど動的に生成されるページがある場合、`filter`で制御するより`frontmatter`に`noindex`フラグを持たせてそれを見てフィルタリングする方が管理しやすかった。

### 3. ビルドして動作確認

```bash
npm run build
ls dist/sitemap*.xml
```

`sitemap-index.xml`と`sitemap-0.xml`の2ファイルが生成されていれば成功。

`sitemap-index.xml`は各サイトマップファイルを束ねるインデックスで、`sitemap-0.xml`が実際のページURLの一覧。記事数が多くなると`sitemap-1.xml`と分割されていく。Search Consoleには`sitemap-index.xml`を送信する。

`dist/sitemap-0.xml`の中身を確認して、記事ページのURLが正しく入っているか確認する。

```bash
head -20 dist/sitemap-0.xml
```

URLがlocalhostになっていないか、記事のURLが含まれているか、この2点を必ず確認しておく。

xmllintが使える環境であればサイトマップのXMLが正しいかバリデーションもできる。

```bash
xmllint --noout dist/sitemap-0.xml
```

エラーが出なければXMLの構造は正しい。Googleへの送信前に一応確認しておくと安心だった。

Windowsの場合、`xmllint`はGit Bashに含まれていることがある。PowerShellではデフォルトで使えないので、Git Bashのターミナルから確認するといい。

### 4. robots.txtをpublicフォルダに設置

`public/robots.txt`として以下の内容で保存する。

```
User-agent: *
Allow: /

Sitemap: https://yourdomain.com/sitemap-index.xml
```

`Sitemap:`の行のURLは自分のドメインに書き換える。`public/`に置くことでビルド後に`dist/robots.txt`にそのままコピーされる。Astroによる変換処理は一切入らない。

`robots.txt`に書く`Sitemap:`の値はCloudflareのカスタムドメインのURLを使う。`*.pages.dev`ではなく独自ドメインのURLを書く。

ビルドしてrobots.txtが正しく出力されているか確認する。

```bash
cat dist/robots.txt
```

`Sitemap:`の行に設定したURLが表示されていればOK。

noindexにしたいページがある場合は`robots.txt`ではなく各ページの`<meta name="robots" content="noindex">`で制御する。`robots.txt`の`Disallow`はクロールをブロックするものであって、インデックスを制御するものではない。この違いを最初に理解しておかないと、Search Consoleのカバレッジレポートで「除外済み」になる原因を調べて時間を無駄にする。

### 5. 両方をpushしてデプロイ

```bash
git add astro.config.mjs public/robots.txt
git commit -m "add sitemap plugin and robots.txt"
git push
```

デプロイ後、以下のURLでブラウザから確認する。

- `https://yourdomain.com/sitemap-index.xml` → 全記事のURLが含まれているか確認
- `https://yourdomain.com/robots.txt` → Sitemapの行のURLが正しいか確認

### 6. Google Search Consoleでサイトマップを送信

左メニュー「サイトマップ」→ URLの入力欄に `sitemap-index.xml` と入力して「送信」をクリックする。

送信後すぐに「ステータス：成功」になれば完了。「フェッチできませんでした」が出る場合は、デプロイが完了しているか確認してから数分後に再送信する。

「読み取り成功」と表示された後も「検出されたURL：0」になることがある。Search Consoleがサイトマップの中身を処理するまで数日かかるので、送信から1〜3日後に再確認する。

Search Consoleへの登録がまだの場合は[Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)から先に設定する。

サイトマップ送信後の数日間は、カバレッジレポートの「有効」のURL数がゼロのままになることが多い。これは正常な動作で、Googleがサイトマップを処理してURLをクロールキューに入れるまでに時間がかかるため。1週間待ってもゼロのままなら、サイトマップのURLが正しいか、サイトがGooglebotからアクセスできるかを確認する。

## ハマったポイント

- `site`を設定しないとプラグインがエラーを出してビルドが止まる。必須プロパティなので忘れずに設定する。エラーメッセージは明確なので原因はすぐわかるが、プラグインを追加したのに`site`の設定が必要とは思っていなかった
- `site`にlocalhostを書いてしまうと`sitemap-0.xml`の中のURLが全部`http://localhost:4321/...`になる。Search Consoleで「フェッチできませんでした」が出たら`sitemap-0.xml`の中身を確認して、URLがlocalhostになっていないか確認するといい
- サイトマップのファイル名が`sitemap.xml`ではなく`sitemap-index.xml`だった。Search Consoleで`sitemap.xml`を入力したら「フェッチできませんでした」というエラーが出た。`sitemap-index.xml`と書き直したら「ステータス：成功」になった。これは見落としやすい
- Cloudflareがrobots.txtを自動生成して上書きする、という情報をどこかで見て心配したが、実際には`public/robots.txt`に置いたものが優先されて問題なかった
- `src/pages/`に`.txt`ファイルを置いても機能しなかった。Astroは`.astro`・`.md`・`.mdx`・`.html`以外のファイルはページとして扱わない。テキストファイルはstatic assetとして`public/`に置くのが正解だった
- プラグインをインストールするだけではサイトマップは生成されない。`astro.config.mjs`の`integrations`に追加するのを忘れると、ビルドしても`sitemap-index.xml`が生成されない。インストール後に設定ファイルへの追記が必要だった。「インストールは完了しているのになぜ生成されないのか」と30分以上調べた
- robots.txtの`Sitemap:`行に`*.pages.dev`のURLを書いてしまっていた。カスタムドメインを設定した後もrobots.txtを更新し忘れていて、Googlebot向けのサイトマップURLが`*.pages.dev`のままになっていた。カスタムドメイン設定後は必ずrobots.txtの内容も更新する
- `dist/`ディレクトリの中身を確認せずにSearch Consoleに送信してしまうと、存在しないファイルを送信することになる。`npm run build && ls dist/sitemap*.xml`でファイル存在確認してからSearch Consoleに送信する順番を守るだけで余分なデバッグ時間がなくなった

SEOのmeta情報も一緒に設定したい場合は[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も合わせて対応しておくとSEO対策が一通り揃う。

## 関連記事

- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [Astroで新しいページを追加する基本的な方法](/posts/astro-add-page)
- [Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)
- [Cloudflare Pagesのビルドログの見方とエラーの対処法](/posts/cloudflare-pages-build-log)

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">
