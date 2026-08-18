---
title: 'npx pagefindが「403 Forbidden」でビルド失敗、原因はpackage.json未記載のnpx自動インストール'
date: '2026-08-18'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'Astroサイトのビルドで実行しているnpx pagefindが、npmレジストリへの通信が制限された環境で403 Forbiddenを返して失敗する症状を解説。原因はpagefindがpackage.jsonに記載されておらずビルドの度にnpxが自動取得している点にあり、devDependenciesへ固定してローカルバイナリを使う手順で解決します。'
ja_tags: ['Astro', 'npm', 'pagefind']
en_tags: ['Astro', 'npm', 'pagefind']
---

## やりたかったこと（症状）

このブログはAstroで構築しており、`package.json`の`build`スクリプトは以下のようになっている。

```json
"scripts": {
  "build": "astro build && npx pagefind --site dist"
}
```

サイト内検索の索引を作る`pagefind`を、`npx`経由でそのまま実行する形にしていた。ローカルの開発機ではこれまで何の問題もなく動いていたが、ビルドをネットワークアクセスが制限されたサンドボックス環境（npmレジストリ以外への通信を絞った検証用コンテナ）で実行したところ、`astro build`自体は成功するのに、続く`pagefind`のステップだけが失敗するようになった。

```bash
npm run build
```

```text
npm error code E403
npm error 403 403 Forbidden - GET https://registry.invalid/pagefind
npm error 403 In most cases, you or one of your dependencies are requesting
npm error 403 a package version that is forbidden by your security policy, or
npm error 403 on a server you do not have access to.
npm error A complete log of this run can be found in: /root/.npm/_logs/2026-08-18T00_10_16_926Z-debug-0.log
```

`astro build`は265ページ分すべて正常に出力されており、ビルドの本体は壊れていない。にもかかわらず、直後の`pagefind`実行だけがレジストリへの通信を拒否されて止まる、という切り分けにくい失敗だった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: ^6.3.5（`astro build`は成功）
- pagefind: 1.5.2 相当（`npx`経由で毎回取得される版）
- `package.json`の`dependencies`/`devDependencies`に`pagefind`の記載なし

## 試したこと

最初は「npmレジストリへ疎通できていないだけだろう」と考え、`.npmrc`のレジストリ設定を見直した。

```bash
cat .npmrc 2>/dev/null
npm config get registry
```

```text
https://registry.npmjs.org/
```

設定自体は正しい公式レジストリを指しており、`.npmrc`に怪しい上書きは見当たらなかった。次に、`astro build`のときは`node_modules`にインストール済みのパッケージだけで完結しているのに、`pagefind`のステップだけがなぜ外部通信を必要とするのかを確認した。

```bash
grep -n pagefind package.json package-lock.json
```

```text
package.json:    "build": "astro build && npx pagefind --site dist",
```

`package-lock.json`には`pagefind`のエントリが一切なく、`package.json`の`dependencies`にも`devDependencies`にも記載がなかった。つまり`pagefind`は一度も「このプロジェクトの依存関係」としてインストールされたことがなく、`npm run build`を実行するたびに`npx`が都度レジストリへ問い合わせてダウンロードしていた。実際、ネットワーク制限のない通常の開発環境で実行すると、次のような警告が出ていたことに気づいた。

```text
npm warn exec The following package was not found and will be installed: pagefind@1.5.2
```

この`npm warn exec`が出ている時点で、`pagefind`はキャッシュがあれば省略されるものの、キャッシュがない環境（CIのクリーンな実行環境や、今回のような検証用サンドボックス）では毎回ネットワーク経由の取得が必須になる。ここでようやく、通信そのものが失敗しているのではなく、「本来ローカルにあるべきバイナリを、ビルドのたびに外部から取りに行く構成になっている」ことが根本原因だと分かった。

## 原因

`npx <package>`は、対象パッケージが`node_modules`内にローカルインストールされていればそれを使い、なければ実行時に一時的に取得してから実行する仕様になっている。今回の`build`スクリプトは`npx pagefind`という書き方だったため、`pagefind`が`package.json`の依存関係として固定されていない限り、ビルドの度に「npmレジストリへ到達できる」ことが暗黙の前提になっていた。

ローカル開発機やネットワーク制限のないCIではこの前提が常に満たされていたため問題化しなかったが、レジストリ通信が制限・遮断された環境（社内プロキシ経由のビルド基盤、レジストリ許可リストを絞ったCI、オフラインに近いサンドボックスなど）では、`astro build`自体は`node_modules`内で完結して成功するのに、`npx pagefind`だけが403やタイムアウトで失敗するという非対称な壊れ方になる。`pagefind`がバージョン固定もされずに毎回解決される点も、再現性の観点で別のリスクだった。

## 解決手順

`pagefind`を`npx`任せにせず、他の依存パッケージと同様に`devDependencies`へ固定してインストールする。

```bash
npm install --save-dev pagefind@1.5.2
```

`package.json`と`package-lock.json`にエントリが追加されたことを確認する。

```bash
grep -n pagefind package.json package-lock.json | head -5
```

```text
package.json:    "build": "astro build && npx pagefind --site dist",
package.json:    "pagefind": "^1.5.2"
package-lock.json:        "pagefind": "^1.5.2"
package-lock.json:    "node_modules/@pagefind/darwin-arm64": {
```

`node_modules`にローカルインストールされていれば`npx`はレジストリへ問い合わせずローカルバイナリをそのまま実行するため、`build`スクリプトの文言自体は変更しなくても動作する。念のため、`npx`を経由せず`node_modules/.bin`のバイナリを直接呼ぶ形に固定した。

```json
"scripts": {
  "build": "astro build && pagefind --site dist"
}
```

npmスクリプト内の`pagefind`は`PATH`に`node_modules/.bin`が自動で通るため、追加設定なしでローカルバイナリが優先される。

## 動作確認

先ほどと同じくレジストリ通信を遮断した状態で、修正後のビルドを実行した。

```bash
npm_config_registry=https://registry.invalid/ npm run build
```

```text
[build] 265 page(s) built in 7.76s
[build] Complete!
Indexed 265 pages
Indexed 9567 words
Finished in 1.846 seconds
```

レジストリが到達不能な状態でも`astro build`・`pagefind`の両方が正常に完了し、`npm error code E403`は再発しなかった。`package-lock.json`にバージョンが固定されたことで、以後のビルドで`pagefind`のバージョンが意図せず変わることもなくなった。

## ハマったポイント

- `npx <package>`は「ローカルになければ勝手に取ってきてくれる便利機能」だが、裏を返せば「ビルドスクリプトが暗黙にネットワーク依存を持つ」ということでもある。`package.json`に載っていないパッケージを`npx`で呼んでいる箇所は、CI環境が変わった瞬間に壊れるリスクを常に抱えている。
- `astro build`が成功しているログだけを見て「ビルドは通っている」と思い込み、直後の`pagefind`の403を見落としかけた。複数コマンドを`&&`で連結したスクリプトは、どのコマンドがどのエラーを出しているのか一目で分かりにくい。
- ローカル開発機ではnpmのキャッシュが効いていたため、この問題に長らく気づかなかった。キャッシュのないクリーンな環境で一度ビルドを通してみないと顕在化しないタイプの不具合だった。

## よくある質問

**Q: `npx`を使わずに最初から`pagefind`をインストールしておけば防げましたか？**
防げます。今回のように依存パッケージとして`package.json`に固定していれば、`npm install`の時点でネットワークアクセスが完結し、`build`スクリプト自体はオフラインで動作します。

**Q: `npm ci`を使っている場合はどう影響しますか？**
`npm ci`は`package-lock.json`に記載されたパッケージのみを厳密にインストールします。`pagefind`が記載されていない状態では`npm ci`の対象にもならないため、今回のように`npx`実行時に別途取得が発生する構成でした。`devDependencies`へ固定した後は`npm ci`だけで`pagefind`も含めて用意できます。

**Q: 他にも同じ落とし穴になりやすいコマンドはありますか？**
`npx`経由でCIやビルドスクリプトから呼んでいるツールは基本的に同じリスクを持ちます。`package.json`の`dependencies`/`devDependencies`に載っていない`npx`呼び出しがないか、`grep -n "npx " package.json`で棚卸ししておくと安全です。

## 関連記事

- [Astroの記事にSEO用metaタグを追加する方法](/posts/astro-seo-meta-tags)
- [Astroでsitemap.xmlとrobots.txtを設定する方法](/posts/astro-sitemap-robots)
- [npmのERESOLVEエラーの原因と対処法](/posts/npm-eresolve-error)
- [GitHub ActionsでNode.jsの依存関係をキャッシュする方法](/posts/github-actions-node-cache)
- [Cloudflare Pagesのビルドログを確認する方法](/posts/cloudflare-pages-build-log)
