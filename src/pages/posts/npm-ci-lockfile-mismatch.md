---
title: 'npm ci が「in sync」エラーで失敗する原因と解決手順'
date: '2026-08-06'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに依存関係を追記した後にnpm ciを実行すると、EUSAGEエラーで「package.jsonとpackage-lock.jsonが同期していません」と表示されて失敗する症状を解説。原因を切り分け、package-lock.jsonを正しく更新して解決するまでの手順を紹介します。'
ja_tags: ['npm', 'Node.js', 'package-lock.json']
en_tags: ['npm', 'Node.js', 'package-lock.json']
---

## やりたかったこと（症状）

個人のNode.jsプロジェクトに日付処理用の`dayjs`を追加しようと思い、`package.json`の`dependencies`に直接1行追記した。エディタで手早く編集して、インストールは後でまとめてやろうと考えていた。

```json
{
  "name": "npmci-repro",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "^1.3.0",
    "chalk": "^5.3.0",
    "dayjs": "^1.11.10"
  }
}
```

CI環境を再現するクリーンインストールの動作を手元でも確認しておきたかったので、`npm install`ではなく`npm ci`を先に実行した。

```bash
npm ci
```

すると`added`のログではなく、いきなりエラーで終了した。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
npm error
npm error Clean install a project
```

終了コードも`1`で、`node_modules`は生成されなかった。

```bash
echo $?
```

```text
1
```

## 環境

- OS: Linux（コンテナ環境、Ubuntu系）
- Node.js: v22.22.2
- npm: 10.9.7
- `package-lock.json`: `lockfileVersion: 3`
- 追加しようとした依存関係: `dayjs@^1.11.10`（既存の`package-lock.json`には未登録）

## 試したこと

最初は「`node_modules`が壊れているのでは」と考え、`node_modules`を削除してから再度`npm ci`を試した。

```bash
rm -rf node_modules
npm ci
```

結果は同じで、`Missing: dayjs@1.11.21 from lock file`というメッセージが変わらず出た。この時点で、`node_modules`側の問題ではなく`package-lock.json`の中身そのものが原因だと分かった。

念のため`package-lock.json`を`grep`し、`dayjs`のエントリが存在するかを確認した。

```bash
grep -c "\"dayjs\"" package-lock.json
```

```text
0
```

`package.json`には`dayjs`を追記したのに、`package-lock.json`には一切反映されていなかった。`npm ci`はこのエラーメッセージにもある通り、`package-lock.json`（または`npm-shrinkwrap.json`）に記録された依存関係ツリーを**そのまま**再現するだけのコマンドで、`package.json`を見て依存解決を行う`npm install`とは役割が異なる。`package.json`を手編集しただけでは`package-lock.json`は自動更新されないため、両者の内容が食い違った状態で`npm ci`を呼ぶと、今回のように`EUSAGE`で止まる。

## 原因

`npm ci`は「ロックファイルに書かれている通りに、寸分違わずインストールする」ことを目的としたコマンドで、内部的に依存解決は行わない。そのため実行前に、`package.json`に列挙された各依存関係が`package-lock.json`内に**過不足なく**存在するかどうかの整合性チェックが走る。

今回は`package.json`の`dependencies`に`dayjs`を直接追記しただけで、`package-lock.json`を更新するコマンド（`npm install`など）を一度も実行していなかった。その結果、`package.json`側には`dayjs`が存在するのに`package-lock.json`側には存在しない、という不一致が生まれ、`npm ci`が「ロックファイルに記載のない依存関係がある＝同期していない」と判断してエラーで停止した。

`package.json`を直接編集する行為自体は禁止されていないが、編集後に`package-lock.json`を更新する工程を省略すると、ローカルでは`npm install`で誤魔化せてしまう一方、`npm ci`を使うCI/Dockerビルドでは必ずこのエラーに当たる。

## 解決手順

### 1. npm installでロックファイルを更新する

`package.json`に加えた変更を`package-lock.json`に反映させるため、`npm install`を実行した。

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 770ms

1 package is looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

### 2. package-lock.jsonにdayjsが追加されたことを確認する

```bash
grep -c "\"dayjs\"" package-lock.json
```

```text
2
```

`lockfileVersion`が`3`の`package-lock.json`では、パッケージ名がトップレベルの依存関係欄と`packages`欄の2箇所に記録されるため、`2`件ヒットすれば正しく登録されている。

### 3. 改めてnpm ciを実行する

CI相当のクリーンインストールが通るかを再確認するため、`node_modules`を消してから`npm ci`をやり直した。

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 669ms

1 package is looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

今度はエラーなく`added 3 packages`で完了した。

## 動作確認

`node_modules`に`dayjs`が実際に展開されているか、バージョンを直接確認した。

```bash
node -e "console.log(require('./node_modules/dayjs/package.json').version)"
```

```text
1.11.21
```

`package.json`で指定した`^1.11.10`の範囲内で解決された`1.11.21`が正しくインストールされていることを確認できた。終了コードも`0`になっている。

```bash
echo $?
```

```text
0
```

## まとめ

- `npm ci`は`package-lock.json`の内容をそのまま再現するコマンドで、`package.json`を見て依存解決はしない。`package.json`を手編集しただけでは`package-lock.json`は更新されない。
- 依存関係を追加・変更したら、ローカルで`npm install`を一度実行して`package-lock.json`を最新化してからコミットする。`npm ci`は「ロックファイル通りに再現できるか」の検証コマンドとして使い分けるとよい。
- 同じ`EUSAGE` + `Missing: <package>@<version> from lock file`は、Dockerビルドの`RUN npm ci`ステップやCIパイプラインで特に踏みやすい。手元で`npm install`を試すだけで正常に見えても、`npm ci`基準のクリーン環境では失敗することがあるため、`package.json`を変更したPRでは`package-lock.json`の差分が一緒にコミットされているかを必ず確認するとよい。

## 関連記事

- [npmキャッシュのクリア方法](/posts/npm-cache-clear)
- [npmとyarnの違い](/posts/npm-vs-yarn)
- [npm ERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error)
- [package.jsonのscriptsの使い方](/posts/npm-package-json-scripts)
- [nvmによるNode.jsバージョン管理](/posts/node-version-management-nvm)
