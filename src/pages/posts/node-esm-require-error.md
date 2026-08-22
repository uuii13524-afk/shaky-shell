---
title: 'requireでESM専用パッケージを読み込むとERR_REQUIRE_ESMになる原因と解決手順'
date: '2026-08-22'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'CommonJS形式のNode.jsプロジェクトでrequire("chalk")を実行するとError [ERR_REQUIRE_ESM]で処理が止まる症状を解説します。ESM専用パッケージの見分け方と、dynamic import()で解決する手順を紹介します。'
ja_tags: ['Node.js', 'ESM', 'require']
en_tags: ['Node.js', 'ESM', 'require']
---

## やりたかったこと（症状）

既存のCLIツール`report-cli`（CommonJS形式、`package.json`に`"type": "module"`の指定なし）に、ターミナル出力を色付けするため`chalk`パッケージを追加した。

```bash
npm install chalk
```

インストール自体は成功した。しかし、既存コードのスタイルに合わせて`require`で読み込んだところ、実行時にエラーで落ちた。

```js
// src/logger.js
const chalk = require('chalk');

console.log(chalk.green('done'));
```

```bash
node src/logger.js
```

```text
node:internal/modules/cjs/loader:1157
  throw err;
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/report-cli/node_modules/chalk/source/index.js from /home/user/report-cli/src/logger.js not supported.
Instead change the require of index.js in /home/user/report-cli/src/logger.js to a dynamic import() which is available in all CommonJS modules.
    at Module._extensions..js (node:internal/modules/cjs/loader:1157:19)
    at Module.load (node:internal/modules/cjs/loader:981:32)
    at Module._load (node:internal/modules/cjs/loader:822:12)
    at Module.require (node:internal/modules/cjs/loader:1005:19)
    at require (node:internal/modules/helpers:102:18)
    at Object.<anonymous> (/home/user/report-cli/src/logger.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}
```

`npm install`は正常終了しているのに、実行時になって初めて落ちる。パッケージが壊れているのかと思い、いったん`chalk`を削除して入れ直したが同じエラーが再発した。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 対象パッケージ: chalk 5.3.0
- プロジェクト形式: CommonJS（`package.json`に`"type"`フィールドなし＝デフォルトのCommonJS）

## 試したこと

まず`node_modules/chalk`が壊れていないか、`package.json`の中身を直接確認した。

```bash
cat node_modules/chalk/package.json
```

```text
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js",
  ...
}
```

`"type": "module"`という記述が目に入った。この時点では意味を深く考えず、バージョンを1つ下げれば直るだろうと予想し、`chalk@4`を試した。

```bash
npm uninstall chalk
npm install chalk@4
node src/logger.js
```

```text
done
```

`chalk@4`では問題なく動いた。つまりパッケージが壊れていたわけではなく、`chalk@5`固有の何かが原因だとここで確定した。改めて`chalk`の`package.json`を見比べると、`chalk@4`には`"type": "module"`が存在せず、`chalk@5`にだけ存在していた。

## 原因

Node.jsは`package.json`の`"type"`フィールドで、そのパッケージをCommonJSとして扱うかESモジュール（ESM）として扱うかを判定する。`"type": "module"`が指定されているパッケージは純粋なESモジュールとして公開されており、CommonJSの`require()`から直接読み込むことができない。

`chalk`は v5.0.0 で全面的にESM専用パッケージへ移行しており（`chalk@4`まではCommonJSに対応していた）、今回のプロジェクトが`npm install chalk`で無条件に最新版（5.3.0）を取得したため、既存のCommonJSコードの`require('chalk')`が構造的に成立しなくなっていた。

エラーメッセージの`Error [ERR_REQUIRE_ESM]`は、Node.jsが「requireしようとしたモジュールがESMだった」ことを検出したときに投げる専用のエラーコードであり、メッセージ内で提案されている通り、`require()`を動的`import()`に置き換えるのが公式に案内されている対処法になる。

## 解決手順

### 1. 対象パッケージがESM専用かどうかを確認する

```bash
cat node_modules/chalk/package.json | grep '"type"'
```

```text
"type": "module",
```

`"type": "module"`があり、かつ`"exports"`にCommonJS向けのエントリ（`require`条件）が存在しないパッケージは、`require()`では読み込めない。

### 2. `require`を動的`import()`に置き換える

呼び出し元の関数を`async`にし、`require`を`await import()`へ変更した。

```js
// src/logger.js
async function main() {
  const { default: chalk } = await import('chalk');
  console.log(chalk.green('done'));
}

main();
```

`import()`はCommonJSファイル内でも使える動的インポート構文で、Promiseを返す。名前付きエクスポートではなくデフォルトエクスポートを使っているパッケージの場合、分割代入で`{ default: chalk }`のように取り出す必要がある点にはまった（最初`const chalk = await import('chalk')`としてしまい、`chalk.green`が`undefined`扱いになった）。

### 3. 動作確認

```bash
node src/logger.js
```

```text
done
```

ターミナル上で緑色の`done`が表示され、正常に動作した。

### 4. 呼び出し元が複数ある場合は初期化を1箇所にまとめる

`logger.js`を複数のファイルから`require`していたため、`import()`をファイルごとに書くと重複読み込みになる。トップレベルで一度だけ`import()`した結果をキャッシュするヘルパーに切り出した。

```js
// src/chalkLoader.js
let chalkPromise;
function getChalk() {
  if (!chalkPromise) {
    chalkPromise = import('chalk').then((m) => m.default);
  }
  return chalkPromise;
}
module.exports = { getChalk };
```

```js
// src/logger.js
const { getChalk } = require('./chalkLoader');

async function main() {
  const chalk = await getChalk();
  console.log(chalk.green('done'));
}

main();
```

## 動作確認

呼び出し元3ファイルすべてから`getChalk()`経由で色付き出力ができることを確認した。

```bash
node src/logger.js
node src/reporter.js
node src/cli.js --check
```

```text
done
report: 12 passed, 0 failed
check: ok
```

いずれも`ERR_REQUIRE_ESM`は再発せず、`chalk`の色付け出力が正しく表示された。

## まとめ

- `Error [ERR_REQUIRE_ESM]`は、CommonJSの`require()`でESM専用パッケージを読み込もうとしたときにNode.jsが出す専用エラー。パッケージが壊れているサインではない。
- 対象パッケージの`package.json`に`"type": "module"`があるかを確認すれば、ESM専用への移行が原因かどうかを素早く切り分けられる。
- CommonJSプロジェクトのまま使い続けたい場合は`require`を`await import()`に置き換える。頻繁に呼ぶ箇所が複数あるなら、初期化結果をキャッシュするヘルパーに切り出すと重複importを避けられる。
- 恒久的にプロジェクト全体をESMへ移行する選択肢もあるが、影響範囲が大きい場合は今回のように該当パッケージだけ動的importに切り替える方が変更を局所化できる。

## よくある質問

**Q: `chalk`のバージョンを4系に固定し続ければ問題は起きませんか？**
起きません。`chalk@4`まではCommonJSにも対応しているため、`require('chalk')`のまま使い続けられます。ただし将来的なセキュリティ修正や新機能はv5以降にしか入らないため、恒久対応としては動的importへの移行を推奨します。

**Q: プロジェクト全体を`"type": "module"`にしてしまえば解決しますか？**
解決しますが影響が大きい変更です。`require`や`module.exports`を使っている既存コードすべてを`import`/`export`構文に書き換える必要があり、他の依存パッケージがCommonJS前提で書かれている場合はそちらで別の問題が出ることがあります。今回のように該当箇所だけ動的importにする方が変更範囲を小さく抑えられます。

**Q: `await import()`をトップレベルで書けないのはなぜですか？**
CommonJSモジュールはトップレベルで`await`を使えないためです（トップレベル`await`はESモジュールのみの機能）。そのため`main()`のような`async`関数でラップして、その中で`await import()`する必要があります。

## 関連記事

- [git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順](/posts/git-submodule-not-initialized/)
- [npmインストール時のERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error/)
- [Node.jsのバージョン管理（nvm）の基本](/posts/node-version-management-nvm/)
- [Node.jsでheap out of memoryが発生したときの対処法](/posts/node-heap-out-of-memory/)
- [npm installでpermission deniedになったときの解決手順](/posts/npm-install-permission-denied/)
