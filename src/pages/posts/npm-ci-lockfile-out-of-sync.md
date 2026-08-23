---
title: 'npm ciでEUSAGE「package.jsonとpackage-lock.jsonがsyncしていません」の原因と解決手順'
date: '2026-08-23'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'npm installは通るのにnpm ciだけがEUSAGEエラーで失敗する症状を解説。package.jsonに手動で依存を追記してpackage-lock.jsonを更新し忘れたことが原因で、npm installでlockを同期させて解決するまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'ビルドエラー']
en_tags: ['Node.js', 'npm', 'npm ci', 'build error']
---

## やりたかったこと（症状）

CI環境の再現性を上げるために、ローカルの開発サーバーでは`npm install`を使い、CIパイプライン用のDockerビルドでは`npm ci`を使うように統一している小さなNode.jsプロジェクトがある。日付処理に`dayjs`を新しく使いたくなったので、`package.json`の`dependencies`に直接エントリを追記し、そのままコミットしてpushした。

```json
{
  "dependencies": {
    "lodash": "^4.17.20",
    "dayjs": "^1.11.10"
  }
}
```

ローカルでは`npm install`を実行してから動作確認していたので何の問題もなく動いていた。ところが、同じ内容を素の状態（`node_modules`もlockの更新履歴もない状態）から`npm ci`で入れ直そうとしたところ、インストール自体が失敗した。

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

最初は「`npm ci`と`npm install`で挙動が違うだけで、そのうち直る一時的なエラーだろう」と軽く見て、`node_modules`を消してもう一度`npm ci`をやり直したが、まったく同じエラーが出続けた。

## 環境

- OS: Ubuntu 24.04.4 LTS（カーネル 6.18系）
- Node.js: v22.22.2
- npm: 10.9.7
- package-lock.json: `lockfileVersion: 3`
- 追加しようとした依存: `dayjs@^1.11.10`

## 試したこと

まず、キャッシュが古いのが原因ではないかと疑い、`npm cache clean --force`を実行してから再度`npm ci`を試した。

```bash
npm cache clean --force
npm ci
```

結果は変わらず、同じ`EUSAGE`エラーが出た。ここでキャッシュの問題ではないと判断した。

次に、エラーメッセージを改めて読み直した。「`npm ci` can only install packages when your package.json and package-lock.json ... are in sync」という一文と、「Missing: dayjs@1.11.23 from lock file」という具体的な指摘がある。ここで初めて、`package.json`は編集したが`package-lock.json`はまったく触っていないことに気づいた。

実際に`package-lock.json`の中身を`dayjs`で検索してみると、該当エントリが1件もヒットしなかった。

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`にだけ依存が増えていて、`package-lock.json`側には反映されていない状態だった。

## 原因

`npm install`は実行のたびに`package.json`を読み、必要なら`package-lock.json`を再計算・更新してからインストールする。そのため、`package.json`を手で編集した直後でも`npm install`を挟めば辻褄が合ってしまい、症状に気づきにくい。

一方`npm ci`は、`package-lock.json`（または`npm-shrinkwrap.json`）に書かれている内容を厳密な唯一の真実として扱い、そこに書かれている通りの依存関係だけを再現するために存在するコマンドで、`package.json`と`package-lock.json`の間に矛盾があると解決を試みずに即座に失敗する仕様になっている。今回は`package.json`の`dependencies`に`dayjs`を手動追記した際に`npm install`を経由しなかった（エディタで直接書き換えてそのままコミットした）ため、`package-lock.json`にはその変更が一切反映されておらず、両者が食い違ったままリポジトリに残っていた。

CI環境やDockerビルドで`npm ci`を使う理由はまさにこの厳密さ（ローカルの`node_modules`の状態やnpmのバージョン差に左右されず、lockファイル通りに再現する）にあるため、「動くはずのpackage.jsonなのに`npm ci`だけ失敗する」ときは、まず`package.json`と`package-lock.json`の同期が崩れていないかを疑うのが定石になる。

## 解決手順

### 1. package-lock.jsonに対象パッケージが存在しないことを確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`側にはあるのに、lock側には無いことを確認した。

### 2. npm installでlockファイルを同期させる

`npm ci`ではなく、あえて`npm install`を実行して`package-lock.json`を`package.json`の内容に合わせて再計算させる。

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 753ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

### 3. package-lock.jsonに反映されたことを確認する

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
    "dayjs": "^1.11.10",
    "lodash": "^4.17.20"
  }
```

`dependencies`のエントリだけでなく、`node_modules/dayjs`側の解決済みエントリにも`version: "1.11.23"`として反映されていることも確認した。

### 4. npm ciを再実行して成功することを確認する

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 900ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

`EUSAGE`エラーは出ず、正常にクリーンインストールが完了した。

## 動作確認

`node_modules`を完全に削除した状態から`npm ci`のみで依存解決が通ることを確認し、CIパイプラインと同じ条件を再現できていることを確かめた。

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 900ms
```

エラーなく`node_modules`が復元され、`dayjs`と`lodash`の両方が想定通りのバージョンでインストールされていることも`npm ls dayjs lodash`で確認した。

## まとめ

- `npm ci`は`package-lock.json`の内容だけを唯一の真実として扱うコマンドで、`package.json`との間に矛盾があると解決を試みず即座に`EUSAGE`エラーで失敗する。
- `package.json`を直接編集して依存を追加・変更した場合、必ず`npm install`を一度挟んで`package-lock.json`を再計算させる。そのままコミットすると、ローカルでは`npm install`経由で動いて見えても、CIやDockerビルドの`npm ci`だけが失敗する食い違いが生まれる。
- エラーメッセージ中の「Missing: `<パッケージ名>@<バージョン>` from lock file」は、まさにどのパッケージが同期していないかを直接教えてくれているので、原因調査の最短ルートになる。

## よくある質問

**Q: `package.json`を編集したら毎回`npm install`を実行しないといけませんか？**
依存関係（`dependencies`・`devDependencies`など）を変更した場合は必要です。`npm install <package>`のようにコマンド経由で追加すれば`package.json`と`package-lock.json`は自動的に同時更新されるので、手編集よりもこちらを使う方が今回のような食い違いを防げます。

**Q: CIでは`npm install`ではなく`npm ci`を使うべきなのはなぜですか？**
`npm ci`は`package-lock.json`に記録された内容を厳密に再現し、インストールごとに解決結果がぶれないことを保証するためのコマンドです。ローカルのnpmキャッシュや依存の解決順序に左右される`npm install`と違い、CIでは同じlockファイルから毎回同じ`node_modules`を再現できることが重要なので、`npm ci`の方が適しています。

**Q: `package-lock.json`はGit管理すべきですか？**
すべきです。今回のように`package.json`と`package-lock.json`の食い違いに気づけるのは、両方がGit管理下にあり差分として見えるからです。`.gitignore`に含めてしまうと、この種の不整合をレビューで発見する手段がなくなります。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npm installでEACCES権限エラーが出た時の対処法](/posts/npm-install-permission-denied)
- [Node.jsのバージョンをnvmで管理する方法（Windows/Mac）](/posts/node-version-management-nvm)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
