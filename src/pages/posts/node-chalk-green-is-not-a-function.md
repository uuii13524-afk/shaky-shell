---
title: 'Node.js 22で require("chalk") すると chalk.green is not a function になる原因と解決手順'
date: '2026-09-02'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.js 22でrequire("chalk")するとTypeError: chalk.green is not a functionになる症状を解説。requireがESMのnamespaceオブジェクトを返すのが原因で、.defaultで解決する手順を紹介します。'
ja_tags: ['Node.js', 'CommonJS', 'ESM', 'chalk']
en_tags: ['Node.js', 'CommonJS', 'ESM', 'chalk']
---

## やりたかったこと（症状）

既存のCommonJSスクリプトに、ターミナル出力を色付けするため `chalk` を追加しようとした。

```bash
npm install chalk
```

`package.json` は特に手を入れず、`"type": "module"` も指定していない、いつも通りのCommonJSプロジェクトのつもりだった。

```js
// index.js
const chalk = require('chalk');
console.log(chalk.green('Hello, world!'));
```

```bash
node index.js
```

これだけの短いスクリプトで、いきなりTypeErrorが出た。

```text
/tmp/esm-repro/index.js:2
console.log(chalk.green('Hello, world!'));
                  ^

TypeError: chalk.green is not a function
    at Object.<anonymous> (/tmp/esm-repro/index.js:2:19)
    at Module._compile (node:internal/modules/cjs/loader:1705:14)
    at Object..js (node:internal/modules/cjs/loader:1838:10)
    at Module.load (node:internal/modules/cjs/loader:1441:32)
    at Function._load (node:internal/modules/cjs/loader:1263:12)
    at TracingChannel.traceSync (node:diagnostics_channel:328:14)
    at wrapModuleLoad (node:internal/modules/cjs/loader:237:24)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:171:5)
    at node:internal/main/run_main_module:36:49

Node.js v22.22.2
```

「ESM専用パッケージをrequireすると `ERR_REQUIRE_ESM` で落ちる」という話は以前どこかで見た記憶があったので、てっきりその手のエラーだと思い込んだ。しかし実際に出たのはそれとは別の、`require`自体は成功しているのに`chalk.green`が関数として存在しないという、一見つながりの見えないエラーだった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象パッケージ: chalk v6.0.0（`package.json` に `"type": "module"` を持つ、CommonJSエクスポートを提供しないESM専用パッケージ）
- プロジェクト自体は `"type"` フィールドを持たない素のCommonJSプロジェクト

## 試したこと

まず、`ERR_REQUIRE_ESM`が出ているのだと思い込んでいたので、パッケージのバージョンを疑って`chalk`の`package.json`を確認した。

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "6.0.0",
  "type": "module",
  "exports": {
    "types": "./source/index.d.ts",
    "default": "./source/index.js"
  },
  "engines": {
    "node": ">=22"
  }
}
```

たしかにESM専用（`"type": "module"`、CommonJS用の`exports`条件がない）だった。しかし`node index.js`の実行結果を見返すと、`ERR_REQUIRE_ESM`というエラーコードはどこにも出ていない。`require('chalk')`自体はエラーにならず完了していて、`chalk.green`を呼んだ行で初めて`TypeError`になっている。ここで「`require`は通っているのに中身がおかしい」ことに気づいた。

`require('chalk')`が実際に何を返しているのか、Node REPLで直接確認した。

```bash
node -e "const chalk = require('chalk'); console.log(chalk); console.log(Object.keys(chalk));"
```

```text
[Module: null prototype] {
  Chalk: [class Chalk],
  __esModule: true,
  backgroundColorNames: [ 'bgBlack', 'bgRed', ... ],
  chalkStderr: [Function: chalk] createChalk { [Symbol(LEVEL)]: 0 },
  default: [Function: chalk] createChalk { [Symbol(LEVEL)]: 0 },
  foregroundColorNames: [ 'black', 'red', ... ],
  modifierNames: [ 'reset', 'bold', ... ],
  supportsColor: false,
  ...
}
[
  'Chalk',           '__esModule',
  'backgroundColorNames', 'backgroundColors',
  'chalkStderr',      'colorNames',
  'colors',           'default',
  'foregroundColorNames', 'foregroundColors',
  'modifierNames',    'modifiers',
  'supportsColor',    'supportsColorStderr',
  'underlineColorNames'
]
```

`[Module: null prototype]`という表示と`__esModule: true`というプロパティが目に入った。`chalk`本体として呼び出せる関数は、トップレベルの`chalk`ではなく`chalk.default`というキーに入っていた。つまり`require('chalk')`は、ESMの「モジュール名前空間オブジェクト」をそのまま返していて、`import chalk from 'chalk'`をしたときのようにデフォルトエクスポートを自動で取り出してはくれていなかった。

## 原因

Node.js 22系では、CommonJSファイルから`require()`でESM専用パッケージを直接読み込めるネイティブの相互運用機能が既定で有効になっている（`ERR_REQUIRE_ESM`で強制終了していた以前のNode.jsとの大きな違い）。この機能自体は動作したので、`require('chalk')`はエラーにならずに完了した。

ただし、この相互運用が返すのはESMモジュールの名前空間オブジェクトそのものであり、バンドラ（webpackやts-node、Babelなど）が長年提供してきた「CommonJS互換のため`default`エクスポートをトップレベルに引き上げる」という独自の便宜的な変換は行われない。`chalk`のようにデフォルトエクスポートだけを提供するESMパッケージの場合、実際に呼び出し可能な関数は名前空間オブジェクトの`default`プロパティに入ったままになる。

つまり`require('chalk')`は「`chalk`という関数」ではなく「`{ default: chalk関数, __esModule: true, ...その他の名前付きエクスポート }`というオブジェクト」を返していた、というのが実際の原因だった。トップレベルの`chalk.green`は存在しないため、`chalk.green('Hello, world!')`は`TypeError: chalk.green is not a function`になる。

`ERR_REQUIRE_ESM`という以前の知識に引っ張られていたため、「requireできた＝ESM問題は解決している」と誤解し、しばらく`node_modules`の再インストールやNode.jsのバージョン確認など、見当違いの箇所を疑ってしまった。

## 解決手順

### 1. `require`の戻り値からデフォルトエクスポートを取り出す

```js
// index.js
const chalk = require('chalk').default;
console.log(chalk.green('Hello, world!'));
```

`require('chalk')`が返す名前空間オブジェクトの`default`プロパティに、実際に呼び出し可能な`chalk`関数が入っているため、これを明示的に取り出す。

### 2. 実行して確認する

```bash
node index.js
```

```text
Hello, world!
```

（実際の出力は緑色の文字で表示される）

`TypeError`は解消し、期待通りの色付き出力が得られた。

### 3. TypeScriptプロジェクトの場合は`esModuleInterop`の設定も確認する

TypeScriptで書いている場合、`tsconfig.json`の`esModuleInterop: true`と`allowSyntheticDefaultImports: true`を有効にしておくと、`import chalk from 'chalk'`という書き方でコンパイル後のコードが自動的に`.default`を扱ってくれるようになる。素の`require`を直接書いている場合はこの恩恵を受けられないため、手動で`.default`を付ける必要がある。

## 動作確認

`.default`を付けた状態と付けない状態を並べて、挙動の違いを再確認した。

```bash
node -e "const chalk = require('chalk'); console.log(typeof chalk.green);"
```

```text
undefined
```

```bash
node -e "const chalk = require('chalk').default; console.log(typeof chalk.green);"
```

```text
function
```

`require('chalk')`単体では`chalk.green`が`undefined`になっている一方、`.default`を付けると`function`として認識されることを確認できた。原因の切り分けが正しかったことがこれで裏付けられた。

## まとめ

- Node.js 22系はCommonJSから`require()`でESM専用パッケージを直接読み込めるが、これは以前の`ERR_REQUIRE_ESM`とは別の挙動であり、混同しやすい。
- このネイティブの相互運用は、バンドラのCommonJS互換変換とは異なり、ESMの名前空間オブジェクトをそのまま返す。デフォルトエクスポートは自動で引き上げられず、`require('pkg').default`のように明示的に取り出す必要がある。
- 同様の症状（`require`はエラーにならないのに、プロパティが`undefined`や`is not a function`になる）を見たら、まず`console.log(Object.keys(require('pkg')))`でオブジェクトの中身を確認し、`__esModule`や`default`キーの有無を見るのが早い切り分け方法。

## よくある質問

**Q: すべてのESM専用パッケージで同じ現象が起きますか？**
デフォルトエクスポートのみを提供するパッケージ（`chalk`など）で顕著に起きます。名前付きエクスポートだけを使う場合（`const { someFunction } = require('pkg')`のような書き方）は、名前空間オブジェクトのプロパティとしてそのままアクセスできるため、この問題には遭遇しません。

**Q: プロジェクト自体を`"type": "module"`にして`import`文で書き直す方が根本的な解決になりますか？**
はい、可能であればそちらが推奨されます。`import chalk from 'chalk'`と書けばデフォルトエクスポートが正しく取り出されるため、`.default`を意識する必要がなくなります。ただし既存のCommonJSプロジェクト全体をESMに移行するのは影響範囲が大きいため、影響を最小限にしたい場合は該当箇所だけ`.default`で対処するのが現実的です。

**Q: `ERR_REQUIRE_ESM`が出る場合との違いは何ですか？**
`ERR_REQUIRE_ESM`は、Node.jsのバージョンやフラグの設定によってネイティブのrequire-ESM相互運用が無効な環境で、CommonJSからESM専用パッケージをrequireしようとしたときに発生します。今回のケースはNode.js 22でこの相互運用自体が有効だったため`require`は成功し、その先の「戻り値の形」でつまずいた点が異なります。

## 関連記事

- [npm installでERESOLVEエラーが出た時の対処法](/posts/npm-eresolve-error)
- [Node.jsのバージョン管理（nvm）の使い方](/posts/node-version-management-nvm)
- [Node.jsでEADDRINUSEエラーが出てポートが使えない時の対処法](/posts/node-eaddrinuse-port-fix)
- [Node.jsでheap out of memoryが出た時の対処法](/posts/node-heap-out-of-memory)

## スキルアップにおすすめ
エラーを自力で解決できる力を身につけたい方に。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+7N2A9E+529E+5YJRM" rel="nofollow">資格と仕事に強い！個人レッスンのプログラミングスクール【Winスクール】</a><img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=4B3VRB+7N2A9E+529E+5YJRM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" rel="nofollow">未経験から3ヶ月でプロライターの思考力を習得</a><img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" alt="">

## スキルアップにおすすめ
エラーを自力で解決できる力を身につけたい方に。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+7N2A9E+529E+5YJRM" rel="nofollow">資格と仕事に強い！個人レッスンのプログラミングスクール【Winスクール】</a><img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=4B3VRB+7N2A9E+529E+5YJRM" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" rel="nofollow">未経験から3ヶ月でプロライターの思考力を習得</a><img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" alt="">
