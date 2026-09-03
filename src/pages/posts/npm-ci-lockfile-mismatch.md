---
title: 'npm ci で「can only install packages when your package.json and package-lock.json ... are in sync」の原因と解決手順'
date: '2026-09-03'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'ローカルではnpm installが通るのに、CI環境のnpm ciだけがEUSAGEエラーで失敗する症状を解説。package.jsonにpackage-lock.jsonが追従していないことが原因で、npm installによるロックファイル再生成で解決するまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

検証用のNode.jsプロジェクトに`is-odd`パッケージを追加する必要があった。急いでいたため`npm install is-odd`を叩かず、`package.json`の`dependencies`に直接一行追記してコミットした。

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

ローカルではこの後も`npm install`が通っていたので気づかなかったが、CIパイプラインの`npm ci`ステップだけが失敗するようになった。

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
npm error
npm error Clean install a project
```

手元では同じ`package.json`を使って`npm install`を実行しても何のエラーも出ないため、最初は「CI環境のnpmキャッシュが壊れているのでは」と疑った。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- パッケージ管理: npm（`package-lock.json`使用）
- CI: `npm ci`でクリーンインストールするジョブ

## 試したこと

まずCI側のキャッシュを疑い、npmキャッシュをクリアしてから再実行した。

```bash
npm cache clean --force
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

キャッシュとは無関係に同じエラーが再現した。次に、`package.json`と`package-lock.json`を実際に見比べてみた。

```bash
grep -A2 '"is-odd"' package.json
grep -m1 '"is-odd"' -A2 package-lock.json
```

```text
"is-odd": "^3.0.1"
```

`package.json`には`is-odd`が存在するが、`package-lock.json`側には該当エントリが1件も出てこなかった。ここでようやく、CI固有の問題ではなく「ロックファイルが`package.json`に追従していない」ことが原因だと分かった。

## 原因

`npm ci`はロックファイルの内容を厳密な設計図として扱い、`package.json`と`package-lock.json`の内容が完全に一致していることを前提にクリーンインストールを行う。今回は`package.json`の`dependencies`に`is-odd`を手動で追記しただけで、`npm install`を一度も実行していなかったため、`package-lock.json`には`is-odd`とその依存先である`is-number`のエントリが一切追加されていなかった。

`npm install`は`package.json`と実際の依存関係の差分を見て、その場でロックファイルを補完しながらインストールを進める。そのため手元では気づかず動いてしまう。一方`npm ci`はこの補完を行わず、差分があれば即座に`EUSAGE`エラーで停止する仕様になっている。CIで`npm ci`を使うのはまさにこの「ロックファイルに書かれていない依存を静かに混入させない」ことが目的なので、今回はその仕組みが正しく機能していたことになる。

## 解決手順

### 1. package.jsonとpackage-lock.jsonの差分を確認する

```bash
grep -A2 '"is-odd"' package.json
grep -m1 '"is-odd"' -A2 package-lock.json
```

`package.json`にだけ存在し、`package-lock.json`に存在しないパッケージがないか確認した。

### 2. npm installでロックファイルを再生成する

```bash
npm install
```

```text
added 2 packages, and audited 4 packages in 403ms

found 0 vulnerabilities
```

`package.json`の内容に合わせて`package-lock.json`が更新され、`is-odd`と依存先の`is-number`のエントリが追加された。

### 3. 更新されたpackage-lock.jsonをコミットする

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with is-odd dependency"
```

ロックファイルの更新だけをコミットに含め、`package.json`の変更と分離しないようにした。

### 4. npm ciで再検証する

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 408ms

found 0 vulnerabilities
```

`EUSAGE`エラーが出ることなくクリーンインストールが完了した。

## 動作確認

`node_modules`配下に追加した依存が正しくインストールされているかを確認した。

```bash
ls node_modules | grep -E "left-pad|is-odd|is-number"
```

```text
is-number
is-odd
left-pad
```

`is-odd`本体とその依存である`is-number`の両方が展開されており、`package-lock.json`の再生成が正しく反映されたことを確認できた。

## まとめ

- `npm ci`は`package.json`と`package-lock.json`の内容が完全一致していることを前提とするため、`package.json`を手動編集しただけでは動かない。
- ローカルの`npm install`は差分を黙って補完してしまうため、ロックファイルのずれに気づきにくい。依存を追加・変更するときは必ず`npm install <パッケージ名>`を使い、`package.json`と`package-lock.json`を同時に更新する。
- 手動編集してしまった場合は`npm install`を一度実行してロックファイルを再生成し、`package.json`と`package-lock.json`をセットでコミットすれば`npm ci`は通るようになる。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmキャッシュのクリア方法（npm cache clean --force）](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [Node.jsのバージョンをnvmで管理する方法（Windows/Mac）](/posts/node-version-management-nvm)
