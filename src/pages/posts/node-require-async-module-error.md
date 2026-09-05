---
title: 'requireしたESMパッケージでERR_REQUIRE_ASYNC_MODULEが出る原因と解決手順（Node.js 22）'
date: '2026-09-05'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.js 22でrequire()したESMパッケージが「require() cannot be used on an ESM graph with top-level await」で落ちる症状を解説。原因を切り分け、動的import()に置き換えて解決する手順を紹介します。'
ja_tags: ['Node.js', 'ESM', 'require']
en_tags: ['Node.js', 'ESM', 'require']
---

## やりたかったこと（症状）

社内のビルドスクリプト`build.js`は長らくCommonJS（`require()`）で書かれている。依存している自作の内部ユーティリティパッケージ`async-esm-utils`を、設定値を非同期で取得できるように書き換え、`type: "module"`のESMパッケージとしてバージョンアップした。

```bash
node build.js
```

すると、これまで問題なく動いていた`require()`呼び出しが、いきなり例外を吐くようになった。

```text
node:internal/modules/esm/module_job:450
      throw new ERR_REQUIRE_ASYNC_MODULE(filename, parentFilename);
      ^

Error [ERR_REQUIRE_ASYNC_MODULE]: require() cannot be used on an ESM graph with top-level await. Use import() instead. To see where the top-level await comes from, use --experimental-print-required-tla.
  From /work/esm-repro2/build.js
  Requiring /work/esm-repro2/node_modules/async-esm-utils/index.js
    at ModuleJobSync.runSync (node:internal/modules/esm/module_job:450:13)
    at ModuleLoader.importSyncForRequire (node:internal/modules/esm/loader:435:47)
    at loadESMFromCJS (node:internal/modules/cjs/loader:1536:24)
    at Module._compile (node:internal/modules/cjs/loader:1687:5)
    at Object..js (node:internal/modules/cjs/loader:1838:10)
    at Module.load (node:internal/modules/cjs/loader:1441:32)
    at Function._load (node:internal/modules/cjs/loader:1263:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24)
    at Module.require (node:internal/modules/cjs/loader:1463:12) {
  code: 'ERR_REQUIRE_ASYNC_MODULE'
}
```

紛らわしいのは、同じ`require('async-esm-utils')`という書き方自体は、以前バージョン（トップレベルawaitなし）では何のエラーも出さずに動いていたことだった。Node.jsを18から22に上げたタイミングと重なっていたので、最初はNodeのバージョンアップそのものが原因だと疑った。

## 環境

- OS: Ubuntu 22.04.4（サーバー用ビルドコンテナ）
- Node.js: v22.22.2
- npm: 10.9.7
- 呼び出し元: `build.js`（CommonJS、`require()`使用）
- 依存パッケージ: `async-esm-utils`（自作、`package.json`に`"type": "module"`、`index.js`冒頭にトップレベルawaitあり）

## 試したこと

まず、Node.jsのバージョンを18系に戻せば直るのではと考え、`nvm`で切り替えて同じコードを実行してみた。

```bash
nvm use 18
node build.js
```

```text
Error [ERR_REQUIRE_ESM]: require() of ES Module /work/esm-repro2/node_modules/async-esm-utils/index.js from /work/esm-repro2/build.js not supported.
Instead change the require of index.js in /work/esm-repro2/build.js to a dynamic import() which is available in all CommonJS modules.
```

Node 18では`ERR_REQUIRE_ESM`という別のエラーになった。つまりNode 18では「ESMをrequireすること自体」がそもそもできず、Node 22では逆に「requireは通るケースがある（トップレベルawaitさえなければ）」ことが分かった。ここで、Node 22系がCommonJSからのESM requireを部分的にサポートするようになった一方、非同期のESM（トップレベルawaitあり）は依然としてrequireできない、という仕様の違いに気づいた。

念のため、`async-esm-utils`からトップレベルawaitを取り除いた最小構成でも同じ現象を確認した。

```bash
node -e "console.log(process.version, process.features.require_module)"
```

```text
v22.22.2 [Getter]
```

`process.features.require_module`というgetterが存在すること自体が、Node 22で`require(esm)`機能が有効化されていることの手がかりになった。

エラーメッセージにある`--experimental-print-required-tla`フラグを付けて、どの行がトップレベルawaitと判定されているかも確認した。

```bash
node --experimental-print-required-tla build.js
```

```text
Error: unexpected top-level await at file:///work/esm-repro2/node_modules/async-esm-utils/index.js:1
const config = await Promise.resolve({ env: 'production' });
               ^
```

`index.js`の1行目、`await Promise.resolve(...)`がトップレベルawaitとして検出されていることが明確になった。

## 原因

Node.js 22.12以降、`require()`はCommonJSからESMモジュールを同期的に読み込めるようになった（`require(esm)`機能）。ただし、これは「モジュールの評価が同期的に完結できる場合」に限られる。ESM側にトップレベルawaitが含まれていると、モジュールの評価がPromiseを介した非同期処理になり、`require()`が期待する同期セマンティクスと両立しない。そのため、Node 22はトップレベルawaitを持つESMモジュールに対しては`require()`を拒否し、代わりに非同期の`import()`を使うよう`ERR_REQUIRE_ASYNC_MODULE`で明示的にエラーを返す。

今回のケースでは、`async-esm-utils`のバージョンアップで設定取得処理にトップレベルawaitが追加されたことが直接の原因。Node 18からNode 22へのアップグレード自体はエラーの発生に無関係ではなかったが、根本原因は「Nodeのバージョン」ではなく「requireされる側のESMモジュールがトップレベルawaitを持つようになったこと」だった。

## 解決手順

### 1. 呼び出し元をrequireから動的importに変更する

`build.js`のトップを非同期関数にし、`require()`を`await import()`に置き換えた。

```javascript
// Before
const { getEnv } = require('async-esm-utils');
console.log(getEnv());
```

```javascript
// After
async function main() {
  const { getEnv } = await import('async-esm-utils');
  console.log(getEnv());
}

main();
```

### 2. 動作を確認する

```bash
node build.js
```

```text
production
```

エラーなく、`async-esm-utils`側のトップレベルawaitで取得した設定値`production`が正しく出力された。

### 3. CommonJSのまま維持したい場合の代替案

`build.js`自体をどうしてもCommonJSのまま変えられない場合は、依存パッケージ側でトップレベルawaitを使わない実装（例: 初期化処理を同期関数か、明示的な非同期初期化関数`init()`に分離する）に変更してもらう方法もある。ただし今回は呼び出し元を直しても実害がなかったため、`import()`への置き換えを採用した。

## 動作確認

念のため、Node 18環境でも同じ`build.js`（`import()`版）が動くかを確認した。

```bash
nvm use 18
node build.js
```

```text
production
```

Node 18・Node 22のどちらでも同じ結果になることを確認できた。動的`import()`はCommonJSモジュールからでも常に使えるため、Nodeのバージョンやrequire側の実装差異に影響されない。

## まとめ

- Node.js 22.12以降は`require()`でESMモジュールを読み込めるようになったが、これは同期的に評価できるESMに限られる。
- ESM側にトップレベルawaitがあると、`require()`は`ERR_REQUIRE_ASYNC_MODULE`で明示的に拒否される。エラーメッセージが案内する通り`import()`に置き換えれば解決する。
- 「以前はrequireできていたのに突然エラーになった」場合、Nodeのバージョン差だけでなく、requireされる側の依存パッケージにトップレベルawaitが追加されていないかも合わせて確認するとよい。`--experimental-print-required-tla`フラグで発生源の行を特定できる。

## よくある質問

**Q: `ERR_REQUIRE_ESM`と`ERR_REQUIRE_ASYNC_MODULE`は何が違いますか？**
`ERR_REQUIRE_ESM`はNode 20.19/22.12より前のバージョンで、CommonJSから`require()`でESMを読み込もうとしたときに常に発生するエラーです。`ERR_REQUIRE_ASYNC_MODULE`はNode 22.12以降で`require(esm)`機能が有効になった後も、対象のESMがトップレベルawaitを含み同期評価できない場合にのみ発生します。

**Q: `require(esm)`機能を無効化することはできますか？**
`--no-experimental-require-module`フラグで無効化できます。ただし無効化すると、トップレベルawaitのないESMパッケージのrequireも含めてすべて`ERR_REQUIRE_ESM`に戻るため、根本的な解決にはなりません。

**Q: TypeScriptでコンパイルしている場合も同じ現象は起きますか？**
起きます。トランスパイル後のJavaScriptが`require()`を出力する設定（`module: "commonjs"`など）のままだと、依存パッケージ側がトップレベルawaitを含むESMに変わった時点で同じ`ERR_REQUIRE_ASYNC_MODULE`が発生します。ビルド設定側の`module`ターゲットも合わせて見直す必要があります。

## 関連記事

- [Node.jsでEADDRINUSEエラーが出てポートが使えない原因と解決手順](/posts/node-eaddrinuse-port-fix)
- [npm installでERESOLVEエラーが出る原因と解決手順](/posts/npm-eresolve-error)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [Node.jsのヒープメモリ不足エラーの原因と解決手順](/posts/node-heap-out-of-memory)
- [pm2でNode.jsアプリを常駐させる方法](/posts/node-pm2-setup)
