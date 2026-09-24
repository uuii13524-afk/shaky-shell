---
title: 'Node.jsでrequire()がError [ERR_REQUIRE_ESM]になる原因と解決手順'
date: '2026-09-24'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'CommonJSプロジェクトでnode-fetchをrequire()した際にError [ERR_REQUIRE_ESM]が発生する症状を解説。ESM専用パッケージの見分け方と、動的import・バージョン固定による解決手順を紹介します。'
ja_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'node-fetch']
en_tags: ['Node.js', 'ERR_REQUIRE_ESM', 'node-fetch']
---

## やりたかったこと（症状）

Express製の社内バッチスクリプトに、外部APIを叩く処理を追加することになった。今まで`node-fetch`を使ったことがなかったので、深く考えずに最新版をインストールした。

```bash
npm install node-fetch
```

インストール自体は成功し、`package.json`の依存関係にも`node-fetch`が追加された。そのままいつも通り`require`で読み込んだ。

```js
// fetch-users.js
const fetch = require('node-fetch');

async function main() {
  const res = await fetch('https://api.example.com/users');
  const data = await res.json();
  console.log(data);
}

main();
```

これを`node fetch-users.js`で実行したところ、いきなり例外が投げられて処理が止まった。

```text
node:internal/modules/cjs/loader:1105
    throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
    ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/batch/node_modules/node-fetch/src/index.js from /home/user/batch/fetch-users.js not supported.
Instead change the require of index.js in /home/user/batch/fetch-users.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/batch/fetch-users.js:1:15) {
  code: 'ERR_REQUIRE_ESM'
}
```

`npm install`は何のエラーも出さずに終わっているので、最初は自分の書いたコードのどこかにタイプミスがあるのだと思い込んだ。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 対象パッケージ: node-fetch 3.3.2
- プロジェクト構成: `package.json`に`"type"`フィールドの指定なし（デフォルトでCommonJSとして解釈される）

## 試したこと

まず疑ったのは`require`の書き方だった。分割代入で書けば直るのではと考え、以下のように書き換えてみた。

```js
const { default: fetch } = require('node-fetch');
```

しかし結果は同じで、`Error [ERR_REQUIRE_ESM]`がそのまま出た。分割代入の問題ではなく、`require`という読み込み方式そのものが拒否されていることに気づいた。

次に`node_modules/node-fetch/package.json`の中身を直接確認した。

```bash
cat node_modules/node-fetch/package.json | grep -E '"type"|"exports"|"main"'
```

```text
  "type": "module",
  "exports": "./src/index.js",
  "main": "./src/index.js",
```

ここで`"type": "module"`という記述を見つけた。これがNode.jsに対して「このパッケージはESモジュールとして扱ってほしい」と伝えるフィールドであることは知っていたが、これまで自分が書くコード側でしか意識したことがなかった。依存パッケージ側がESM専用になっているケースがあるということを、このとき初めて実感した。

さらにnode-fetchのリリース履歴を確認すると、v3系でCommonJSサポートが打ち切られ、ESM専用パッケージになっていたことが分かった。手元の`package.json`には`node-fetch`のバージョン指定をしていなかったため、`npm install`時に何も考えずv3系の最新版が入ってしまっていた。

## 原因

確認できた事実は以下の通り。

- `node-fetch`はv3.0.0以降、ESM専用パッケージとなり、CommonJSの`require()`からは読み込めなくなった。
- 手元のプロジェクトは`package.json`に`"type": "module"`を指定していない、つまりCommonJSとして動作している。
- CommonJSのファイルからESM専用パッケージを`require()`すると、Node.jsはモジュール解決の時点でエラーを投げ、実行を止める。これは`import`文への書き換えや、動的`import()`の利用を促す仕様であり、バグではない。

## 解決手順

今回はプロジェクト全体をESMに移行する余裕がなかったため、CommonJSのまま使える`node-fetch@2`系に固定する方針を選んだ。

まず既存のv3系を削除する。

```bash
npm uninstall node-fetch
```

CommonJS対応の最終メジャーバージョンである2系を明示的に指定してインストールする。

```bash
npm install node-fetch@2
```

`package.json`に固定バージョンとして記録されたことを確認する。

```bash
grep node-fetch package.json
```

```text
    "node-fetch": "^2.7.0",
```

コード側は変更せず、そのまま`require('node-fetch')`で動作する。

```js
const fetch = require('node-fetch');
```

なお、将来的にプロジェクト全体をESM化する場合は、`package.json`に`"type": "module"`を追加したうえで、`require`をすべて`import`に書き換える方法もある。今回はバッチスクリプト1本のためにプロジェクト全体の構成を変える判断はせず、依存バージョンの固定で解決した。

もう一つ、今回は使わなかったが知っておくと役立つ方法がある。CommonJSのファイルの中から動的`import()`を使う方法で、実はNode.jsのエラーメッセージ自体がこの方法を示唆している。

```js
async function getFetch() {
  const { default: fetch } = await import('node-fetch');
  return fetch;
}

async function main() {
  const fetch = await getFetch();
  const res = await fetch('https://api.example.com/users');
  const data = await res.json();
  console.log(data);
}

main();
```

`import()`は静的な構文ではなく関数呼び出しなので、CommonJSの中でも合法であり、同期的に例外を投げる代わりにPromiseを返す。大きなCommonJSプロジェクトの中で1〜2箇所だけESM専用パッケージを使いたい、かつプロジェクト全体の移行はしたくない、というケースに向いている。今回はv2系への固定でコードを変えずに済んだため使わなかったが、CJS対応バージョンが古すぎる、あるいは必要な機能がCJS版に無い場合には有効な選択肢になる。

なぜこの種のエラーが増えているのかも合わせて理解しておくと良い。近年、人気のnpmパッケージがメジャーバージョンアップのタイミングでCommonJSサポートを打ち切り、ESM専用として公開するケースが増えている。`node-fetch`はv3で、`chalk`はv5で、`inquirer`はv9でそれぞれESM専用化した。これはパッケージ側のバグではなく、Node.jsが安定してESMをサポートするようになったことを受けた、メンテナ側の意図的な判断である。利用者側への実質的な影響はどのケースも同じで、バージョン指定をせずにこれらの依存を更新すると、自分のコードを一切変更していないのに次回の`npm install`で突然`ERR_REQUIRE_ESM`に遭遇することになる。

## 動作確認

`node-fetch@2`をインストールした状態で、再度スクリプトを実行した。

```bash
node fetch-users.js
```

```text
[
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
]
```

エラーなくAPIレスポンスが取得できることを確認した。念のため`npm ls node-fetch`でもバージョンを確認しておいた。

```bash
npm ls node-fetch
```

```text
batch@1.0.0 /home/user/batch
└── node-fetch@2.7.0
```

## まとめ

- `Error [ERR_REQUIRE_ESM]`は自分のコードのバグではなく、`require()`しようとした対象パッケージがESM専用である場合に発生する。
- 依存パッケージの`node_modules/<パッケージ名>/package.json`で`"type": "module"`や`"exports"`の値を確認すれば、ESM専用かどうかを判別できる。
- CommonJSプロジェクトのままにするならCJS対応バージョンへ固定、プロジェクトごとESM化するなら`import`への書き換えが必要になる。同種のエラーは`chalk`や`inquirer`など、他の人気パッケージがESM専用化した際にも同じ形で発生する。

## 関連記事

- [nvmでNode.jsのバージョンを切り替える手順](/posts/node-version-management-nvm/)
- [npm installでERESOLVEエラーが出たときの原因と解決手順](/posts/npm-eresolve-error/)
- [package.jsonのscriptsフィールドの書き方まとめ](/posts/npm-package-json-scripts/)
- [Node.jsがJavaScript heap out of memoryで落ちる原因と解決手順](/posts/node-heap-out-of-memory/)
- [GitHub ActionsでNode.jsの依存関係をキャッシュする方法](/posts/github-actions-node-cache/)
