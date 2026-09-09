---
title: 'Node.js 22でrequire()がERR_REQUIRE_ASYNC_MODULEになる原因と解決手順'
date: '2026-09-09'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.js 22でCommonJSのrequire()が社内パッケージの読み込みでErr [ERR_REQUIRE_ASYNC_MODULE]を投げて落ちる症状を解説。requireをdynamic importに置き換えて解決するまでの手順を紹介します。'
ja_tags: ['Node.js', 'ERR_REQUIRE_ASYNC_MODULE', 'ESM']
en_tags: ['Node.js', 'ERR_REQUIRE_ASYNC_MODULE', 'ESM']
---

## やりたかったこと（症状）

社内のバッチ処理スクリプト`report-batch`は昔ながらのCommonJS（`"type": "module"`を持たない）で書かれていて、共通ユーティリティを社内パッケージ`@internal/word-wrap`から`require()`で読み込んでいた。

```js
const { wrap } = require('word-wrap');
console.log(wrap('hello'));
```

ローカルのNode.js 20では何の問題もなく動いていたが、CIランナーのイメージをNode.js 22に上げた直後から、同じコードが例外を吐いて落ちるようになった。

```text
node:internal/modules/esm/module_job:450
      throw new ERR_REQUIRE_ASYNC_MODULE(filename, parentFilename);
      ^

Error [ERR_REQUIRE_ASYNC_MODULE]: require() cannot be used on an ESM graph with top-level await. Use import() instead. To see where the top-level await comes from, use --experimental-print-required-tla.
  From /app/index.js
  Requiring /app/node_modules/word-wrap/index.js
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

依存パッケージ自体は数ヶ月前から変わっていない。「Node.jsのバージョンを上げただけで動かなくなった」という点が最初の手がかりだった。`ERR_REQUIRE_ESM`ならこれまでも何度か見たことがあったが、`ERR_REQUIRE_ASYNC_MODULE`という耳慣れないコードは初めてで、最初は依存パッケージが壊れているのかと疑った。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象パッケージ: `word-wrap`（社内向けにメンテナンスしているESM専用パッケージ、`package.json`に`"type": "module"`を指定）
- 呼び出し元: CommonJSのバッチスクリプト`index.js`（`"type": "module"`なし、`require()`で読み込み）

## 試したこと

まず「依存パッケージが壊れた」という仮説を検証するため、パッケージ側の`package.json`を確認した。

```json
{
  "name": "word-wrap",
  "version": "2.0.0",
  "type": "module",
  "main": "index.js"
}
```

`"type": "module"`が指定されているだけで、特に壊れているようには見えない。次に、パッケージの中身`index.js`を見てみた。

```js
await Promise.resolve();
export function wrap(str) {
  return str;
}
```

ファイルの先頭でトップレベルawaitを使っている。ここで「Node.js 20から22への変化」と「トップレベルawait」という2つの手がかりがつながった。Node.js 22では、CommonJSの`require()`がESMモジュールを同期的に読み込める（require(esm)）機能がデフォルトで有効になっている。そのため、以前はESMを`require()`すると即座に`ERR_REQUIRE_ESM`で弾かれていたのが、Node.js 22ではトップレベルawaitを含まないESMモジュールなら`require()`がそのまま成功するようになっていた。今回のパッケージはトップレベルawaitを含んでいたため、この「同期require」が原則的に不可能で、代わりに`ERR_REQUIRE_ASYNC_MODULE`という別のエラーになった、という流れだった。

原因の当たりをつけるだけでなく、実際にどこでトップレベルawaitが使われているかを特定するため、Node.js自身が案内してくれるデバッグフラグを試した。

```bash
node --experimental-print-required-tla index.js
```

```text
Error: unexpected top-level await at file:///app/node_modules/word-wrap/index.js:1
await Promise.resolve();
^
```

エラーメッセージが指す通りのファイル・行番号でトップレベルawaitが使われていることが、憶測ではなく確認できた。

## 原因

Node.js 22では、CommonJSの`require()`が対象モジュールをESMとして同期的にロードする「require(esm)」という挙動がデフォルトで有効になっている。これにより、これまで`ERR_REQUIRE_ESM`で即座に弾かれていた多くのケース（純粋なESMモジュールをrequireしようとするケース）が、実際にはそのまま動くようになった。

ただし、この同期ロードには根本的な制約がある。`require()`は同期処理である以上、対象モジュールの評価中にPromiseを`await`する（＝非同期の完了を待つ）ことができない。ESMモジュールのトップレベルスコープで`await`が使われている場合、そのモジュールは本質的に非同期にしか評価できない。Node.jsはこれを検知すると、無理にrequireを成功させるのではなく`ERR_REQUIRE_ASYNC_MODULE`を投げて処理を止める。

つまり今回のケースでは、依存パッケージが壊れたわけでも、CI環境が壊れたわけでもなく、「Node.js 22でrequire(esm)が有効になったことで、以前は`ERR_REQUIRE_ESM`として一律に弾かれていたものが、トップレベルawaitの有無で挙動が分岐するようになった」というNode.js本体側の仕様変更が根本原因だった。

## 解決手順

### 1. 呼び出し元をdynamic importに書き換える

`require()`は同期処理なのでトップレベルawaitを含むESMを読み込めないが、`import()`（dynamic import）はPromiseを返す非同期処理なので問題なく読み込める。呼び出し元の関数を`async`にし、`require`を`await import()`に置き換えた。

```js
async function main() {
  const { wrap } = await import('word-wrap');
  console.log(wrap('hello'));
}
main();
```

### 2. 実行して確認する

```bash
node index.js
```

```text
hello
```

例外は発生せず、正常に出力された。

### 3. トップレベルawaitの位置を特定するデバッグ手順を残す

同様のエラーが別の箇所で再発したときのために、原因特定に使った`--experimental-print-required-tla`フラグの使い方をチームのRunbookに残した。

```bash
node --experimental-print-required-tla <エントリーファイル>
```

このフラグを付けて実行すると、`require()`の対象になっているESMモジュールのうち、どのファイルのどの行にトップレベルawaitがあるかを教えてくれる。スタックトレースの`Requiring`行だけでは依存パッケージの入口ファイルしか分からないことが多いため、実際にawaitしている箇所まで特定できるこのフラグは切り分けに有効だった。

## 動作確認

念のため、`require()`のままだと再現することを再確認した上で、`import()`に置き換えた版で問題が起きないことを確認した。

```bash
node index.js
```

```text
hello
```

CI環境（Node.js 22イメージ）でも同じ修正で正常終了することを確認し、パイプラインを復旧した。

## まとめ

- Node.js 22では`require()`がESMモジュールを同期的にロードする「require(esm)」がデフォルトで有効になっており、以前とはエラーの出方が変わっている。
- 対象のESMモジュールがトップレベルawaitを含む場合、`require()`は原理的に対応できず`ERR_REQUIRE_ASYNC_MODULE`で失敗する。依存が壊れたわけでもバージョンが壊れたわけでもなく、Node.js側の仕様として理解する必要がある。
- 解決は「呼び出し元を`await import()`に書き換える」のが最も確実。原因箇所の特定には`node --experimental-print-required-tla`が有効。

## よくある質問

**Q: `ERR_REQUIRE_ESM`と`ERR_REQUIRE_ASYNC_MODULE`は何が違いますか？**
`ERR_REQUIRE_ESM`はrequire(esm)が使えない古いNode.jsで、ESMモジュールをrequireしようとした際に一律で出るエラーです。`ERR_REQUIRE_ASYNC_MODULE`はNode.js 22以降のrequire(esm)環境で、ESMモジュール自体は読み込めるがトップレベルawaitがあるために同期ロードだけができない場合に出る、より限定的なエラーです。

**Q: 自分のプロジェクト自体をESM化すればこの問題は起きませんか？**
起きなくなります。呼び出し元の`package.json`に`"type": "module"`を指定し、`require`を`import`に統一すれば、そもそも同期requireを経由しないため`ERR_REQUIRE_ASYNC_MODULE`は発生しません。ただしプロジェクト全体のESM移行はCommonJS依存の他コードにも影響するため、今回は呼び出し箇所だけをdynamic importに置き換える対処にとどめました。

**Q: Node.jsのバージョンを20に戻せば直りますか？**
直ります。require(esm)の同期ロード自体がNode.js 20時点ではデフォルト無効なため、以前と同じように動作します。ただし根本的な解決にはならず、いずれ22以降へ上げるタイミングで同じ問題が再発するため、今回はrequire側の書き換えを優先しました。

## 関連記事

- [npm installでERESOLVEエラーが出た時の対処法](/posts/npm-eresolve-error)
- [Node.jsのJavaScript heap out of memoryエラーの原因と対策](/posts/node-heap-out-of-memory)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順](/posts/git-submodule-not-initialized)
