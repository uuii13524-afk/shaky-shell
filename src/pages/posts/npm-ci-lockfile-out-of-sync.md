---
title: 'npm ci が package.json と package-lock.json の不一致（EUSAGE）で失敗する原因と解決手順'
date: '2026-08-20'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'CI環境でnpm ciを実行すると、package.jsonとpackage-lock.jsonが同期していないためEUSAGEエラーで失敗する症状を解説します。npm installでlockfileを再同期し、CIで再現しなくなるまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'CI/CD']
en_tags: ['Node.js', 'npm', 'CI/CD']
---

## やりたかったこと（症状）

ローカルで動いているNode.jsプロジェクトに、新しい依存パッケージ`dayjs`を追加した。手元では`package.json`の`dependencies`に直接1行追記しただけで、`npm install`を実行し忘れたままコミットしてpushしてしまった。

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "dayjs": "^1.11.10"
  }
}
```

CI（GitHub Actions想定の環境）で再現させるため、ローカルで`node_modules`を消してから`npm ci`を実行したところ、以下のエラーで即座に失敗した。

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
npm error
npm error Clean install a project
npm error
npm error Usage:
npm error npm ci
```

ローカルでは`npm install`ではなく普段から`npm ci`を使う癖がなかったため、この不一致に気づかずコミットしてしまっていた。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- パッケージマネージャ: npm（yarn/pnpmは未使用）
- 追加した依存: `dayjs@^1.11.10`

## 試したこと

最初は「CI側のキャッシュが古いのでは」と疑い、GitHub Actionsの`actions/cache`のキーを変えてキャッシュを無効化することを検討した。しかしエラーメッセージをよく読むと`Missing: dayjs@1.11.23 from lock file`とあり、キャッシュではなく`package-lock.json`自体に`dayjs`のエントリが存在しないことが原因だと分かった。

念のため`package-lock.json`の中身を`dayjs`で検索してみたが、該当する行は一切ヒットしなかった。

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`には`dayjs`が書かれているのに、`package-lock.json`には一切記録がない。ここでようやく「`package.json`を手編集した後に`npm install`を実行し忘れた」という単純な原因に気づいた。

`npm ci`は`npm install`と違い、`package-lock.json`の内容を書き換えることを許可しない。これは意図的な仕様で、CI環境で「実行するたびに依存関係が微妙に変わる」ことを防ぐための安全装置になっている。今回のように`package.json`だけを手で書き換えると、その安全装置がそのままエラーとして表面化する。

## 原因

`npm ci`は`package-lock.json`（または`npm-shrinkwrap.json`）に記録された内容を一字一句そのままインストールするコマンドで、`package.json`との整合性チェックを厳密に行う。`package.json`の`dependencies`に新しいパッケージを追記しても、`npm install`を実行して`package-lock.json`を更新しない限り、lockfile側にはそのパッケージの依存解決結果（バージョン・integrity hash・依存ツリー上の位置）が一切反映されない。

`npm install`は多少の不整合があっても自動的にlockfileを更新して先に進んでくれるが、`npm ci`は「lockfileと完全一致しない限り実行しない」という前提のコマンドなので、更新し忘れたlockfileをそのまま使おうとした瞬間にEUSAGEエラーで止まる。CIパイプラインの多くは再現性を優先して`npm ci`を採用しているため、ローカルで`npm install`だけ実行して動作確認した気になっていても、CIで初めてこの不一致が発覚するというパターンに何度か遭遇している。

## 解決手順

### 1. lockfileにdayjsが存在しないことを確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

### 2. npm installでlockfileを再同期する

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 2 packages, and audited 3 packages in 539ms

found 0 vulnerabilities
```

`npm install`を実行すると、`package.json`の内容を元に`package-lock.json`が自動的に更新される。

### 3. lockfileにdayjsが追加されたことを確認する

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
        "dayjs": "^1.11.10",
        "left-pad": "^1.3.0"
      }
```

### 4. package-lock.jsonの差分をコミットする

```bash
git add package.json package-lock.json
git commit -m "chore: sync package-lock.json after adding dayjs"
```

`package.json`だけでなく、更新された`package-lock.json`も必ず同じコミットに含める。片方だけをコミットすると、次に誰かが`npm ci`を実行したときに同じエラーが再発する。

### 5. npm ciで再現確認する

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 2 packages, and audited 3 packages in 523ms

found 0 vulnerabilities
```

エラーなく完了した。

## 動作確認

インストールされたパッケージのバージョンを`npm ls`で確認し、意図した`dayjs`が実際にインストールされていることを確認した。

```bash
npm ls --depth=0
```

```text
npm-ci-repro@1.0.0
+-- dayjs@1.11.23
`-- left-pad@1.3.0
```

`dependencies`に書いた`dayjs`が実際にインストールされ、`npm ci`もエラーなく通ることを確認できた。

## まとめ

- `npm ci`は`package.json`と`package-lock.json`の完全な整合性を要求するコマンドで、`package.json`を手編集しただけでは`package-lock.json`は自動更新されない。
- `Missing: <package>@<version> from lock file`というメッセージが出た場合は、まず`grep`でlockfile内に該当パッケージのエントリが本当に存在するか確認するのが早い。
- 依存を追加・変更するときは、必ず`npm install`を実行してから`package.json`と`package-lock.json`の両方を同じコミットに含める。CIで`npm ci`を使っている場合は、これを忘れるとローカルでは動くのにCIだけ落ちるという分かりにくい状況になる。

## よくある質問

**Q: `npm install`と`npm ci`はどちらを使うべきですか？**
ローカルでの開発中に依存を追加・更新する場合は`npm install`を使います。CI環境やDockerビルドなど、lockfileの内容をそのまま再現したい場面では`npm ci`を使うのが推奨されています。`npm ci`は`node_modules`を毎回削除してからクリーンインストールするため、ローカル開発の日常的な用途にはやや過剰です。

**Q: pre-commitフックなどで事前にこのミスを防ぐ方法はありますか？**
`package.json`と`package-lock.json`のどちらか一方だけがステージングされている場合に警告するフックを`husky`などで組んでおくと、コミット前に気づけます。厳密には`npm install --package-lock-only`を実行してlockfileだけ更新し、差分がないかをCIの最初のステップでチェックする方法もあります。

**Q: yarnやpnpmでも同じ問題は起きますか？**
仕組みは違いますが、同種の問題は起こり得ます。yarnには`yarn install --frozen-lockfile`、pnpmには`pnpm install --frozen-lockfile`という、`npm ci`に相当する「lockfileと不一致なら失敗する」オプションがあります。

## 関連記事

- [npm installでERESOLVEエラーが出たときの原因と解決手順](/posts/npm-eresolve-error)
- [npm installでEACCESエラー（permission denied）が出る原因と解決手順](/posts/npm-install-permission-denied)
- [npmキャッシュのクリア方法（npm cache clean --force）](/posts/npm-cache-clear)
- [package.jsonのscriptsの書き方まとめ](/posts/npm-package-json-scripts)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
