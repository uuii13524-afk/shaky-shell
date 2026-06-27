---
title: 'Astroでrobots.txtとsitemapを自動生成する方法'
date: '2026-05-05'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトに@astrojs/sitemapプラグインでsitemap.xmlを自動生成し、robots.txtを手動で設置する方法を解説します。'
---

## ひとことで言うと

```bash
npm install @astrojs/sitemap
```

```js
// astro.config.mjs
import sitemap from '@astrojs/sitemap';
export default defineConfig({
  site: 'https://yourdomain.com',  // localhost はダメ
  integrations: [sitemap()],
});
```

```bash
npm run build && ls dist/sitemap*.xml
# → sitemap-index.xml と sitemap-0.xml が生成されたら成功
```

Search Consoleに送る時は `sitemap.xml` ではなく `sitemap-index.xml` を入力する。

---

## やりたかったこと

AstroサイトをCloudflare Pagesで公開してGoogle Search Consoleに登録したら、サイトマップを送信するよう求められた。最初は`sitemap.xml`を自分で手書きするXMLファイルだと思って、`public/sitemap.xml`を直接編集して記事を書くたびに`<url>`タグを1件ずつ追加していた。

3ヶ月間それを続けたが、記事が30本を超えたあたりで破綻した。更新を忘れてインデックスされない記事が出てきたり、URLをtypoしたまま登録してしまったりと問題が積み重なった。`<loc>`の中のtypoはGoogleがエラーを教えてくれないので、誤ったURLでインデックスされてしばらく気づかなかった。

`@astrojs/sitemap`プラグインを見つけてから試してみたら、「プラグインをインストールして設定ファイルに2行追加するだけ」が本当にそれだけだった。手動管理の3ヶ月が何だったのかと思った。

ただ自動生成への切り替えも一筋縄ではいかなかった。`site`プロパティ未設定でビルドエラー、`sitemap-index.xml`と`sitemap.xml`の混乱、`integrations`への追加を忘れてサイトマップが生成されない、という3つのハマりポイントを踏んで完成まで2時間かかった。

## 環境

- Astro 5.2.3
- Cloudflare Pages（Freeプラン）
- Node.js 20.11.0
- npm 10.2.4

## 試したこと・うまくいかなかったこと

**汎用ViteプラグインでサイトマップURLがおかしくなった**

`@astrojs/sitemap`を知る前に`vite-plugin-sitemap`を試した。「ViteベースならAstroでも使えるだろう」と思って`npm install vite-plugin-sitemap`してから`astro.config.mjs`の`vite.plugins`に追加した。ビルド自体は通ったが、生成されたサイトマップのURLが全部おかしかった。Astroのファイルベースルーティングを無視してVite側のビルドパスを参照していたため、`.astro`ファイルのパスがそのまま入ったり末尾の拡張子が残ったりしていた。30分試してあきらめた。

生成されたサイトマップを`cat dist/sitemap-0.xml`で確認したら以下のような形になっていた。

```xml
<url>
  <loc>https://yourdomain.com/src/pages/posts/my-article.astro</loc>
</url>
```

URLに`.astro`拡張子が付いていてGoogleがクロールしてもページが存在しない状態だった。Astroのルーティングを理解しているプラグインでないと正しいURLが生成されないことがわかった。

**`@astrojs/sitemap`をインストールしてもサイトマップが生成されなかった**

`npm install @astrojs/sitemap`の後ビルドしたが`sitemap-index.xml`が生成されなかった。「インストールが失敗したのかも」と思ってもう一度インストールし直したが変わらなかった。原因はパッケージのインストールだけでは動かず、`astro.config.mjs`の`integrations`配列に追加する設定が別途必要だったことで、これを書き忘れていた。30分以上「なぜ生成されないのか」を調べてようやく気づいた。

**`site`プロパティをlocalhostで設定してしまった**

`integrations`への追加後、`site`プロパティが必要というエラーが出た。

```
[@astrojs/sitemap] No `site` option is set in your Astro config.
A site URL is required to generate a sitemap.
```

`site`を追加したが、ローカル確認用に`site: 'http://localhost:4321'`と書いたままビルドした。生成された`sitemap-0.xml`の中のURLが全部`http://localhost:4321/...`になっていた。Search Consoleに送信しても意味がないので本番URLに書き直した。

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

`site`には本番環境のURL（`https://`付き）を書く。**ここでlocalhostを書いてしまうと生成されるサイトマップのURLが全部localhostになる**ので注意。

特定のページをサイトマップから除外したい場合は`filter`オプションを使う。

```js
integrations: [
  sitemap({
    filter: (page) => !page.includes('/admin/') && !page.includes('/preview/'),
  }),
],
```

### 3. ビルドして動作確認

```bash
npm run build
ls dist/sitemap*.xml
```

`sitemap-index.xml`と`sitemap-0.xml`の2ファイルが生成されていれば成功。`sitemap-index.xml`は各サイトマップファイルを束ねるインデックスで、Search Consoleには`sitemap-index.xml`を送信する。

`dist/sitemap-0.xml`の中身を確認して、記事ページのURLが正しく入っているか確認する。

```bash
head -20 dist/sitemap-0.xml
```

URLがlocalhostになっていないか、記事のURLが含まれているかの2点を確認しておく。

サイトマップは`npm run dev`では生成されない。`npm run build`後の`dist/`フォルダで確認するのが唯一の方法で、devサーバーで`/sitemap-index.xml`にアクセスしても404になる。

### 4. robots.txtをpublicフォルダに設置

`public/robots.txt`として以下の内容で保存する。

```
User-agent: *
Allow: /

Sitemap: https://yourdomain.com/sitemap-index.xml
```

`Sitemap:`の行のURLは自分のドメインに書き換える。`public/`に置くことでビルド後に`dist/robots.txt`にそのままコピーされる。Astroによる変換処理は一切入らない。

`src/pages/`に`.txt`ファイルを置いてもAstroはページとして処理しないため機能しなかった。テキストファイルはstatic assetとして`public/`に置くのが正解だった。

```bash
cat dist/robots.txt
```

`Sitemap:`の行に設定したURLが表示されていればOK。

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

Search ConsoleへのHTMLファイル認証登録がまだの場合は[Google Search ConsoleのHTMLファイル認証をAstro+Cloudflare Pagesで行う手順](/posts/google-search-console-html-verification)から先に設定する。

## ハマったポイント

- パッケージをインストールするだけではサイトマップは生成されないと思っていなかった。`npm install @astrojs/sitemap`後に`astro.config.mjs`の`integrations`配列への追加が別途必要で、これを書き忘れると`npm run build`しても`sitemap-index.xml`は生成されない。「インストールしたのになぜ動かないのか」と30分悩んだが、設定ファイルへの追記を忘れていただけだった
- `site`プロパティにlocalhostを書いてしまうと`sitemap-0.xml`の中のURLが全部`http://localhost:4321/...`になる。Search Consoleで「フェッチできませんでした」が出た時は`sitemap-0.xml`の中身を確認して、URLがlocalhostになっていないかを最初に確認する
- Search ConsoleにサイトマップのURLを入力する時、`sitemap.xml`と書いたら「フェッチできませんでした」というエラーが出た。Astroが生成するのは`sitemap-index.xml`で、`sitemap.xml`というファイルは存在しない。この2つのファイル名は全然違うので入力欄に正確に書く必要があった
- `src/pages/`に`.txt`ファイルを置いてrobots.txtを設置しようとしたが機能しなかった。Astroは`.astro`・`.md`・`.mdx`・`.html`以外のファイルをページとして扱わない。テキストファイルは`public/`に置くのが唯一の正解で、`public/`に置いたファイルはAstroのビルド処理を通らずそのままコピーされる
- devモードではサイトマップが生成されないとは知らなかった。`npm run dev`でサーバーを起動して`/sitemap-index.xml`にアクセスしても404になり続けた。サイトマップは`npm run build`でのみ生成されるので、確認は必ず`npm run build && ls dist/sitemap*.xml`の後に行う必要があった

SEOのmeta情報も一緒に設定したい場合は[AstroでSEOに必要なmetaタグを設定する方法](/posts/astro-seo-meta-tags)も合わせて対応しておくとSEO対策が一通り揃う。

## よくある質問

**Q: サイトマップが生成されているか確認する方法は？**
`npm run build && ls dist/sitemap*.xml` で確認する。`sitemap-index.xml` と `sitemap-0.xml` の2ファイルが出れば成功。`npm run dev` ではサイトマップは生成されないので必ずビルドして確認する。

**Q: 特定のページをサイトマップから除外したい。**
`filter` オプションで除外できる。例：管理ページや下書きページを除く場合は `sitemap({ filter: (page) => !page.includes('/draft/') })` のように書く。

**Q: Search Consoleでサイトマップが「フェッチできませんでした」になります。**
原因は3つ。(1) `sitemap-index.xml` ではなく `sitemap.xml` と入力した（ファイル名が違う）。(2) Cloudflare Pagesのデプロイがまだ完了していない。(3) `astro.config.mjs` の `site` がlocalhostになっていてURLが正しくない。`dist/sitemap-0.xml` を直接開いてURLがhttps://yourdomain.comで始まっているか確認する。

**Q: robots.txtのSitemapの行は必須ですか？**
必須ではないが設定しておくと検索エンジンがサイトマップを見つけやすくなる。`Sitemap: https://yourdomain.com/sitemap-index.xml` の1行を追加するだけなので設定しておいた方がいい。

---

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
