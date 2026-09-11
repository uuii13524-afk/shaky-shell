---
title: 'Node.jsで Error [ERR_REQUIRE_ESM]: require() of ES Module not supported が出た原因と解決手順'
date: '2026-09-11'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'chalkをv5にアップデートしたらrequire()でERR_REQUIRE_ESMが発生しCLIツールが起動しなくなった症状を解説。ESM専用パッケージの見分け方と、旧バージョン固定・動的import・ESM移行という3つの解決策を紹介します。'
ja_tags: ['Node.js', 'ESM', 'CommonJS', 'ERR_REQUIRE_ESM']
en_tags: ['Node.js', 'ESM', 'CommonJS', 'ERR_REQUIRE_ESM']
---

## やりたかったこと（症状）

社内用の小さなCLIツール（`my-cli-tool`）で、ターミナル出力に色を付けている`chalk`パッケージを最新化しようとした。`package.json`には`"chalk": "^4.1.2"`と書かれていたが、READMEのバッジを見て「もう5系が出てるのか」と思い、深く考えずにアップデートした。

```bash
npm install chalk@latest
```

```text
added 1 package, and audited 43 packages in 1s
```

インストール自体はエラーなく終わったので、そのまま`node index.js`でCLIを起動しようとした。

```bash
node index.js
```

すると、これまで普通に動いていたスクリプトが、いきなり例外を投げて落ちるようになった。

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/my-cli-tool/node_modules/chalk/source/index.js from /home/user/my-cli-tool/index.js not supported.
Instead change the require of index.js in /home/user/my-cli-tool/index.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/my-cli-tool/index.js:1:16) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

`index.js`は1行目で`const chalk = require('chalk');`しているだけで、コード自体は何も変更していない。パッケージを上げただけでrequireが壊れるとは思っていなかったので、最初は`node_modules`の破損を疑った。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 対象パッケージ: `chalk` (`^4.1.2` → `5.3.0`に更新)
- プロジェクト形式: CommonJS（`package.json`に`"type"`フィールドなし）

## 試したこと

まず`node_modules`が壊れているだけだと考え、クリーンインストールを試した。

```bash
rm -rf node_modules package-lock.json
npm install
```

```text
added 43 packages in 2s
```

しかし`node index.js`を再実行しても、まったく同じ`ERR_REQUIRE_ESM`が出た。この時点で「パッケージの中身自体が変わった」ことに気づき、`node_modules/chalk/package.json`を直接確認した。

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

`"type": "module"`という行が目に入った。これまで意識したことがなかったフィールドだったので、Node.jsの公式ドキュメントで意味を調べた。

## 原因

`package.json`の`"type": "module"`は、そのパッケージ内の`.js`ファイルをNode.jsがESM（ECMAScript Modules）として解釈することを示す。`chalk`はv5.0.0でCommonJSからESMへの完全移行を行っており、`require()`で読み込むことをサポートしなくなっていた。

一方、こちらの`my-cli-tool`側の`package.json`には`"type"`フィールドがなく、デフォルトのCommonJSとして動作している。CommonJSモジュールから`require()`でESM専用パッケージを読み込もうとすると、Node.jsはモジュール解決の段階で`ERR_REQUIRE_ESM`を投げて処理を止める。これはNode.js側の仕様であり、`require()`はESMを同期的に読み込む手段を持たないために発生する制約だった。

`npm install`が警告なく成功していたのも混乱の一因だった。npmはパッケージの`type`フィールドの互換性までは検証しないため、依存関係の解決自体は問題なく完了してしまう。エラーが表面化するのは、実際に`require()`が実行されるランタイムのタイミングになる。

## 解決手順

今回は3つの選択肢を比較し、影響範囲が最小の方法を選んだ。

### 1. まず動的importで動くか検証する

Node.jsのエラーメッセージが提案する通り、`require()`を`import()`に置き換えられるか試した。

```js
// index.js（検証用に書き換え）
const chalk = await import('chalk');
console.log(chalk.default.green('OK'));
```

```bash
node index.js
```

```text
file:///home/user/my-cli-tool/index.js:1
const chalk = await import('chalk');
              ^^^^^

SyntaxError: await is only valid in async functions and the top level body of modules
```

トップレベルの`await`はCommonJSファイルでは使えないため、このスクリプト全体を`async function main() {}`で包み直す必要が出てきた。CLIのエントリーポイント1つだけなら現実的だが、`chalk`を呼んでいる箇所が複数ファイルに散らばっていたため、書き換えコストが見合わないと判断した。

### 2. 実用解: chalkをCommonJS対応の最終バージョンに固定する

`chalk`はv4系までがCommonJS対応の最終系統にあたる。ここに固定し直した。

```bash
npm install chalk@4.1.2 --save-exact
```

```text
added 1 package, and audited 43 packages in 1s
```

```bash
grep '"chalk"' package.json
```

```text
"chalk": "4.1.2",
```

`^`を付けずに完全固定したのは、`4.x`系のマイナーアップデートで意図せず挙動が変わるのを避けるためと、今後`npm update`で誤って5系に引き上げられないようにするため。

### 3. 動作確認前に元のrequireへ戻す

検証用に書き換えた`index.js`の1行目を元の`require`に戻した。

```js
const chalk = require('chalk');
console.log(chalk.green('OK'));
```

## 動作確認

```bash
node index.js
```

```text
OK
```

色付き出力を含め、アップデート前と同じ挙動に戻ったことを確認した。念のため`npm ls chalk`でバージョン固定も確認した。

```bash
npm ls chalk
```

```text
my-cli-tool@1.0.0 /home/user/my-cli-tool
└── chalk@4.1.2
```

## まとめ

- `Error [ERR_REQUIRE_ESM]`は、CommonJSの`require()`でESM専用パッケージを読み込もうとした時にNode.jsが投げるエラー。パッケージの中身が壊れたわけではなく、モジュール形式の非互換が原因。
- パッケージが`"type": "module"`に切り替わっていないかは、`node_modules/<パッケージ名>/package.json`を直接見れば確認できる。`npm install`は形式の互換性を検証しないため、警告なく更新されてしまう点に注意が必要。
- 恒久対応は3択：①自分のコードを`async`化して動的`import()`に寄せる、②互換性のある旧メジャーバージョンにピン留めする、③プロジェクト自体を`"type": "module"`にしてESMへ移行する。今回のように呼び出し箇所が散らばっている小規模CLIでは、②が最も手戻りが少なかった。将来的にコード規模が大きくなるなら、③でESM統一しておく方が長期的には楽になる。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [package.jsonのscriptsを使いこなす方法](/posts/npm-package-json-scripts)
- [Node.jsのheap out of memoryエラーを解決する](/posts/node-heap-out-of-memory)
