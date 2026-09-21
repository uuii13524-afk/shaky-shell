---
title: 'chalkをrequireすると Error [ERR_REQUIRE_ESM] が出る原因と解決手順'
date: '2026-09-21'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.jsでchalkなどESM専用パッケージをrequireすると Error [ERR_REQUIRE_ESM] が発生し起動できなくなる症状を解説。dynamic importへの書き換えとバージョン固定、それぞれの解決手順を紹介します。'
ja_tags: ['Node.js', 'ESM', 'CommonJS']
en_tags: ['Node.js', 'ESM', 'CommonJS']
---

## やりたかったこと（症状）

社内のCLIツール`deploy-notify`のログ出力を色付けするために、以前から使っていた`chalk`を更新しようとした。

```bash
npm install chalk@latest
node index.js
```

`npm install`自体はエラーなく終わったが、`node index.js`を実行した瞬間に例外で落ちた。

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, true, hint);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notify/node_modules/chalk/source/index.js from /home/user/deploy-notify/index.js not supported.
Instead change the require of index.js in /home/user/deploy-notify/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.Module._extensions..js (node:internal/modules/cjs/loader:1105:13)
    at Module.load (node:internal/modules/cjs/loader:981:32)
    at Function.Module._load (node:internal/modules/cjs/loader:822:12)
    at Module.require (node:internal/modules/cjs/loader:1005:19)
    at require (node:internal/modules/helpers:102:18)
    at Object.<anonymous> (/home/user/deploy-notify/index.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v18.18.0
```

昨日までは`chalk@4.1.2`で普通に動いていたコードで、`require('chalk')`の1行しか触っていない。バージョンを上げただけでここまで壊れるとは思わず、最初は`node_modules`の破損を疑った。

## 環境

- OS: Ubuntu 22.04 LTS
- Node.js: v18.18.0
- npm: 9.8.1
- プロジェクトの`package.json`: `"type"`フィールドなし（＝デフォルトでCommonJS扱い）
- 該当パッケージ: `chalk`（更新前 4.1.2 → 更新後 5.3.0）

## 試したこと

まず疑ったのは`node_modules`の破損だったので、クリーンインストールを試した。

```bash
rm -rf node_modules package-lock.json
npm install
node index.js
```

結果は同じエラー。ここで初めて`node_modules`の問題ではないと分かった。

次に`node_modules/chalk/package.json`を直接確認した。

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js"
}
```

`"type": "module"`という記述が目に入った。これがCommonJSの`require()`と噛み合っていない予感がした。

念のため`require('chalk')`を`import chalk from 'chalk'`に単純に書き換えても試したが、プロジェクトの`package.json`に`"type": "module"`がないため、今度は別のエラーが出た。

```text
SyntaxError: Cannot use import statement outside a module
```

書き換え方向は合っていそうだが、プロジェクト全体の設定と噛み合っていないと分かった。

## 原因

`chalk`はv5から純粋なESM（ECMAScript Modules）専用パッケージになり、CommonJSの`require()`をサポートしなくなった。パッケージの`package.json`に`"type": "module"`が指定されている場合、Node.jsはそのパッケージ内のすべての`.js`ファイルをESMとして読み込む。

一方で、`require()`はCommonJSの仕組みであり、同期的にモジュールを解決する。ESMは非同期でロードされる仕様のため、CommonJSの`require()`からESM専用パッケージを同期的に読み込むことは構造的にできない。Node.jsはこれを検知すると`ERR_REQUIRE_ESM`を投げて、代わりに`import()`（dynamic import）を使うよう案内する。

今回のプロジェクトは`package.json`に`"type"`フィールドがなく、デフォルトでCommonJSとして扱われていた。そこへ`chalk@latest`（5.x系）を入れたことで、CommonJSのコードからESM専用パッケージを`require`する組み合わせになり、エラーが発生していた。`chalk@4`まではCommonJS/ESM両対応（デュアルパッケージ）だったため気づかなかっただけで、v5への更新が引き金だった。

## 解決手順

状況に応じて2つの対処法がある。今回のCLIツールでは方法1を採用した。

### 方法1: chalkをCommonJS対応の最終バージョンに固定する

プロジェクト全体をESM化する余裕がない場合、こちらが現実的。

```bash
npm install chalk@4
```

```text
added 1 package, and audited 45 packages in 1s
```

```bash
node index.js
```

```text
[deploy-notify] デプロイを開始します
```

`require('chalk')`のコードを一切変更せずにエラーが解消した。`chalk@4.1.2`はCommonJSでも動作する最後の系列で、`package.json`を見ると`"type"`フィールド自体が存在しない。

```bash
cat node_modules/chalk/package.json | grep '"version"\|"type"'
```

```text
"version": "4.1.2",
```

### 方法2: dynamic importでESM版を読み込む（最新版を使い続けたい場合）

最新のchalkの機能が必要な場合は、`require`をトップレベルの`async`関数でラップして`import()`を使う。

```js
async function main() {
  const chalk = (await import('chalk')).default;
  console.log(chalk.green('デプロイを開始します'));
}

main();
```

トップレベルで直接`await import('chalk')`と書くと`SyntaxError`になる点に注意する。CommonJSのモジュールにはトップレベルawaitがないため、必ず`async`関数の中に入れる必要がある。

```bash
node index.js
```

```text
[deploy-notify] デプロイを開始します
```

こちらもエラーなく実行できた。

## 動作確認

方法1（`chalk@4`固定）を採用したので、`package.json`の依存関係が意図通りになっているか最終確認した。

```bash
npm ls chalk
```

```text
deploy-notify@1.0.0 /home/user/deploy-notify
└── chalk@4.1.2
```

`^4.1.2`で固定され、`npm update`で誤って5系に上がらないようバージョン範囲も見直した。

```json
{
  "dependencies": {
    "chalk": "^4.1.2"
  }
}
```

## まとめ

- `ERR_REQUIRE_ESM`は「CommonJSの`require()`からESM専用パッケージを読み込もうとした」ことを示すエラー。パッケージ側の`package.json`に`"type": "module"`があるかを確認すれば切り分けられる。
- 根本原因はNode_modulesの破損ではなく、依存パッケージのメジャーアップデートでCommonJS対応が切られたこと。`npm install <pkg>@latest`のような操作は、パッケージ自体のモジュール形式が変わっていないか`package.json`の`"type"`を確認してから行うと事故を防げる。
- 対処は「CommonJSを維持するなら旧バージョンに固定」「最新版を使うならプロジェクトをESM化するか`async`関数内で`dynamic import()`」の二択。プロジェクト全体をESM化する余裕がないなら、まずはバージョン固定が手早い。
- 同種のエラーは`chalk`以外にも`node-fetch`・`execa`・`ora`など、ESM移行した人気パッケージで同様に起こる。エラーメッセージに`ERR_REQUIRE_ESM`と出たら、まず該当パッケージの`package.json`を疑うとよい。

## よくある質問

**Q: プロジェクト全体を`"type": "module"`にしてESM化すれば解決しますか？**
解決しますが、影響範囲が広い。`require`や`module.exports`を全て`import`/`export`に書き換える必要があり、`__dirname`や`__filename`のようなCommonJS固有のグローバル変数も使えなくなる。既存コードが大きい場合は、まず方法1（バージョン固定）で止血してから、計画的にESM移行するほうが安全。

**Q: `npm install chalk@4`のように特定バージョンに固定したら、脆弱性対応の更新が受けられなくなりませんか？**
`4.x`系もセキュリティ修正が入るパッチバージョンはリリースされているため、`^4.1.2`のようなキャレット範囲で固定すれば4系内でのパッチ更新は受けられる。5系へのメジャーアップデートだけを避ける形になる。

**Q: `require()`の中で直接`await import()`と書けないのはなぜですか？**
CommonJSモジュールはトップレベルでの`await`をサポートしていないため。ESMではトップレベルawaitが可能だが、CommonJSでは`await`は`async`関数の内部でしか使えない。そのため`dynamic import()`を使う場合は、必ず`async`関数でラップする必要がある。

## 関連記事

- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [npm ERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error)
- [pm2でNode.jsアプリをデーモン化する方法](/posts/node-pm2-setup)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [Node.jsでheap out of memoryエラーが出た時の対処法](/posts/node-heap-out-of-memory)
