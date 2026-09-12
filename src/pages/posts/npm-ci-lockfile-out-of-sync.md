---
title: 'npm ciで「in sync」エラーが出てGitHub Actionsが落ちる原因と解決手順'
date: '2026-09-12'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub ActionsでのCI実行時にnpm ciがEUSAGEエラーで失敗する症状を解説。package.jsonにだけ依存パッケージを追記しpackage-lock.jsonを更新し忘れたことが原因で、npm installでロックファイルを再生成して解決する手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

個人開発しているツールに、日付フォーマット用のライブラリ`dayjs`を追加しようとした。ローカルではまだ`npm install dayjs`を実行しておらず、`package.json`の`dependencies`に直接1行追記しただけの状態でコミットしてしまった。

```json
{
  "name": "npmci-repro",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "lodash": "^4.17.21",
    "dayjs": "^1.11.10"
  }
}
```

その状態でpushしたところ、GitHub Actions側のCIが依存インストールの段階で失敗した。CI側のワークフローは再現性を優先して`npm install`ではなく`npm ci`を使っている。

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

ローカルでは`npm run build`まで問題なく動いていたので、最初は「CI環境固有の問題」だと思い込み、Node.jsのバージョン差やキャッシュのせいを疑った。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 実行コマンド: `npm ci`（GitHub ActionsのCIジョブ内、および手元でのローカル再現）
- package.json: `dependencies`に`dayjs`を手動追記済み、`package-lock.json`は追記前の状態のまま

## 試したこと

まずCIのNode.jsバージョンを疑い、`actions/setup-node`のバージョン指定をローカルの`v22.22.2`に合わせてみたが、エラーメッセージは変わらなかった。

次に「キャッシュが古いのでは」と考え、GitHub Actions側のnpmキャッシュキーを変更して再実行してみたが、これも同じ`EUSAGE`エラーで失敗した。

ここでようやく、ローカルの`node_modules`を消してから`npm ci`を手元で再現させてみた。

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

CI固有の問題ではなく、手元でも確実に再現することがここで分かった。エラー本文をよく読むと、「`package.json`と`package-lock.json`が同期していない」「`dayjs@1.11.23`がロックファイルから欠落している」と、原因そのものが明記されていた。

## 原因

`npm ci`は`npm install`と違い、`package-lock.json`の内容を**そのまま**信頼してインストールを行うコマンドである。`package.json`の内容とロックファイルの内容に食い違いがあっても自動で解決や更新はせず、食い違いを検知した時点で即座に`EUSAGE`エラーで停止する仕様になっている。

今回のケースでは、`package.json`の`dependencies`に`dayjs`を手で追記しただけで、`npm install`（または`npm install dayjs`）を一度も実行していなかった。そのため`package-lock.json`には`dayjs`のエントリが一切存在せず、`npm ci`が「ロックファイルに書かれている内容と`package.json`が一致しない」と判断してインストールを拒否していた。

`npm install`はロックファイルとの差分を検知すると自動的にロックファイルを更新してくれるため、ローカルで`npm run build`を試したときは（`npm install`を経由していれば）問題が表面化しなかった可能性が高い。一方でCIは再現性を保証するために意図的に`npm ci`を使っており、この仕様の違いが今回の食い違いを顕在化させた。

## 解決手順

### 1. ロックファイルとpackage.jsonの状態を確認する

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

エラー文中の`Missing: dayjs@1.11.23 from lock file`から、不足しているパッケージを特定した。

### 2. npm installでロックファイルを再生成する

```bash
npm install
```

```text
added 2 packages, and audited 3 packages in 755ms

found 0 vulnerabilities
```

このコマンドで`package-lock.json`に`dayjs`とその依存パッケージのエントリが追加される。

### 3. package-lock.jsonの差分を確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
1
```

`dayjs`のエントリが`package-lock.json`に追加されたことを確認した。

### 4. package-lock.jsonをコミットに含める

```bash
git add package.json package-lock.json
git commit -m "add: dayjs dependency"
git push
```

`package.json`だけをコミットして`package-lock.json`を含め忘れるのが今回の根本原因だったため、両方を必ずセットでコミットする。

### 5. npm ciで再現しないことを確認する

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 535ms

found 0 vulnerabilities
```

`EUSAGE`エラーは出ず、正常にインストールが完了した。

## 動作確認

修正後にpushし直し、GitHub Actions側のCIログでも依存インストールのステップが成功していることを確認した。ローカルでも`rm -rf node_modules && npm ci`を再実行し、エラーが再現しないことを再確認済み。

## まとめ

- `npm ci`は`package.json`と`package-lock.json`の内容が完全に一致していることを前提とするコマンドで、食い違いがあると自動修復せずに`EUSAGE`エラーで止まる。
- `package.json`に依存を手で書き足しただけで`npm install`を実行し忘れると、`package-lock.json`が古いままになりこのエラーを引き起こす。エラー文中の`Missing: <パッケージ名>@<バージョン> from lock file`が原因特定の手がかりになる。
- 依存を追加・変更したら必ず`npm install`を実行し、`package.json`と`package-lock.json`をセットでコミットする。CIで`npm ci`を使っている場合は、pushする前に`rm -rf node_modules && npm ci`をローカルで通しておくと同じ失敗を未然に防げる。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error/)
- [npm installでEACCES権限エラーが出た時の対処法](/posts/npm-install-permission-denied/)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict/)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache/)
