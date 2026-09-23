---
title: 'npm ciが「package.jsonとpackage-lock.jsonがsyncしていません」で失敗する原因と解決手順（npm 10.9 / Node.js 22）'
date: '2026-09-23'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに依存関係を追加した直後にnpm ciを実行するとEUSAGEエラーで停止し、package-lock.jsonと同期していないと表示される症状を解説。npm installでロックファイルを更新し、npm ciを通す手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

検証用の小さなNode.jsプロジェクトに、ちょっとした依存パッケージを1つ追加しようとした。手順としては `package.json` の `dependencies` に直接1行追記してから、CI環境と同じ挙動を手元でも確認するために `npm ci` を実行する、というものだった。

```bash
npm ci
```

すると、`node_modules` のインストールが始まる前に赤いエラーで止まった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
npm error
npm error Clean install a project
npm error
npm error Usage:
npm error npm ci
```

普段 `npm install` しか使っていない環境だと見慣れないエラーで、最初は「ロックファイルが壊れているのか」「npmのバージョンが古いのか」を疑った。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Git: 2.43.0
- プロジェクト構成: `package.json` と `package-lock.json` のみのシンプルな検証用プロジェクト（`dependencies` に `left-pad@1.3.0` を1件保持）

## 試したこと

まず、`package-lock.json` そのものが破損しているのではないかと疑い、ファイルの中身をエディタで開いて確認した。JSON構文としては壊れておらず、パースエラーも出ていない。

次に、npmのキャッシュが古いのではないかと考え、キャッシュをクリアしてから再実行した。

```bash
npm cache clean --force
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

キャッシュクリア後もまったく同じ文言のエラーが出た。ここで、エラーメッセージの本文をもう一度落ち着いて読み直した。「in sync」「Missing: is-odd@3.0.1 from lock file」という2行に、実は原因がそのまま書かれていることに気づいた。`is-odd` は自分が直前に `package.json` へ手で追記したパッケージ名だった。

`git diff` で直前の変更差分を確認したところ、案の定 `package.json` だけが変更されており、`package-lock.json` はコミット時のまま更新していなかったことが分かった。

```bash
git diff --stat
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

## 原因

`npm install` は `package.json` の内容を見て、必要に応じて `package-lock.json` を自動的に書き換えながら依存関係を解決してインストールする。一方 `npm ci` は「クリーンインストール専用」のコマンドで、`package-lock.json`（または `npm-shrinkwrap.json`）に記録された内容だけを厳密にそのままインストールする仕様になっている。`package.json` を直接編集して新しい依存パッケージを追記しても、`npm ci` は `package-lock.json` を一切更新しない。そのため、`package.json` には書かれているのに `package-lock.json` には記録されていないパッケージ（今回は `is-odd` とその依存先の `is-number`）が「Missing」として検出され、両ファイルの内容が食い違っている（in syncでない）と判断されてインストールそのものが中断される。

これは意図された安全装置であり、バグではない。`npm ci` はCI環境やチーム開発において「ロックファイルに記録された通りの依存関係を、誰の環境でも寸分違わず再現する」ことを目的に設計されているため、ロックファイルと `package.json` の間に少しでも矛盾があると即座にエラーで止まる。`npm install` のように黙って自動修正することはしない。

## 解決手順

### 1. 現在のロックファイルの状態を確認する

```bash
git diff --stat package.json package-lock.json
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

`package-lock.json`側に差分が出ていないことを確認し、更新が漏れていると確定させた。

### 2. npm installでロックファイルを更新する

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 490ms

found 0 vulnerabilities
```

`npm install` を実行すると、`package.json` に追記した `is-odd@3.0.1` と、その依存先である `is-number@6.0.0` が解決され、`package-lock.json` に書き込まれる。

### 3. package-lock.jsonが更新されたことを確認する

```bash
git diff --stat package.json package-lock.json
```

```text
 package-lock.json | 24 +++++++++++++++++++++---
 package.json      |  1 +
 2 files changed, 22 insertions(+), 3 deletions(-)
```

先ほどは差分が出ていなかった `package-lock.json` にも変更が入っていることを確認できた。

### 4. npm ciを再実行する

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 663ms

found 0 vulnerabilities
```

エラーなく `npm ci` が完了した。

## 動作確認

インストールされたパッケージの一覧を確認し、追加した `is-odd` とその依存先が正しく `node_modules` に展開されていることを確認した。

```bash
npm ls
```

```text
npmci-test@1.0.0
├── is-odd@3.0.1
└── left-pad@1.3.0
```

続けて、`package-lock.json` を更新したコミットを含めた状態でもう一度 `npm ci` が通ることを確認するため、`node_modules` を削除してから再実行した。

```bash
rm -rf node_modules
npm ci
```

```text
added 3 packages, and audited 4 packages in 601ms

found 0 vulnerabilities
```

`node_modules` を作り直しても同じ結果になり、ロックファイルと `package.json` が正しく同期していることが確認できた。

## まとめ

- `npm ci` は `package-lock.json` を一切更新せず、記録された内容をそのまま厳密にインストールするコマンド。`package.json` を手編集した直後に `npm ci` を使うと、ロックファイルとの不一致がすぐにエラーになる。
- エラーメッセージ中の `Missing: <パッケージ名> from lock file` の行に、実際に足りていないパッケージ名がそのまま書かれているので、まずそこを読む。
- 修正手順は単純で、`npm install` を1回実行して `package-lock.json` を更新し、その差分ごとコミットしてから改めて `npm ci` を使えばよい。CI環境でこのエラーが出た場合も、原因はほぼ必ず「ローカルで `package-lock.json` の更新をコミットし忘れている」ことなので、同じ手順で切り分けられる。

## よくある質問

**Q: `npm install` の代わりに `npm ci` を使う理由は何ですか？**
`npm ci` は `package-lock.json` に記録された正確なバージョンだけをインストールするため、開発者ごと・CI環境ごとにインストール結果がぶれない。またインストール前に既存の `node_modules` を削除してからクリーンインストールする点も `npm install` と異なる。

**Q: CIだけで再現し、ローカルでは気づきにくいのはなぜですか？**
多くの開発フローではローカルで `npm install` を使い続けているため、`package.json` を編集してもロックファイルはその場で自動的に更新され、矛盾に気づかないまま作業を続けられてしまう。CIパイプラインで `npm ci` を使って初めて、ロックファイルの更新漏れが表面化する。

**Q: `package-lock.json` の差分だけコミットし忘れることを防ぐ方法はありますか？**
`package.json` を編集した際は必ず `npm install` を実行してから `git status` で `package-lock.json` にも差分が出ているか確認する運用にするとよい。pre-commitフックで両ファイルの変更有無を突き合わせるチェックを入れておくのも有効。

## 関連記事

- [npm installでERESOLVEエラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
