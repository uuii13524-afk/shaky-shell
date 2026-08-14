---
title: 'npm ciがEUSAGEエラーで失敗する原因と解決手順（package-lock.json不一致）'
date: '2026-08-14'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'CIで実行したnpm ciがEUSAGEエラーで停止し、package.jsonとpackage-lock.jsonが同期していないと言われる症状を解説。原因を切り分け、npm installでロックファイルを更新して解消するまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'GitHub Actions']
en_tags: ['Node.js', 'npm', 'npm ci', 'GitHub Actions']
---

## やりたかったこと（症状）

社内ダッシュボードのプロジェクトに、日時フォーマット処理を簡潔に書くため`dayjs`を追加した。ローカルでは`npm install`でそのままインストールでき、動作確認も問題なかったので、変更をコミットしてpushした。

```bash
npm install dayjs
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

ところがGitHub ActionsのCIログを確認すると、ビルドジョブの`npm ci`のステップが赤くなっていた。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
npm error
npm error Clean install a project
```

ローカルでは何の問題もなく動いていたのに、CI上だけで失敗する状況で、最初は原因が分からなかった。

## 環境

- CIランナー: GitHub Actions（`ubuntu-24.04`）
- ローカルOS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 追加したパッケージ: `dayjs@^1.11.10`（インストール時点の解決バージョンは`1.11.21`）

## 試したこと

まず、CIのワークフローファイルを確認した。

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
- run: npm ci
- run: npm run build
```

`npm ci`自体は一般的な書き方で、特に間違いは見当たらなかった。次に、ローカルでキャッシュが影響しているのではと考え、`node_modules`を消してもう一度`npm install`を実行してみた。

```bash
rm -rf node_modules
npm install
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

ローカルでは相変わらず成功する。ここでようやく、「ローカルでは`npm install`、CIでは`npm ci`を使っている」という違いに気づいた。手元で`npm ci`を直接実行してみたところ、CIと同じエラーが再現した。

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.21 from lock file
```

`git status`で確認すると、`package.json`はコミットに含めていたが、`package-lock.json`の差分をステージし忘れて別コミットのままpushされていないことが分かった。

```bash
git log --oneline -1 -- package-lock.json
git log --oneline -1 -- package.json
```

`package.json`だけが最新コミットに含まれ、`package-lock.json`は1つ前のコミットのままだった。

## 原因

`npm install`はコマンド実行時に`package.json`の内容を見て依存関係を解決し、必要なら`package-lock.json`を更新しながらインストールを進める。そのため、`package.json`に手を加えた直後でも実行さえすれば整合性が取れてしまう。

一方`npm ci`は「`package-lock.json`に書かれている内容をそのままインストールするだけ」の専用コマンドで、`package.json`との整合性チェックだけを行い、不一致があれば解決を試みずに即座にエラーで停止する。CI環境で`npm ci`が推奨されるのは、まさにこの「ロックファイル通りにしかインストールしない」という再現性の高さが理由だが、今回のように`package-lock.json`のコミットを忘れると、ローカルでは気づけずCIだけで失敗する状態になる。

## 解決手順

### 1. ロックファイルを最新化する

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 587ms
found 0 vulnerabilities
```

### 2. package-lock.jsonの差分を確認する

```bash
git diff package-lock.json | head -20
```

```text
        "dayjs": "^1.11.10",
        "lodash": "^4.17.21"
      }
```

`dayjs`のエントリが追加されていることを確認した。

### 3. package.jsonとpackage-lock.jsonを両方コミットする

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json for dayjs"
git push
```

### 4. ローカルでnpm ciを再現して確認する

pushする前に、CIと同じコマンドで検証しておく。

```bash
rm -rf node_modules
npm ci
```

```text
added 2 packages, and audited 3 packages in 782ms
found 0 vulnerabilities
```

エラーが出ずにインストールが完了した。

## 動作確認

CIのワークフロー実行結果を確認し、`npm ci`のステップが成功していることを確認した。以降のビルド・テストステップも問題なく通過した。念のため別ブランチを切って同じ手順で`git clone`し直し、クリーンな状態から`npm ci`が一発で通ることも確認した。

## まとめ

- `npm ci`は`package-lock.json`の内容をそのままインストールするだけで、依存関係の解決や更新は行わない。`package.json`との不一致は即座に`EUSAGE`エラーになる。
- `npm install`はロックファイルを自動更新するため、ローカルでは問題が隠れやすい。依存関係を追加・変更したら`package.json`と`package-lock.json`を必ずセットでコミットする。
- push前に`rm -rf node_modules && npm ci`をローカルで実行しておくと、CIで初めて気づくという事故を防げる。

## よくある質問

**Q: `npm install`と`npm ci`はどちらをCIで使うべきですか？**
CIでは`npm ci`が推奨されます。`package-lock.json`の内容を厳密に再現するため、ローカルとCIで異なるバージョンがインストールされるのを防げます。`npm install`はロックファイルを書き換えてしまう可能性があり、CIの再現性という目的には向きません。

**Q: `.gitignore`に`package-lock.json`を入れているのですが問題ありますか？**
`package-lock.json`はコミット対象にすべきファイルです。`.gitignore`に含めていると、他の開発者やCIが実行するたびに異なるバージョンの依存関係が解決される可能性があり、今回のような不一致がさらに起きやすくなります。

**Q: 依存関係を1つ追加しただけなのに、ロックファイルの差分が大量に出ます。なぜですか？**
npmのバージョンによっては、インデントやメタデータ（`lockfileVersion`のフォーマット等）が変わることで差分が広がる場合があります。差分が異常に大きい場合は、`npm --version`がチーム内・CI内で揃っているか確認してください。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [git pushがrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [GitHub Actionsでシークレットを使う方法](/posts/github-actions-secrets)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
