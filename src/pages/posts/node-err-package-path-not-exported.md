---
title: '社内パッケージにexportsを追加したらERR_PACKAGE_PATH_NOT_EXPORTEDで動かなくなった原因と解決手順'
date: '2026-09-13'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: '社内共通パッケージのpackage.jsonにexportsフィールドを追加した途端、既存のディープインポートがErr [ERR_PACKAGE_PATH_NOT_EXPORTED]で落ちるようになった症状を解説。exportsマップにサブパスを追加して解決するまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'exports', 'モジュール解決']
en_tags: ['Node.js', 'npm', 'exports', 'module resolution']
---

## やりたかったこと（症状）

社内で複数のプロジェクトから使い回している共通ユーティリティパッケージ`@internal/date-utils`に、ESM対応の準備として`package.json`の`exports`フィールドを追加した。公開APIを明示するのが目的で、エントリポイント（`require("@internal/date-utils")`）自体は今まで通り動くはずだと思っていた。

ところが、このパッケージを利用している別リポジトリの`batch-report`プロジェクトで、CIのビルドが突然落ちるようになった。

```bash
npm run build
```

```text
node:internal/modules/cjs/loader:657
      throw e;
      ^

Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './lib/format.js' is not defined by "exports" in /workspace/batch-report/node_modules/@internal/date-utils/package.json
    at exportsNotFound (node:internal/modules/esm/resolve:314:10)
    at packageExportsResolve (node:internal/modules/esm/resolve:661:9)
    at resolveExports (node:internal/modules/cjs/loader:650:36)
    at Function._findPath (node:internal/modules/cjs/loader:717:31)
    at Function._resolveFilename (node:internal/modules/cjs/loader:1369:27)
    at defaultResolveImpl (node:internal/modules/cjs/loader:1025:19)
    at resolveForCJSWithHooks (node:internal/modules/cjs/loader:1030:22)
    at Function._load (node:internal/modules/cjs/loader:1192:37)
    code: 'ERR_PACKAGE_PATH_NOT_EXPORTED'
}
```

`@internal/date-utils`本体には手を入れておらず、`exports`フィールドを追加しただけのつもりだった。エントリポイントのimportは通っていたので、最初はこの`exports`追加が原因だとは思わず、`batch-report`側のnode_modulesが壊れているのだと疑ってしまった。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 社内パッケージ: `@internal/date-utils`（monorepoのローカルパッケージ、`file:`参照で他プロジェクトから利用）
- 利用側プロジェクト: `batch-report`（CommonJS、`require`でモジュールを読み込む構成）

## 試したこと

まず`node_modules`のキャッシュが古いだけではないかと疑い、クリーンインストールを試した。

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

結果は変わらず、同じ`ERR_PACKAGE_PATH_NOT_EXPORTED`で落ちた。これでキャッシュや依存解決の問題ではないと分かった。

次に、実際にどこで`./lib/format.js`を直接読み込んでいるのかを`grep`で洗い出した。

```bash
grep -rn "date-utils/lib/format" src/
```

```text
src/reports/monthly.js:3:const { formatJst } = require("@internal/date-utils/lib/format.js");
src/reports/weekly.js:5:const { formatJst } = require("@internal/date-utils/lib/format.js");
```

公開エントリポイント（`require("@internal/date-utils")`）ではなく、パッケージ内部の`lib/format.js`を直接`require`で指定している箇所が2ファイルにあった。これは以前、公開APIに`formatJst`が含まれていなかった時期に、応急処置として内部ファイルへの直接パスで読み込んだコードだった。

`@internal/date-utils`側の`package.json`を確認すると、案の定こうなっていた。

```json
{
  "name": "@internal/date-utils",
  "version": "2.0.0",
  "main": "index.js",
  "exports": {
    ".": "./index.js"
  }
}
```

`exports`にはエントリポイント`.`しか定義しておらず、`./lib/format.js`のようなサブパスは一切許可していなかった。

## 原因

`package.json`に`exports`フィールドが存在すると、Node.jsのモジュール解決はそこに書かれたパス以外への直接アクセスを一切禁止するようになる。`exports`を追加する前は、`main`フィールドで指定したエントリポイント以外にも、パッケージ内の任意のファイルパスへ`require("pkg/any/internal/file.js")`のようにアクセスできてしまっていた（これは意図された公開APIではなく、Node.jsの解決ルール上たまたま到達できていただけ）。

`exports`フィールドを追加した時点で、この「たまたま到達できていた」経路がすべて塞がれる。今回は`exports`に`"."`（エントリポイント）しか定義していなかったため、`./lib/format.js`のような内部パスへの直接アクセスは`ERR_PACKAGE_PATH_NOT_EXPORTED`として拒否されるようになった。

パッケージ本体の公開APIは変えていないつもりでも、`exports`の追加自体が「今まで通っていた非公式な内部パスへのアクセスを塞ぐ」という破壊的変更になっていた、というのが実態だった。

## 解決手順

### 1. 内部パスへの直接アクセス箇所を洗い出す

```bash
grep -rn "date-utils/lib/" --include="*.js" .
```

```text
src/reports/monthly.js:3:const { formatJst } = require("@internal/date-utils/lib/format.js");
src/reports/weekly.js:5:const { formatJst } = require("@internal/date-utils/lib/format.js");
```

利用箇所が2ファイルだけであることを確認した。

### 2. 恒久対応：公開APIとして再エクスポートする

`@internal/date-utils`の公開APIに`formatJst`が含まれていないこと自体が本来の問題だったので、エントリポイント側で再エクスポートするよう修正した。

```js
// @internal/date-utils/index.js
const { formatJst } = require("./lib/format.js");

module.exports = {
  // 既存のエクスポート...
  formatJst,
};
```

### 3. 利用側のimportをエントリポイント経由に修正する

```js
// 修正前
const { formatJst } = require("@internal/date-utils/lib/format.js");

// 修正後
const { formatJst } = require("@internal/date-utils");
```

`monthly.js`・`weekly.js`の2ファイルを修正した。

### 4. 応急処置として exports にサブパスを追加する場合

すぐに利用側を直せない場合の一時対応として、`exports`にサブパスを明示的に追加する方法もある。

```json
{
  "name": "@internal/date-utils",
  "version": "2.0.1",
  "main": "index.js",
  "exports": {
    ".": "./index.js",
    "./lib/format.js": "./lib/format.js"
  }
}
```

ただしこれは内部実装ファイルを公開APIとして固定してしまうため、今回は根本対応（手順2・3）を採用し、こちらは使わなかった。

### 5. パッケージを再インストールしてビルドを確認する

```bash
npm install
npm run build
```

```text
> batch-report@1.0.0 build
> node scripts/build.js

Build completed successfully.
```

エラーなくビルドが完了した。

## 動作確認

`node -e`で該当モジュールを直接読み込み、エラーが再発しないことを確認した。

```bash
node -e "const { formatJst } = require('@internal/date-utils'); console.log(formatJst(new Date('2026-09-13T00:00:00Z')))"
```

```text
2026-09-13 09:00:00
```

意図した公開APIから`formatJst`が問題なく取得できることを確認できた。念のため他のプロジェクトからの利用箇所も`grep`で再確認し、内部パスへの直接アクセスが残っていないことも確かめた。

```bash
grep -rn "date-utils/lib" --include="*.js" ../*/src 2>/dev/null || echo "内部パスへの直接アクセスなし"
```

```text
内部パスへの直接アクセスなし
```

## まとめ

- `package.json`に`exports`フィールドを追加すると、そこに列挙していないパスへの`require`はすべて`ERR_PACKAGE_PATH_NOT_EXPORTED`で拒否されるようになる。以前は`main`以外の内部ファイルにも直接アクセスできていたが、それはNode.jsの解決ルール上たまたま可能だっただけで、`exports`追加によってその抜け道が塞がれる。
- 本来公開すべきAPIが足りずに内部パスへ直接アクセスしていたコードがある場合、`exports`を追加するタイミングでそれが一斉に壊れる。まず`grep`で内部パスへの直接アクセス箇所を洗い出し、必要な関数はエントリポイント側で正式に再エクスポートするのが恒久対応になる。
- どうしても利用側をすぐ直せない場合は、`exports`にサブパスを明示的に追加することで一時的に動作を維持できるが、内部実装をAPIとして固定してしまう副作用があるため、根本対応への移行を前提にした一時措置と考えるべき。

## よくある質問

**Q: `main`フィールドだけで`exports`がないパッケージでは、この問題は起きませんか？**
起きません。`exports`フィールドが存在しない場合、Node.jsは従来通りパッケージ内の任意のファイルパスへの`require`を許可します。制限がかかるのは`exports`フィールドを定義した時点からです。

**Q: `exports`に`"./*": "./*.js"`のようなワイルドカードを設定すれば回避できますか？**
技術的には可能ですが、それだと`exports`を導入した意味（公開APIを明示し、内部実装への直接依存を防ぐこと）がほぼ失われます。今回のように利用箇所を洗い出して正式なエントリポイント経由に直すほうが、将来の内部リファクタリングの自由度を保てます。

**Q: この問題はCommonJS（`require`）だけの話ですか？ESM（`import`）でも起きますか？**
ESMの`import`でも同様に`ERR_PACKAGE_PATH_NOT_EXPORTED`が発生します。`exports`フィールドはモジュール解決の入り口を制限する仕組みなので、`require`か`import`かに関わらず、列挙されていないサブパスへのアクセスは拒否されます。

## 関連記事

- [npmのERESOLVEエラーの原因と解決方法](/posts/npm-eresolve-error)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
- [package.jsonのscriptsの書き方まとめ](/posts/npm-package-json-scripts)
- [GitHub Actionsでnode_modulesをキャッシュする方法](/posts/github-actions-node-cache)
- [Node.jsの「JavaScript heap out of memory」の原因と解決手順](/posts/node-heap-out-of-memory)
