---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトに@astrojs/sitemapプラグインでsitemap.xmlを自動生成し、robots.txtを手動で設置する方法を解説します。'
---

## やりたかったこと

AstroサイトをCloudflare Pagesで公開してGoogle Search Consoleに登録したら、サイトマップを送信するよう求められた。最初は`sitemap.xml`というのは自分で手書きするXMLファイルのことだと思っていた。WordPressで見たことがあったので「あれを自分で書くのか」と覚悟した。

実際、最初の3ヶ月はそうやっていた。`public/sitemap.xml`を直接開いて、記事を書くたびに`<url>`タグを1件ずつ手で追加していた。記事が10本くらいまでは良かったが、30本を超えたあたりで「これは絶対に続かない」と感じ始めた。更新を忘れてインデックスされない記事が出てきたり、URLをtypoしたまま登録してしまったりと問題が積み重なっていた。

3ヶ月目にようやく`@astrojs/sitemap`というプラグインを見つけた。「プラグインをインストールして設定ファイルに2行追加するだけで完結する」と書いてあって半信半疑だったが、実際に試してみたら本当にそれだけで自動生成されるようになった。手動管理の3ヶ月が何だったのかと思った。

ただ自動生成への切り替えも一筋縄ではいかなかった。「siteプロパティ未設定エラー」「sitemap-index.xmlとsitemap.xmlの混乱」「robots.txtの設置場所間違い」と3つのハマりポイントを踏んで、完成まで2時間かかった。

また`robots.txt`はどこに置けばいいかも最初わからず、`src/pages/`に置いたらAstroがそれを処理してしまって想定外の挙動になった。さらに`astro.config.mjs`の`site`プロパティを書き忘れてビルドが止まるエラーも踏んだ。一通り動くまでに複数の詰まりポイントがあったので、まとめて残しておく。

手動でXMLを書いていた時代にやらかしたのが、URLのtypoだった。記事のslugを書き間違えたまま`sitemap.xml`に書いてしまい、その記事が正しいURLでインデックスされずに存在しないURLでインデックスされてしまっていた。Googleがインデックスした後に気づいて修正するはめになった。自動生成であれば記事ファイルのパスからURLを生成するのでtypoが入り込む余地がない、という安心感が大きかった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Node.js 20.11.0
- npm 10.2.4

## 試したこと・うまくいかなかったこと

最初、`public/sitemap.xml`にXML形式のファイルを手動で作った。記事のURLを1件ずつ書いていく作業で、10記事くらいまでは良かったが30記事を超えたあたりから管理しきれなくなった。記事を追加するたびにsitemap.xmlも手動で更新しないといけないし、URLを書き間違えることもあった。`<loc>`の中にtypoがあってもGoogleはエラーを教えてくれないので、しばらくURLが間違ったまま放置されていた。

`@astrojs/sitemap`の前に、もっと汎用的なViteプラグインで`vite-plugin-sitemap`というものを試したことがあった。「ViteベースならAstroでも使えるだろう」と思って`npm install vite-plugin-sitemap`してから`astro.config.mjs`の`vite.plugins`に追加した。ビルド自体は通ったが、生成されたsitemapのURLが全部おかしかった。Astroのファイルベースルーティングを無視してVite側のビルドパスを参照していたため、`.astro`ファイルのパスがそのまま入ったり、末尾の拡張子が残ったりしていた。結局30分試してあきらめた。AstroのSSG出力に対応しているのは`@astrojs/sitemap`だけで、汎用的なViteプラグインではAstroの出力を正しく解釈できないとわかった。

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

`astro.config.mjs`で`site`プロパティを設定した後、ローカルの`npm run dev`でも確認しようとしたが、devモードではサイトマップは生成されないことに気づいた。サイトマップは`npm run build`でビルドした時にしか生成されないので、確認は必ず`npm run build`後に`dist/`を見る必要がある。「devで確認できない」という事実を知らずに「なぜdevで見えないのか」と悩んだ時間があった。

サイトマップが生成されたと思って`dist/sitemap-0.xml`を開いたら、記事ページのURLが含まれていないことに気づいたことがあった。原因を調べたらAstroのコンテンツコレクションを使って記事ページを生成していたが、`getStaticPaths()`から返すパスがサイトマップに含まれるかどうかはAstroのバージョンによって挙動が違うことがわかった。Astro 4以前では追加設定が必要な場合があった。自分のケースはAstro 5.2.3で問題なく記事URLが含まれていたが、バージョンが古い場合は確認が必要だった。

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

カスタムドメインを設定する前は`*.pages.dev`のURLでサイトにアクセスできる。この段階でrobots.txtに書く`Sitemap:`のURLを`*.pages.dev`ベースで設定してしまうと、カスタムドメイン切り替え後に更新が必要になる。最初から独自ドメインを想定してURLを書いておくのが後々楽だった。

### 5. サイトマップの優先度を設定する（応用）

`@astrojs/sitemap`は`priority`と`changefreq`の設定もできる。デフォルトでは`priority`は設定されない。Googleの公式見解では`priority`や`changefreq`はほとんど無視されているが、設定したい場合は`serialize`オプションを使う。

```js
integrations: [
  sitemap({
    serialize(item) {
      if (/posts/.test(item.url)) {
        return {
          ...item,
          changefreq: 'monthly',
          lastmod: new Date(),
        };
      }
      return item;
    },
  }),
],
```

記事ページ（`/posts/`を含むURL）だけ`changefreq`を設定するような使い方ができる。`lastmod`に実際の更新日時を入れる場合は、frontmatterの`date`を読み込んで設定するとより正確になる。

`lastmod`を正確に設定したい場合は、Astroのコンテンツコレクションからfrontmatterの`date`を読み出して渡す方法がある。ただしこの実装は少し複雑になる上、Googleが`lastmod`をクロールの優先度判断にどれだけ使うかは不明瞭なので、最初はデフォルト設定で動かしてから必要に応じて応用するくらいのスタンスがちょうどよかった。

### 6. 両方をpushしてデプロイ

```bash
git add astro.config.mjs public/robots.txt
git commit -m "add sitemap plugin and robots.txt"
git push
```

デプロイ後、以下のURLでブラウザから確認する。

- `https://yourdomain.com/sitemap-index.xml` → 全記事のURLが含まれているか確認
- `https://yourdomain.com/robots.txt` → Sitemapの行のURLが正しいか確認

### 7. Google Search Consoleでサイトマップを送信

左メニュー「サイトマップ」→ URLの入力欄に `sitemap-index.xml` と入力して「送信」をクリックする。

送信後すぐに「ステータス：成功」になれば完了。「フェッチできませんでした」が出る場合は、デプロイが完了しているか確認してから数分後に再送信する。

「読み取り成功」と表示された後も「検出されたURL：0」になることがある。Search Consoleがサイトマップの中身を処理するまで数日かかるので、送信から1〜3日後に再確認する。

Search ConsoleへのHTMLファイル認証登録がまだの場合は[Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)から先に設定する。

サイトマップ送信後の数日間は、カバレッジレポートの「有効」のURL数がゼロのままになることが多い。これは正常な動作で、Googleがサイトマップを処理してURLをクロールキューに入れるまでに時間がかかるため。1週間待ってもゼロのままなら、サイトマップのURLが正しいか、サイトがGooglebotからアクセスできるかを確認する。

### 8. sitemap-index.xmlの中身を確認する方法

デプロイ後に実際のサイトマップの内容を素早く確認したい場合は、`grep`や`curl`を使うのが便利だった。

特定のURLがサイトマップに含まれているか確認する：

```bash
# ローカルのビルド成果物で確認
grep "posts/article-slug" dist/sitemap-0.xml

# デプロイ後に本番のサイトマップから確認
curl -s https://yourdomain.com/sitemap-0.xml | grep "posts/"
```

全URLの一覧だけを抽出して確認したい場合：

```bash
grep -o '<loc>[^<]*</loc>' dist/sitemap-0.xml | sed 's/<[^>]*>//g'
```

記事数が多いときに「この記事のURLは入っているか」を確認したい場合は`grep`が一番速かった。Search Consoleで「検出されたURL：0」になった時もまずこのコマンドで確認して、ファイル自体にURLが入っているかどうかを切り分けた。

draft記事（公開したくない記事）がサイトマップに入っていないか確認するのにも使える：

```bash
# draft: true のページがサイトマップに含まれていないか確認
grep "draft" dist/sitemap-0.xml
```

何も出力されなければdraftページは含まれていない。ただしこの確認はfrontmatterのdraftフラグをfilterで除外している場合のみ有効で、除外設定が正しく動いているかはビルドログでも確認できる。

## ハマったポイント

- `site`を設定しないとプラグインがエラーを出してビルドが止まる。必須プロパティなので忘れずに設定する。エラーメッセージは明確なので原因はすぐわかるが、プラグインを追加したのに`site`の設定が必要とは思っていなかった
- `site`にlocalhostを書いてしまうと`sitemap-0.xml`の中のURLが全部`http://localhost:4321/...`になる。Search Consoleで「フェッチできませんでした」が出たら`sitemap-0.xml`の中身を確認して、URLがlocalhostになっていないか確認するといい
- サイトマップのファイル名が`sitemap.xml`ではなく`sitemap-index.xml`だった。Search Consoleで`sitemap.xml`を入力したら「フェッチできませんでした」というエラーが出た。`sitemap-index.xml`と書き直したら「ステータス：成功」になった。これは見落としやすい
- Cloudflareがrobots.txtを自動生成して上書きする、という情報をどこかで見て心配したが、実際には`public/robots.txt`に置いたものが優先されて問題なかった
- `src/pages/`に`.txt`ファイルを置いても機能しなかった。Astroは`.astro`・`.md`・`.mdx`・`.html`以外のファイルはページとして扱わない。テキストファイルはstatic assetとして`public/`に置くのが正解だった
- プラグインをインストールするだけではサイトマップは生成されない。`astro.config.mjs`の`integrations`に追加するのを忘れると、ビルドしても`sitemap-index.xml`が生成されない。インストール後に設定ファイルへの追記が必要だった。「インストールは完了しているのになぜ生成されないのか」と30分以上調べた
- robots.txtの`Sitemap:`行に`*.pages.dev`のURLを書いてしまっていた。カスタムドメインを設定した後もrobots.txtを更新し忘れていて、Googlebot向けのサイトマップURLが`*.pages.dev`のままになっていた。カスタムドメイン設定後は必ずrobots.txtの内容も更新する
- `dist/`ディレクトリの中身を確認せずにSearch Consoleに送信してしまうと、存在しないファイルを送信することになる。`npm run build && ls dist/sitemap*.xml`でファイル存在確認してからSearch Consoleに送信する順番を守るだけで余分なデバッグ時間がなくなった
- devモードではサイトマップが生成されない。`npm run dev`でサイトを確認しながら「なぜ`/sitemap-index.xml`が404になるのか」と1時間悩んだが、サイトマップはビルド時にのみ生成される。`npm run build && npm run preview`の組み合わせで確認する必要があった
- `sitemap-0.xml`の中に記事ページのURLが含まれていなかった。コンテンツコレクションで記事を管理している場合、Astroのバージョンによってサイトマップへの含まれ方が違うことがある。生成後に`head -50 dist/sitemap-0.xml`で実際の記事URLが含まれているか必ず確認するようにした
- 手動でsitemap.xmlを書いていた時代にURLのtypoが入り込んで、誤ったURLでインデックスされてしまった。自動生成に切り替えてからはtypoのリスクがゼロになった。「記事を追加するたびにsitemap.xmlも更新する」という作業を完全になくせたのが一番の恩恵だった
- Astro用ではない汎用Viteサイトマッププラグイン（`vite-plugin-sitemap`など）を試したが、AstroのSSG出力のURLを正しく解釈してくれなかった。生成されたURLに`.astro`拡張子が残ったり、ルーティングがずれたりした。AstroのサイトマップはAstro公式の`@astrojs/sitemap`だけが正しく動くと理解するまで30分かかった
- frontmatterに`draft: true`を設定した記事が`sitemap-0.xml`に含まれてしまっていた。filterオプションを追加し忘れていたのが原因で、Googleにインデックスしたくないdraft記事のURLが普通に入っていた。`filter: (page) => !page.includes('/draft-')`のような対応が必要だった
- カスタムドメインを変更した時にrobots.txtの`Sitemap:`行の更新を忘れた。新ドメインでサイトを公開した後も`robots.txt`は旧ドメインのURLを指したままで、Googlebotが古いドメインのサイトマップを参照し続けていた。翌日になってからSearch Consoleのエラーで気づいた

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
