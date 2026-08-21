---
title: 'Node.js 20でchalkをv5にアップグレードしたらERR_REQUIRE_ESMになる原因と解決手順'
date: '2026-08-21'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'chalkをv5にアップグレードした直後、require("chalk")を呼んでいた既存コードがError [ERR_REQUIRE_ESM]で起動できなくなる症状を解説。package.jsonのexports確認から、動的import()への書き換えまでの解決手順を紹介します。'
ja_tags: ['Node.js', 'ESM', 'ERR_REQUIRE_ESM']
en_tags: ['Node.js', 'ESM', 'ERR_REQUIRE_ESM']
---

## やりたかったこと（症状）

社内のCLIツール`deploy-notifier`で、ターミナル出力に色を付けるために`chalk`を使っていた。依存パッケージの棚卸しで`npm outdated`を実行したところ、`chalk`が`4.1.2`から`5.3.0`にメジャーアップグレードできる状態だったので、他の依存と一緒にまとめて更新した。

```bash
npm install chalk@latest
node bin/deploy-notifier.js --env staging
```

更新前は問題なく動いていたスクリプトが、更新直後にいきなりクラッシュした。

```text
node:internal/modules/cjs/loader:1105
  throw new ERR_REQUIRE_ESM(filename, parentPath, packageJsonPath);
  ^

Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notifier/node_modules/chalk/source/index.js from /home/user/deploy-notifier/bin/deploy-notifier.js not supported.
Instead change the require of index.js in /home/user/deploy-notifier/bin/deploy-notifier.js to a dynamic import() which is available in all CommonJS modules.
    at Object.<anonymous> (/home/user/deploy-notifier/bin/deploy-notifier.js:3:16) {
  code: 'ERR_REQUIRE_ESM'
}

Node.js v20.14.0
```

最初は「`npm install`が中途半端に終わって`node_modules`が壊れたのでは」と疑い、`node_modules`を削除して入れ直した。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v20.14.0
- npm: 10.7.0
- 対象パッケージ: `chalk` 4.1.2 → 5.3.0（アップグレード）
- 呼び出し側: CommonJS形式のスクリプト（`bin/deploy-notifier.js`、`require()`でモジュールを読み込む）

## 試したこと

まず`node_modules`を疑い、クリーンインストールを試した。

```bash
rm -rf node_modules package-lock.json
npm install
node bin/deploy-notifier.js --env staging
```

```text
Error [ERR_REQUIRE_ESM]: require() of ES Module /home/user/deploy-notifier/node_modules/chalk/source/index.js from /home/user/deploy-notifier/bin/deploy-notifier.js not supported.
```

同じエラーが再現した。`node_modules`の破損ではないと分かったので、次に`chalk`のバージョンを疑い、`package.json`の指定を確認した。

```bash
cat package.json | grep chalk
```

```text
    "chalk": "^5.3.0",
```

`npm install chalk@latest`のときに、意図せずメジャーバージョンが上がっていたことに気づいた。ここで`chalk`のリリースノートを確認し、v5系がCommonJSのサポートを打ち切って純粋なESM（ECMAScript Modules）パッケージになっていることが分かった。

念のため、`chalk`の`package.json`の`exports`フィールドも確認した。

```bash
cat node_modules/chalk/package.json | grep -A3 '"exports"'
```

```text
  "exports": {
    "types": "./index.d.ts",
    "default": "./source/index.js"
  },
```

`require`用のCommonJSエントリ（`"require"`キー）が存在せず、`"default"`が`./source/index.js`という`.mjs`相当のESMファイルのみを指している。これで`require("chalk")`自体が原理的に成立しないことを確認した。

## 原因

`chalk`はv5.0.0で純粋なESM専用パッケージに移行した。CommonJSの`require()`はESMモジュールを同期的に読み込む仕組みを持たないため、Node.jsは`require()`でESM専用パッケージを読み込もうとすると`ERR_REQUIRE_ESM`を投げる仕様になっている。

今回のプロジェクトは`package.json`に`"type": "module"`を指定しておらず、`bin/deploy-notifier.js`自体はCommonJSとして解釈される。CommonJSファイルの中で`require("chalk")`を呼ぶと、Node.jsのモジュールローダーが`chalk`側の`exports`にCommonJS用のエントリポイントが存在しないことを検知し、即座にこの例外を送出する。

`npm install chalk@latest`はセマンティックバージョニング上「最新版を入れる」動作をするため、`^4.1.2`のような範囲指定をしていない限りメジャーバージョンの壁を越えてしまう。今回は`npm outdated`の一覧を見ながら手動で最新化した際に、この境界を意識せずに上げてしまったことが直接の引き金だった。

## 解決手順

### 1. バージョン境界を確認する

```bash
npm view chalk versions --json | tail -20
```

```text
  "5.1.2",
  "5.2.0",
  "5.3.0"
]
```

v5系が最新であることを再確認し、CommonJSのまま使い続けるか、ESM対応まで含めて移行するかを判断した。今回はCLIツール全体をESM化するほどの規模ではなかったため、`chalk`だけv4系に固定する方針を選んだ。

### 2. chalkをCommonJS対応の最終メジャーであるv4系に固定する

```bash
npm install chalk@^4.1.2
```

```text
added 1 package, and audited 154 packages in 2s
```

### 3. package.jsonの指定を確認する

```bash
cat package.json | grep chalk
```

```text
    "chalk": "^4.1.2",
```

`^5`を許容しない範囲に固定できていることを確認した。

### 4. 動作確認のため再実行する

```bash
node bin/deploy-notifier.js --env staging
```

```text
[deploy-notifier] staging へのデプロイ通知を送信しました
```

エラーなく起動し、色付き出力も正常に表示された。

## 動作確認

`require`側の解決を再確認するため、Node.jsのREPLで直接ロードして確かめた。

```bash
node -e "console.log(require('chalk').green('OK'))"
```

```text
OK
```

（ターミナル上では緑色で表示される）

エラーなく`chalk`のCommonJSエントリが解決されていることを確認できた。

## まとめ

- `chalk`はv5.0.0以降、CommonJSの`exports`エントリを持たない純粋なESM専用パッケージになっている。`require()`で読み込むプロジェクトは、`^4.1.2`のようにメジャーバージョンを明示して固定する必要がある。
- `ERR_REQUIRE_ESM`が出たら、まず対象パッケージの`node_modules/<package>/package.json`の`exports`フィールドを見て、`"require"`キーがあるかどうかを確認するのが確実な切り分け方法。
- 恒久的にESM専用パッケージへ追従したい場合は、呼び出し側のファイルを`.mjs`に変えるか`package.json`に`"type": "module"`を設定した上で、`require()`を動的`import()`に書き換える必要がある。今回はCLIツール全体をESM化するコストが見合わなかったため、依存側をCommonJS対応バージョンに留める選択をした。

## よくある質問

**Q: `npm install chalk@latest`のようにバージョンを指定せずに更新すると、また同じ問題が起きますか？**
起きます。`@latest`はメジャーバージョンの壁を無視して最新版を入れるため、`package.json`側で`^4.1.2`のように上限を明示していても、コマンドラインから明示的に`@latest`を指定すると上書きされます。範囲固定した後は`npm outdated`で意図せぬメジャー更新がないか確認する習慣が有効です。

**Q: `require()`を`import()`に書き換える以外に、CommonJSのまま使い続ける方法はありますか？**
あります。今回のようにパッケージ側のバージョンをCommonJS対応の最終メジャーに固定する方法が最も手早いです。ただし固定したバージョンにはセキュリティ更新が来なくなるため、長期的にはESM移行を検討する価値があります。

**Q: 他のパッケージでも同じ現象は起きますか？**
起きます。`node-fetch`のv3系や`execa`のv6系など、CommonJS対応を打ち切ってESM専用になった主要パッケージは他にも存在します。アップグレード前に対象パッケージのCHANGELOGで「ESM only」や「Pure ESM package」といった記載がないか確認するとよいです。

## 関連記事

- [Node.jsでheap out of memoryが発生したときの原因と解決手順](/posts/node-heap-out-of-memory)
- [nvmでNode.jsのバージョンを切り替える基本操作](/posts/node-version-management-nvm)
- [npm installでERESOLVEエラーが出たときの原因と解決手順](/posts/npm-eresolve-error)
- [npm cache clearの使いどころと注意点](/posts/npm-cache-clear)
- [package.jsonのscriptsの書き方まとめ](/posts/npm-package-json-scripts)
