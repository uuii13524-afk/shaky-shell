---
title: 'Node.jsで「Error [ERR_REQUIRE_ESM]: require() of ES Module ... not supported」の原因と解決手順'
date: '2026-08-28'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'Node.jsのCommonJSプロジェクトでchalkをrequireすると「Error [ERR_REQUIRE_ESM]」が出て起動できない症状を解説。ESM専用パッケージが原因と分かるまでの切り分けと、importへの移行・バージョン固定という2つの解決手順を紹介します。'
ja_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'ESM', 'CommonJS', 'chalk']
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'ESM', 'CommonJS', 'chalk']
---

## やりたかったこと（症状）

社内向けのデプロイ通知CLIを書いていた。ターミナル出力に色を付けたかったので、定番の`chalk`を追加しようとした。

```bash
npm install chalk
```

`package.json`に`"type"`フィールドは設定していない（＝デフォルトのCommonJSプロジェクト）。既存のスクリプトと同じ書き方で読み込んだ。

```js
// notify.js
const chalk = require('chalk');

console.log(chalk.green('デプロイが完了しました'));
```

```bash
node notify.js
```

これだけのはずが、実行した瞬間に例外で落ちた。

```text
node:internal/modules/cjs/loader:1105
    throw err;
    ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-cli/node_modules/chalk/source/index.js from /home/user/deploy-cli/notify.js not supported.
Instead change the require of index.js in /home/user/deploy-cli/notify.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/deploy-cli/notify.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

`chalk`は数え切れないくらい使ってきたパッケージなので、まず自分のコードのタイポを疑った。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 追加したパッケージ: `chalk` 5.3.0（`npm install chalk`で入る最新版）
- `package.json`: `"type"`フィールドなし（デフォルトのCommonJS）

## 試したこと

まず`require('chalk')`のパスが正しいか、`node_modules/chalk`が存在するかを確認した。

```bash
ls node_modules/chalk
```

```text
license  package.json  readme.md  source
```

ディレクトリは存在しており、パスのタイポではなさそうだった。次に、以前別プロジェクトで書いたコードをコピーして動かしてみたが、同じエラーが再現した。過去に動いていたコードなので、自分のコードではなく`chalk`側の変化を疑い始めた。

```bash
npm ls chalk
```

```text
deploy-cli@1.0.0 /home/user/deploy-cli
└── chalk@5.3.0
```

以前使っていたプロジェクトの`package-lock.json`を見返すと、`chalk@4.1.2`が入っていた。バージョンが4系から5系に上がっていることに気づき、`chalk`本体の`package.json`を確認した。

```bash
cat node_modules/chalk/package.json
```

```json
{
  "name": "chalk",
  "version": "5.3.0",
  "type": "module",
  "exports": "./source/index.js",
  "main": "./source/index.js"
}
```

`"type": "module"`が指定されており、`"main"`が指すエントリファイルもESM形式だった。CommonJS向けの`"exports"`のCJS分岐や`.cjs`ファイルは見当たらない。ここで「`chalk`が5系でESM専用パッケージに変わった」ことが確定した。

## 原因

`chalk`はv5から、CommonJS向けのビルドを提供しない完全ESM専用パッケージになった。Node.jsの`require()`はCommonJSモジュールしか読み込めない仕組みで、対象モジュールの`package.json`に`"type": "module"`と書かれていると、Node.jsはそのモジュールをES Modulesとして扱う。ES Modulesは`require()`で同期的に読み込むことができない（トップレベルでの非同期解決が必要なため）ため、`ERR_REQUIRE_ESM`が発生する。

エラーメッセージ自体が対処法を示唆している。「`require`を動的`import()`に変更しろ」という指示は正確で、CommonJSファイルの中からでも`import()`（Promiseを返す関数形式）でならESM専用パッケージを読み込めることを意味している。逆に言うと、静的な`require('chalk')`のままでは、`chalk`をどんなバージョンに固定しても5系以降は動かない。

## 解決手順

今回は2つの対処法を比較し、プロジェクト全体をESMに寄せる方針にした。

### 方法1（採用）: プロジェクト自体をESMに切り替える

`package.json`に`"type": "module"`を追加し、`require`を`import`に書き換えた。

```json
{
  "name": "deploy-cli",
  "version": "1.0.0",
  "type": "module"
}
```

```js
// notify.js
import chalk from 'chalk';

console.log(chalk.green('デプロイが完了しました'));
```

```bash
node notify.js
```

```text
デプロイが完了しました
```

（実際のターミナルでは緑色で表示される）

他に`require()`していた自作モジュールが3つあったため、それぞれ`module.exports`を`export default`または`export const`に、呼び出し側の`require`を`import`に置き換えて動作確認した。

### 方法2（今回は不採用・記録として）: chalkを4系に固定する

ESMへの移行が難しいプロジェクトなら、CommonJS対応の最終バージョンに固定する方法もある。

```bash
npm install chalk@4
```

```text
+ chalk@4.1.2
```

```js
const chalk = require('chalk'); // chalk@4系ならこのまま動く
console.log(chalk.green('デプロイが完了しました'));
```

この場合、`chalk@4`は2021年で機能追加が止まっており、将来的なセキュリティ修正が入らない可能性がある点に注意が必要。今回のプロジェクトは新規かつ小規模だったため、方法1（ESM移行）を選んだ。

## 動作確認

ESM化後、`require`が残っていないかを確認した。

```bash
grep -rn "require(" *.js
```

```text
（該当なし）
```

念のため`package.json`の`"type"`が反映されているかも確認した。

```bash
node -e "console.log(require('./package.json').type)"
```

```text
module
```

`node notify.js`を複数回実行し、色付きログが安定して出力されることを確認できた。

## まとめ

- Node.jsの`Error [ERR_REQUIRE_ESM]`は、`require()`でESM専用パッケージを読み込もうとしたときに出る。対象モジュールの`package.json`に`"type": "module"`があるかを`cat node_modules/<pkg>/package.json`で確認すれば切り分けられる。
- `chalk`はv5でCommonJSサポートを打ち切ってESM専用になった。同様の変更は`node-fetch`（v3〜）や`nanoid`（v4〜）など他の主要パッケージでも起きているため、「今まで動いていたコードが急に落ちる」ときはまず対象パッケージの`package.json`の`"type"`を疑うとよい。
- 解決策は大きく2つ。プロジェクトをESM化できるなら`"type": "module"`＋`import`に寄せるのが恒久対応。ESM移行が難しい場合は、CommonJS対応の旧バージョンに固定する（`npm install <pkg>@<旧メジャー>`）のが暫定対応になる。

## よくある質問

**Q: 一部のファイルだけESMにして、他はCommonJSのままにできますか？**
できます。`package.json`の`"type": "module"`をプロジェクト全体に設定する代わりに、ESMで書きたいファイルだけ拡張子を`.mjs`にする方法があります。逆にCommonJSのままにしたいファイルは`.cjs`にすれば、`"type"`の設定に関わらずNode.jsが拡張子でモジュール形式を判定してくれます。

**Q: `require()`のままでもESM専用パッケージを使う方法はありますか？**
エラーメッセージにある通り、動的`import()`を使えば読み込めます。ただし`import()`はPromiseを返すため、`require`のように同期的に変数へ代入することはできません。`async`関数の中で`const chalk = (await import('chalk')).default;`のように書く必要があり、CommonJSファイルの構造をある程度変える必要があります。

**Q: 依存パッケージのどれがESM専用に切り替わったか、事前に調べる方法はありますか？**
`npm outdated`で更新可能なパッケージを確認したうえで、更新前に各パッケージのリリースノートやREADMEで「ESM only」「no longer supports require」といった記述を確認するのが確実です。特にメジャーバージョンアップ時は`package.json`の差分（`"type"`や`"exports"`の追加）を`npm view <pkg>@<新バージョン> type`のように事前確認すると事故を防げます。

## 関連記事

- [npm installで依存関係を解決できない「ERESOLVE」エラーの原因と対処法](/posts/npm-eresolve-error)
- [pm2でNode.jsアプリケーションをプロセス管理する方法](/posts/node-pm2-setup)
- [nvmでNode.jsのバージョンを切り替えて管理する方法](/posts/node-version-management-nvm)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [package.jsonのscriptsフィールドの書き方](/posts/npm-package-json-scripts)
