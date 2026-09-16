---
title: 'npm ciで「can only install packages when your package.json and package-lock.json...are in sync」が出る原因と解決手順'
date: '2026-09-16'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub Actions上でnpm ciを実行するとEUSAGEエラーでインストールが止まる症状を解説。package.jsonに依存を追加してpackage-lock.jsonを更新し忘れた場合の原因と、npm installでロックファイルを同期させる解決手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

ローカルの検証用リポジトリに軽い依存パッケージを1つ追加しようとした。手元では普段通り`package.json`の`dependencies`にエントリを1行足しただけで、`package-lock.json`は更新しないままコミットしようとしていた。CIと同じ手順を手元でも再現するため、`node_modules`を消してから`npm ci`を叩いた。

```bash
rm -rf node_modules
npm ci
```

すると、インストールが始まる前にエラーで即座に止まった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

普段`npm install`しか使っていないと初見のエラーで、最初は「`node_modules`を消したのがまずかったのか」「npmのバージョンが古いのか」と見当違いの方向を疑ってしまった。

## 環境

- OS: Ubuntu 24.04 LTS（コンテナ環境）
- Node.js: v22.22.2
- npm: 10.9.7
- 依存追加前: `package.json`に`left-pad`のみ記載、`package-lock.json`もそれに整合
- 依存追加後: `package.json`に`is-odd`を追記したが`package-lock.json`は未更新のままcommit予定だった

## 試したこと

まず`npm --version`でバージョンを確認したが、特に古いわけではなかった。

```bash
npm --version
```

```text
10.9.7
```

次に、キャッシュが原因かと疑って`npm cache clean --force`を試したが、結果は変わらなかった。

```bash
npm cache clean --force
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

エラーメッセージ自体は変わらず出続けた。ここでようやくメッセージ本文をきちんと読み返し、「`Missing: is-odd@3.0.1 from lock file`」の行が指しているものが、直前に自分が`package.json`へ手で追記した依存だと気づいた。

## 原因

`npm ci`は`npm install`と違い、`package-lock.json`（または`npm-shrinkwrap.json`）の内容を「唯一の正」として扱い、そこに書かれている通りに`node_modules`を構築するコマンドである。ロックファイルの中身を`package.json`と突き合わせて整合性チェックを行い、少しでも食い違いがあれば**インストールを一切実行せずに即座にエラー終了する**仕様になっている。

今回は`package.json`の`dependencies`に`is-odd`を追記したにもかかわらず、`package-lock.json`はまだ`left-pad`だけの古い状態のままだった。そのため`npm ci`が「ロックファイルに書かれていない依存が要求されている」と判断し、`Missing: is-odd@3.0.1 from lock file`というエラーで停止した。

`npm install`であればこの食い違いを自動的に検出してロックファイルを更新してくれるが、`npm ci`にはその自動修復機能がない。これは意図的な設計で、CI環境でロックファイルの内容が知らないうちに書き換わってしまうことを防ぐためのガードになっている。裏を返せば、「ローカルでは`npm install`で動いていたのにCIの`npm ci`だけ落ちる」という症状のほとんどは、この「ロックファイルの更新忘れ」が原因である可能性が高い。

## 解決手順

### 1. package.jsonの内容を確認する

```bash
cat package.json
```

```json
{
  "name": "npmci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

`is-odd`が追記されていることを確認した。

### 2. npm installでロックファイルを同期させる

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 452ms

found 0 vulnerabilities
```

`is-odd`本体に加えて、その依存である`is-number`も一緒に解決され、`package-lock.json`に反映された。

### 3. 更新されたロックファイルを確認する

```bash
grep -A2 '"is-odd"' package-lock.json
```

`package-lock.json`側に`is-odd`と`is-number`のエントリが追加されていることを確認した。

### 4. npm ciを再実行する

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 457ms

found 0 vulnerabilities
```

今度はエラーなくインストールが完了した。

## 動作確認

`node_modules`が生成されていること、想定通りのパッケージが入っていることを確認した。

```bash
ls node_modules
```

```text
is-number  is-odd  left-pad
```

`package.json`・`package-lock.json`・`node_modules`の3者が一致した状態になり、以降`npm ci`を何度実行してもエラーが出ないことを確認できた。

## まとめ

- `npm ci`は`package.json`と`package-lock.json`の内容が完全に一致していることを前提とするコマンドで、`npm install`のように食い違いを自動修復してはくれない。
- 依存を追記・変更したら、必ず`npm install`を一度実行して`package-lock.json`を最新化してからコミットする。CIで`npm ci`を使っている場合は特に、ロックファイルのコミット漏れがそのままビルド失敗に直結する。
- 「ローカルでは動くのにCIだけ`npm ci`で落ちる」という症状を見たら、まずエラー本文の`Missing: ... from lock file`の行を確認し、そこに書かれているパッケージが`package.json`に追記済みかどうかをチェックするのが早い切り分け方法になる。

## よくある質問

**Q: `npm install`ではなく`npm ci`を使うメリットは何ですか？**
`npm ci`は`package-lock.json`の内容を厳密に再現するため、開発者ごと・CI実行ごとにインストールされるバージョンが微妙にずれる事故を防げます。また既存の`node_modules`を毎回削除してからインストールするため、依存関係が汚れた状態を引きずりにくいという利点もあります。

**Q: package-lock.jsonをgitignoreしてしまっても問題ないですか？**
`npm ci`を使う前提であれば、`package-lock.json`は必ずコミット対象に含める必要があります。ロックファイルがリポジトリに存在しない場合、`npm ci`はそもそも実行できず`The npm ci command can only install with an existing package-lock.json`というエラーになります。

**Q: CI側でこのエラーを未然に防ぐ方法はありますか？**
pre-commitフックやCIの別ジョブで`npm install --package-lock-only`のdry-run的なチェックを入れ、`package-lock.json`に差分が出ないかを確認する運用が有効です。差分が出た時点でCIを落とせば、`npm ci`本番実行の前に気づけます。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npm installで EACCES パーミッションエラーが出た時の対処法](/posts/npm-install-permission-denied)
- [npm cacheのクリア方法まとめ](/posts/npm-cache-clear)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [package.jsonのscriptsの書き方まとめ](/posts/npm-package-json-scripts)
