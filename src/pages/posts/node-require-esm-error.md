---
title: 'Node.js 20でnode-fetchをrequireすると出るError [ERR_REQUIRE_ESM]の原因と解決手順'
date: '2026-08-26'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.js 20でnode-fetchをrequire()すると「Error [ERR_REQUIRE_ESM]」が出てプロセスが即座に落ちる症状を解説。原因パッケージがESM専用に切り替わったことを確認し、dynamic importまたはpackage.jsonのtype変更で解決する手順を紹介します。'
ja_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'CommonJS']
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'CommonJS']
---

## やりたかったこと（症状）

社内の集計バッチ`report-fetcher`に、外部APIから取得したデータをキャッシュに書き込む処理を追加していた。既存コードはCommonJS（`require`ベース）で書かれており、`node-fetch`を新規に追加してHTTPリクエストを実装した。

```bash
npm install node-fetch
```

インストール自体は問題なく終わったが、`node index.js`で実行すると起動直後に例外で落ちた。

```text
node:internal/modules/cjs/loader:1246
  throw err;
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/report-fetcher/node_modules/node-fetch/src/index.js from /home/user/report-fetcher/index.js not supported.
Instead change the require of index.js in /home/user/report-fetcher/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/report-fetcher/index.js:3:20) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

`require('node-fetch')`の1行だけで発生しており、コード側の記述ミスではなさそうだった。最初はnode-fetchのバージョン指定ミスか、`package.json`の依存関係が壊れているのだろうと考え、`node_modules`を消して入れ直したが同じエラーが再現した。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 対象パッケージ: `node-fetch@3.3.2`（`npm install node-fetch`で最新版が入った）
- プロジェクト構成: `package.json`に`"type"`フィールドなし（デフォルトのCommonJS）

## 試したこと

まず`node_modules`と`package-lock.json`を削除し、クリーンインストールを試した。

```bash
rm -rf node_modules package-lock.json
npm install
node index.js
```

結果は変わらず同じ`ERR_REQUIRE_ESM`が出た。次に、依存関係の解決ミスを疑い`npm ls node-fetch`でインストールされたバージョンを確認した。

```bash
npm ls node-fetch
```

```text
report-fetcher@1.0.0 /home/user/report-fetcher
└── node-fetch@3.3.2
```

意図通り`node-fetch`単体がインストールされていることが分かった。バージョンも古いものではない。ここで初めて「バージョンが新しすぎる」方向を疑い、`node-fetch`のリリースノートを確認した。

## 原因

`node-fetch`はv3系から**ESM専用パッケージ**に切り替わっている。`package.json`に`"type": "module"`が指定されておらず、かつ`require()`で読み込もうとしたことが直接の原因だった。

Node.jsのCommonJSモジュールローダーは、読み込み対象のパッケージが`package.json`で`"type": "module"`を宣言している、または拡張子が`.mjs`である場合、そのモジュールをESMとして扱う。ESMは`require()`で同期的に読み込むことができない仕様のため、CommonJS側から`require('node-fetch')`を呼ぶと、ロード処理の途中で`ERR_REQUIRE_ESM`が投げられてプロセスが終了する。

`node-fetch@2.x`まではCommonJS/ESM両対応だったため、依存を書いたときの記憶のまま`require`で使ってしまい、実際にインストールされたのはESM専用のv3系だった、というのが今回の経緯だった。`npm install`はデフォルトで最新のメジャーバージョンを取得するため、過去の記憶や別プロジェクトのコードをそのまま流用すると気づきにくい。

## 解決手順

対処法は大きく2つある。今回はプロジェクト全体をESM化するコストが高かったため、対象ファイルだけdynamic importに変更する方法を採用した。

### 方法1: dynamic import()に置き換える（今回採用）

`require('node-fetch')`をトップレベルの同期呼び出しのまま使うのではなく、関数内で`await import()`を使う形に変更する。

```js
// 変更前
const fetch = require('node-fetch');

async function fetchReport(url) {
  const res = await fetch(url);
  return res.json();
}
```

```js
// 変更後
async function fetchReport(url) {
  const { default: fetch } = await import('node-fetch');
  const res = await fetch(url);
  return res.json();
}
```

`import()`はCommonJSファイルの中でも呼び出せる非同期関数のため、`require`が使えない場面でも利用できる。関数の呼び出し元をすべて`async`にする必要があり、同期関数の内部から呼んでいた箇所は修正が必要だった。

```bash
node index.js
```

```text
[report-fetcher] fetch ok: status=200
[report-fetcher] cache written: ./cache/report.json
```

エラーなく起動し、期待通りキャッシュファイルが生成された。

### 方法2: プロジェクトをESMに切り替える（今回は不採用）

`package.json`に`"type": "module"`を追加し、`require`をすべて`import`文に書き換える方法もある。

```json
{
  "type": "module"
}
```

ただし今回のプロジェクトは他にも複数のCommonJS依存を抱えていたため、影響範囲を絞れるdynamic import方式を選んだ。新規プロジェクトであれば、最初からESM前提で組んだほうが今後同種のエラーを踏みにくい。

### 方法3: CommonJS対応の代替パッケージに変える

`node-fetch`にこだわらないのであれば、Node.js 18以降は標準の`fetch`グローバル関数が使える。外部パッケージを追加せずに済むため、これが一番シンプルな解決策になるケースも多い。

```js
async function fetchReport(url) {
  const res = await fetch(url); // グローバルfetch、requireもimportも不要
  return res.json();
}
```

今回は既存コードとの互換性維持を優先してdynamic import方式を採用したが、新規実装であれば標準`fetch`を使う方法を先に検討する価値がある。

## 動作確認

`node -e`で単体の読み込みテストを行い、ESM専用パッケージであることを改めて確認した。

```bash
node -e "require('node-fetch')"
```

```text
node:internal/modules/cjs/loader:1246
  throw err;
Error [ERR_REQUIRE_ESM]: require() of ES Module ... not supported.
```

`require`では引き続きエラーになることを確認したうえで、修正済みの`fetchReport`関数を実運用のバッチとして5回連続実行し、すべて正常終了することを確認した。

```bash
for i in 1 2 3 4 5; do node index.js; done
```

```text
[report-fetcher] fetch ok: status=200
[report-fetcher] cache written: ./cache/report.json
(5回とも同一の出力)
```

## まとめ

- `Error [ERR_REQUIRE_ESM]`は、ESM専用パッケージを`require()`で読み込もうとしたときに出るNode.js側のエラーで、コードの構文ミスではない。
- `node-fetch`はv3系からESM専用になっている。`npm install`は明示的にバージョンを固定しない限り最新版を取得するため、v2時代の記憶で`require`のまま使うとこのエラーを踏む。
- 解決策は「呼び出し側をdynamic import()にする」「プロジェクト全体をESM化する」「Node.js標準の`fetch`を使う」の3択。既存CommonJSプロジェクトへの影響を小さく抑えたい場合はdynamic importが手軽。同じ`ERR_REQUIRE_ESM`は`chalk`や`execa`など他の人気パッケージがESM専用化した際にも同様に発生するため、パッケージのメジャーアップデート後に見かけたら、まずリリースノートで「ESM専用になっていないか」を確認するとよい。

## 関連記事

- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [npm installで出るERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error)
- [Node.jsでEADDRINUSEエラーが出たときのポート確認と解決手順](/posts/node-eaddrinuse-port-fix)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [package.jsonのscriptsフィールドの書き方](/posts/npm-package-json-scripts)
