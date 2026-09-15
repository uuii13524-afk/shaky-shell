---
title: 'npm ciが「package.json and package-lock.json...are in sync」で失敗する原因と解決手順'
date: '2026-09-15'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'ローカルではnpm installが正常に通るのに、CI上のnpm ciだけがpackage.jsonとpackage-lock.jsonの不整合を示すEUSAGEエラーで失敗する症状を解説します。原因となったコミット漏れを特定し、npm ciを通すまでの具体的な手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'CI']
en_tags: ['Node.js', 'npm', 'CI']
---

## やりたかったこと（症状）

チームの`api-server`リポジトリに、日付操作のために`dayjs`を追加した。

```bash
npm install dayjs
git add package.json
git commit -m "feat: add dayjs for date formatting"
git push
```

ローカルでは`npm run build`まで問題なく通り、そのままpushした。ところがGitHub Actions側のCIが落ちた。ログを見ると、失敗しているのは自分が書いたコードではなく、依存関係をインストールする最初のステップだった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrapjson are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.11 from lock file
npm error
npm error Clean install a project
```

最初は「CIのキャッシュが壊れているのでは」と疑い、Actionsのキャッシュを手動で削除して再実行した。しかし結果は同じエラーで変わらなかった。

## 環境

- OS: macOS Sonoma 14.5（ローカル） / Ubuntu 22.04（GitHub Actions runner）
- Node.js: v20.16.0
- npm: 10.8.2
- CI: GitHub Actions（`actions/setup-node@v4` + `npm ci`）
- リポジトリ: `api-server`（Express + TypeScript）

## 試したこと

まずGitHub Actionsのワークフロー定義を確認した。

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'
- run: npm ci
- run: npm run build
```

`npm ci`を使っているだけで、特に変わったことはしていない。次に、Actionsの「Re-run all jobs」でキャッシュを無視して再実行してみたが、まったく同じ`EUSAGE`エラーで落ちた。この時点でキャッシュの問題ではないと判断した。

ローカルの`git status`を確認したところ、原因に気づいた。

```bash
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

「clean」と出ているので一見問題なさそうに見えたが、直前のコミット内容を`git show --stat`で確認して初めて気づいた。

```bash
git show --stat HEAD
```

```text
 package.json | 1 +
 1 file changed, 1 insertion(+)
```

変更されたファイルが`package.json`だけで、`package-lock.json`が含まれていない。`npm install`は実行時にロックファイルも更新するはずだが、コミットには含まれていなかった。

## 原因

手元の`package-lock.json`を`cat`で確認すると、`dayjs`のエントリは実際に追記されていた。つまり`npm install`自体は正しくロックファイルを更新していた。問題は、そのファイルをコミットする前に`git add package.json`とファイル名を明示して`git add`していたことだった。`package-lock.json`は`.gitignore`には含まれていなかったが、コミット対象として明示的に指定し忘れたため、変更がステージングされず、そのままローカルの作業ツリーにだけ残っていた。

`npm install`は`package.json`と`package-lock.json`の内容が食い違っていても、足りないパッケージを補って両方のファイルを書き換えながらインストールを進める（差分を許容するコマンド）。一方`npm ci`は、`package-lock.json`に記録されている内容をそのまま信頼し、`package.json`との整合性チェックで少しでもズレがあれば即座に失敗する（差分を許容しないコマンド）という設計の違いがある。

ローカルでは常に`npm install`を使っていたため矛盾に気づかず、CI側だけが`npm ci`で厳密にチェックしていたために、CIだけが落ちるという状況になっていた。

## 解決手順

### 1. ローカルのpackage-lock.jsonが最新かを確認する

```bash
git diff HEAD -- package-lock.json
```

```text
diff --git a/package-lock.json b/package-lock.json
index 3a1f9c2..8e7b410 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -12,6 +12,9 @@
     "dependencies": {
       "dayjs": "^1.11.11",
+      ...
```

コミット済みのHEADと比較すると、ローカルの`package-lock.json`にだけ`dayjs`の差分が残っていることが確認できた。これでコミット漏れが確定した。

### 2. package-lock.jsonを明示的にステージングしてコミットする

```bash
git add package-lock.json
git commit -m "chore: commit package-lock.json for dayjs"
git push
```

`git add package.json`のように特定ファイルを指定する場合、関連ファイルの追加忘れが起きやすい。今回はこのパターンだった。

### 3. ローカルでnpm ciを試してCIと同じ条件を再現する

```bash
rm -rf node_modules
npm ci
```

```text
added 412 packages, and audited 413 packages in 6s
```

pushする前にローカルでも`npm ci`を実行し、CIと同じ厳密なインストール方式で通ることを確認してからpushする運用に変更した。

### 4. CIの再実行結果を確認する

pushしたコミットでActionsが自動的に再実行され、`npm ci`のステップが成功した。

```text
added 412 packages, and audited 413 packages in 5s
npm notice
```

## 動作確認

念のため、まっさらな環境でも同じ手順を再現して確認した。

```bash
git clone git@github.com:example-org/api-server.git api-server-check
cd api-server-check
npm ci
npm run build
```

```text
added 412 packages, and audited 413 packages in 7s

> api-server@1.0.0 build
> tsc -p tsconfig.json

```

エラーなくインストールとビルドが完了した。

## まとめ

- `npm install`はロックファイルとの差分を許容して自動修正するが、`npm ci`はロックファイルを厳密に信頼し、少しでも`package.json`とズレがあれば`EUSAGE`エラーで即座に失敗する。
- 依存パッケージを追加したときは、`package.json`だけでなく`package-lock.json`も必ず一緒にコミットする。特定ファイルを指定して`git add`する運用だと、関連ファイルの追加漏れに気づきにくい。
- push前にローカルで`npm ci`を一度実行してみると、CIと同じ厳密なチェックを事前に再現でき、今回のようなロックファイル不整合を早期に発見できる。

## よくある質問

**Q: なぜCIだけ失敗して、ローカルの`npm install`では気づけなかったのですか？**
`npm install`はロックファイルとの差分を許容し、足りない分を補いながら両方のファイルを更新してしまうためです。一方`npm ci`はロックファイルの内容をそのまま信頼して厳密にインストールするため、`package.json`との不整合があると即座にエラーになります。CIで`npm ci`を使っている場合、この違いに気づきにくくなります。

**Q: `git add .`を使えば防げましたか？**
はい、`git add .`であれば`package-lock.json`の変更も一緒にステージングされていたはずです。ただし対象ファイルを取りこぼす別のリスクもあるため、コミット前に`git status`で変更ファイル一覧を必ず確認する習慣の方が根本対策になります。

**Q: CIのキャッシュを疑って再実行したのは無駄でしたか？**
今回については無駄でしたが、切り分けとしては悪くない手順です。キャッシュを無視して再実行しても同じエラーが再現するかを確認できれば、「キャッシュの問題ではない」と早い段階で除外でき、次にコミット内容の確認へ進めます。

## 関連記事

- [npmでERESOLVEエラーが出たときの原因と解決手順](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアする方法](/posts/npm-cache-clear)
- [npm installでPermission deniedが出るときの原因と解決手順](/posts/npm-install-permission-denied)
- [GitHub Actionsでnode_modulesをキャッシュして高速化する](/posts/github-actions-node-cache)
- [nvmでNode.jsのバージョンを管理する方法](/posts/node-version-management-nvm)
