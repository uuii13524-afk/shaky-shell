---
title: 'Node.jsで「require is not defined in ES module scope」が出た時の対処法'
date: '2026-08-15'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに"type": "module"を設定した直後、既存の.jsファイルでrequireを呼ぶと「ReferenceError: require is not defined in ES module scope」で落ちる症状を解説。原因の仕組みと、import構文への書き換え・.cjs拡張子・createRequireの3つの解決策を紹介します。'
ja_tags: ['Node.js', 'ESM', 'CommonJS', 'require', 'type module']
en_tags: ['Node.js', 'ESM', 'CommonJS', 'require', 'type module']
---

## やりたかったこと（または「症状」）

トップレベルawaitを使いたくて、自作のビルドスクリプト用の`package.json`に`"type": "module"`を追加した。既存のスクリプト自体は変更していなかったが、その状態で今までどおり`node index.js`を実行したところ、いきなり以下のエラーで落ちた。

```text
file:///home/deploy/scripts/index.js:1
const path = require('path');
             ^

ReferenceError: require is not defined in ES module scope, you can use import instead
This file is being treated as an ES module because it has a '.js' file extension and '/home/deploy/scripts/package.json' contains "type": "module". To treat it as a CommonJS script, rename it to use the '.cjs' file extension.
    at file:///home/deploy/scripts/index.js:1:14
    at ModuleJob.run (node:internal/modules/esm/module_job:343:25)
    at async onImport.tracePromise.__proto__ (node:internal/modules/esm/loader:665:26)
    at async asyncRunEntryPointWithESMLoader (node:internal/modules/run_main:117:5)

Node.js v22.22.2
```

`index.js`のコード自体は1行も触っていないので、最初は`package.json`をどう変更したかとエラーの関連が分からなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象ファイル: 拡張子`.js`のスクリプト（`require`を使うCommonJS形式で記述済み）

## 試したこと

まず、エラーメッセージにある通り`require`を`import`に書き換えれば直るだろうと考えたが、スクリプト内で`require`をいくつも使っており、すぐに全部を書き換えるのは手間だと感じた。そこで一旦`"type": "module"`を`package.json`から削除して様子を見た。

```bash
node index.js
```

```text
a/b
```

これで元通り動くには動いたが、そもそもトップレベルawaitを使いたくて追加した設定なので、これでは目的を達成できていない。次に、`__dirname`も同様のファイルで使っていたことを思い出し、そちらも試しに`"type": "module"`を戻した状態で実行してみた。

```bash
node dirname-test.js
```

```text
file:///home/deploy/scripts/dirname-test.js:1
console.log(__dirname);
            ^

ReferenceError: __dirname is not defined in ES module scope
This file is being treated as an ES module because it has a '.js' file extension and '/home/deploy/scripts/package.json' contains "type": "module".
    at file:///home/deploy/scripts/dirname-test.js:1:13
    at ModuleJob.run (node:internal/modules/esm/module_job:343:25)
    at async onImport.tracePromise.__proto__ (node:internal/modules/esm/loader:665:26)
    at async asyncRunEntryPointWithESMLoader (node:internal/modules/run_main:117:5)

Node.js v22.22.2
```

`require`だけでなく`__dirname`・`__filename`もESMでは使えないと分かり、単発の書き換えでは足りないことに気づいた。

## 原因

`package.json`に`"type": "module"`を設定すると、そのディレクトリ配下にある拡張子`.js`のファイルはすべてCommonJSではなくES Modulesとして解釈されるようになる。CommonJSモジュールでは`require`・`__dirname`・`__filename`・`module`・`exports`がNode.jsによって暗黙に用意されているが、ES Modulesにはこれらのグローバル変数が存在しない。仕様上まったく別のモジュールシステムとして扱われるため、`.js`ファイルの中身を変更していなくても、`package.json`側の`type`フィールドを変えるだけで解釈のされ方自体が変わり、既存のCommonJS構文が軒並みエラーになる。

## 解決方法

状況に応じて次の3つのいずれかを選ぶ。

### 方法1: import構文に書き換える（新規コードや小規模スクリプト向け）

```js
import path from 'path';
console.log(path.join('a', 'b'));
```

```bash
node index2.js
```

```text
a/b
```

`require('path')`を`import path from 'path'`に置き換えるだけで、`"type": "module"`を維持したまま動くようになる。今後もESMで書き続けるつもりなら、これが最もシンプルな対応。

### 方法2: 該当ファイルだけ拡張子を`.cjs`にする（既存コードを触りたくない場合）

```bash
mv index.js index.cjs
node index.cjs
```

```text
a/b
```

拡張子を`.cjs`にすると、`package.json`の`type`設定に関係なくそのファイルは常にCommonJSとして扱われる。`require`や`__dirname`をそのまま使い続けられるため、大量のスクリプトを一度に書き換えたくないときに有効。

### 方法3: createRequireで部分的にrequireを復活させる（CJS専用パッケージが必要な場合）

```js
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const path = require('path');
console.log(path.join('a', 'b'));
```

```bash
node index3.js
```

```text
a/b
```

ESM化した上で、ESM未対応のCommonJS専用パッケージだけ`require`で読み込みたいケースはこれが使える。`__dirname`・`__filename`が必要な場合も同様に、`import.meta.url`から`fileURLToPath`と`path.dirname`で組み立て直す。

```js
import { fileURLToPath } from 'url';
import path from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
console.log(__dirname);
```

```bash
node dirname-fix.js
```

```text
/home/deploy/scripts
```

## ハマったポイント

- `index.js`の中身を一切変更していないのに、`package.json`の`"type": "module"`を足しただけでエラーが出たため、最初は原因の切り分けに時間がかかった。`.js`拡張子の解釈は`package.json`の`type`フィールドで決まるという前提を知らなかった
- `require`のエラーだけ直して満足しかけたが、同じファイルで`__dirname`も使っていたため、修正後に別のReferenceErrorが出てもう一段階の対応が必要だった。CommonJS固有のグローバル変数は`require`以外にも複数あるので、一つ直して終わりと思わない方がよい
- プロジェクト全体を一気にESM化しようとすると、依存しているnpmパッケージの中にCommonJS専用でESMからの`import`に対応していないものが混じっていることがある。その場合は無理に全部`import`化せず、該当パッケージだけ`createRequire`で読み込む方が手戻りが少ない

## よくある質問

**Q: `"type": "module"`を設定しなければこのエラーは起きませんか？**
その通り。`package.json`に`"type"`フィールドがない、または`"commonjs"`を指定している場合、`.js`ファイルは従来どおりCommonJSとして扱われ`require`が使える。トップレベルawaitやESM専用パッケージが必要な場合にのみ`"type": "module"`を検討すればよい。

**Q: ファイルごとに`.js`と`.cjs`を混在させても問題ないですか？**
問題ない。Node.jsは拡張子ごとにモジュールシステムを判定するため、同じプロジェクト内で`.mjs`（常にESM）・`.cjs`（常にCommonJS）・`.js`（`package.json`の`type`に従う）を混在させられる。移行を段階的に進めたい場合は有効な手段。

**Q: TypeScriptを使っている場合も同じ対応が必要ですか？**
`ts-node`や`tsc`のトランスパイル設定（`tsconfig.json`の`module`オプション）によって出力される`.js`の形式が変わるため、コンパイル後の出力先の`package.json`にも同様に`type`フィールドの整合性が必要になる。トランスパイラ側の設定とNode.js側の`package.json`の設定がずれていると、同種のエラーが発生する。

## 関連記事

- [Node.jsでheap out of memoryが出た時の対処法](/posts/node-heap-out-of-memory)
- [Node.jsでEADDRINUSEエラーが出た時の対処法](/posts/node-eaddrinuse-port-fix)
- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
