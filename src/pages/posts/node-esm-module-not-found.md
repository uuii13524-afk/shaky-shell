---
title: 'package.jsonにtype: moduleを追加したらERR_MODULE_NOT_FOUNDになる原因と解決手順（Node.js 22）'
date: '2026-09-04'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに"type": "module"を追加後、拡張子なしの相対importでError [ERR_MODULE_NOT_FOUND]が発生。Node.js 22のESMはrequire()と違い拡張子を自動補完しないのが原因で、.js拡張子を明記して解決する手順を紹介します。'
ja_tags: ['Node.js', 'ESM', 'ERR_MODULE_NOT_FOUND']
en_tags: ['Node.js', 'ESM', 'ERR_MODULE_NOT_FOUND']
---

## やりたかったこと（症状）

個人ツールのCLIスクリプトを、これまでのCommonJS（`require`/`exports`）からESM（`import`/`export`）に書き換えていた。手始めに`package.json`に`"type": "module"`を追加し、エントリポイントの`require`を`import`に置き換えた。

```json
{
  "name": "esm-ext-repro",
  "version": "1.0.0",
  "type": "module",
  "main": "index.js"
}
```

```js
import { formatDate } from './lib';

console.log(formatDate(new Date('2026-09-04')));
```

`lib.js`は同じディレクトリに存在しており、CommonJS時代は`require('./lib')`のように拡張子を省略しても何の問題もなく動いていた。今回もそのままの書き方で`node index.js`を実行したところ、次のエラーで即座に落ちた。

```text
node:internal/modules/run_main:123
    triggerUncaughtException(
    ^

Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/path/to/esm-ext/lib' imported from /path/to/esm-ext/index.js
Did you mean to import "./lib.js"?
    at finalizeResolution (node:internal/modules/esm/resolve:275:11)
    at moduleResolve (node:internal/modules/esm/resolve:861:10)
    at defaultResolve (node:internal/modules/esm/resolve:985:11)
    at #cachedDefaultResolve (node:internal/modules/esm/loader:731:20)
    at ModuleLoader.resolve (node:internal/modules/esm/loader:708:38)
    at ModuleLoader.getModuleJobForImport (node:internal/modules/esm/loader:310:38)
    at ModuleJob._link (node:internal/modules/esm/module_job:182:49) {
  code: 'ERR_MODULE_NOT_FOUND',
  url: 'file:///path/to/esm-ext/lib'
}

Node.js v22.22.2
```

`lib.js`は確かにその場所に存在している。ファイル名のタイプミスも見当たらない。`require`から`import`に変えただけで、なぜモジュールが見つからなくなったのか分からず戸惑った。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象ファイル: `package.json`（`"type": "module"`）、`index.js`、`lib.js`（いずれも同一ディレクトリ直下）

## 試したこと

まず`ls`でファイルの存在と名前を再確認した。

```bash
ls -la
```

```text
-rw-r--r-- 1 user user  76 Sep  4 09:00 index.js
-rw-r--r-- 1 user user  98 Sep  4 09:00 lib.js
-rw-r--r-- 1 user user 108 Sep  4 09:00 package.json
```

`lib.js`は確かに存在しており、`index.js`側のimportパス（`./lib`）に打ち間違いもない。次に、念のため同じ`require('./lib')`という書き方をCommonJSのままのプロジェクトで試し、そちらは本当に問題なく動くのかを切り分けた。

```bash
# package.jsonに"type": "module"を付けていない別ディレクトリで検証
node index.js
```

```text
2026-09-04
```

CommonJSの`require('./lib')`は拡張子なしのままエラーなく動作した。つまり「`lib.js`が存在しない」わけではなく、「`import`と`require`で相対パスの解決ルールそのものが違う」ことが疑わしくなった。ここでエラーメッセージを読み直すと、`Did you mean to import "./lib.js"?`という一文がある。Node.js自身が拡張子付きのパスを提案してくれていることに気づいた。

## 原因

Node.jsのCommonJSローダー（`require()`）は、拡張子を省略した相対パスを渡された場合、`.js` → `.json` → `.node`の順に拡張子を補って存在確認を行う独自の解決アルゴリズムを持っている。これは長年のCommonJSの慣習であり、`require('./lib')`と書くだけで`lib.js`が見つかるのはこの補完のおかげだった。

一方、`package.json`に`"type": "module"`を指定してNode.jsのESM（ECMAScript Modules）ローダーを使う場合、相対importの解決はWeb標準の仕様（URL解決）に準拠する。ESMローダーは拡張子の自動補完を行わないため、`import './lib'`と書いてもNode.jsは`./lib`という名前のファイルをそのまま探しにいき、見つからずに`ERR_MODULE_NOT_FOUND`で失敗する。CommonJSからESMに切り替えるということは、モジュール解決の仕組みそのものが変わることを意味しており、単に`require`を`import`に置換するだけでは済まない。

今回のケースでは、拡張子省略の相対importが数カ所に散らばっていたため、`"type": "module"`を追加した瞬間にそれらが一斉にエラーの対象になった。

## 解決手順

### 1. エラーメッセージが提案する拡張子を確認する

```text
Did you mean to import "./lib.js"?
```

Node.jsのESMローダーは、拡張子なしの指定がエラーになった際、同名で拡張子違いのファイルが存在すればこのように候補を提示してくれる。今回はこの提案どおり`.js`を付ければよいと判断した。

### 2. 相対importに拡張子を明記する

```js
import { formatDate } from './lib.js';

console.log(formatDate(new Date('2026-09-04')));
```

`./lib`を`./lib.js`に書き換えた。ESMでは相対パスの拡張子省略が許されないため、ディレクトリ内の相対import・re-exportをすべてこの形式に統一する必要がある。

### 3. 再実行して解決を確認する

```bash
node index.js
```

```text
2026-09-04
```

エラーなく実行でき、`formatDate`関数の結果が正しく出力された。

### 4. 他ファイルの拡張子省略importも洗い出す

```bash
grep -rn "from '\./" --include="*.js" . | grep -v "\.js'"
```

このプロジェクトでは他に拡張子省略のimportは残っていなかったが、複数ファイルに分割されたプロジェクトでは同様の箇所が他にも潜んでいることが多い。`grep`で`from './`から始まり`.js'`で終わっていない行を洗い出し、機械的に潰していくのが確実だった。

## 動作確認

念のため、CommonJSのまま拡張子を省略した場合とESMで拡張子を省略した場合を並べて再実行し、挙動の違いを最終確認した。

```bash
# CommonJS（type未指定）: 拡張子省略でも動く
node cjs-check/index.js
```

```text
2026-09-04
```

```bash
# ESM（"type": "module"）: 拡張子省略はエラー、拡張子ありは成功
node esm-ext/index.js
```

```text
2026-09-04
```

CommonJS側は拡張子省略のままでも動作し続け、ESM側は拡張子を明記した状態でのみ成功することを確認できた。両者の解決ルールが異なるという理解が裏付けられた。

## まとめ

- CommonJSの`require()`は拡張子を自動補完するが、Node.jsのESM（`"type": "module"`）の`import`は補完を行わない。相対importには`.js`などの拡張子を必ず明記する必要がある。
- `ERR_MODULE_NOT_FOUND`のエラーメッセージには`Did you mean to import "./lib.js"?`のように正しいパスの候補が表示されることが多いので、まずそこを確認するのが早い。
- 既存のCommonJSプロジェクトをESMへ移行する際は、`require`から`import`への単純な置換では終わらない。相対importの拡張子省略箇所を`grep`などで洗い出し、事前にすべて明記しておくと同様のエラーを一度に防げる。

## よくある質問

**Q: `.mjs`拡張子を使えば拡張子省略のimportは可能になりますか？**
なりません。`.mjs`拡張子はファイル単位でそのファイルをESMとして扱わせるための指定であり、`package.json`の`"type": "module"`と同様にNode.jsのESMローダーが使われます。ESMローダーである以上、相対importの拡張子省略はどちらの場合でも`ERR_MODULE_NOT_FOUND`になります。

**Q: TypeScriptで書いていて`.ts`ファイルを`import`しているときも同じエラーになりますか？**
`ts-node`や`tsx`などのローダー経由で実行している場合は、それぞれのツールが独自の解決ロジックで拡張子省略を補ってくれることが多く、今回のエラーが出ないケースもあります。ただし`tsc`でコンパイルした`.js`をNode.js本体で直接実行する場合は本記事と同じESMの解決ルールが適用されるため、コンパイル後のimportパスに拡張子が付くよう`tsconfig.json`の設定（`moduleResolution`など）を確認する必要があります。

**Q: `package.json`の`"type": "module"`を外せば元通り拡張子省略で動きますか？**
動きます。`"type": "module"`を削除するか`"type": "commonjs"`に戻せば、そのディレクトリ配下の`.js`ファイルは再びCommonJSとして解決され、`require`の拡張子自動補完も有効に戻ります。ただし`import`/`export`構文はCommonJSでは使えないため、ESMの構文を維持したまま解決ルールだけをCommonJSに戻すことはできません。

## 関連記事

- [nvmでNode.jsのバージョンを管理する方法](/posts/node-version-management-nvm)
- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [Node.jsでheap out of memoryが出た時の対処法](/posts/node-heap-out-of-memory)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [Node.jsアプリをPM2で本番環境に常駐させる方法](/posts/node-pm2-setup)
