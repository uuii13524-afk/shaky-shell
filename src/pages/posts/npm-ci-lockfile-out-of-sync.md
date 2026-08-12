---
title: 'npm ciが「package.json and package-lock.json...are in sync」で失敗する原因と解決手順'
date: '2026-08-12'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub Actionsのnpm ciステップが「can only install packages when your package.json and package-lock.json...are in sync」で落ちる症状を解説。package.jsonを手編集してpackage-lock.jsonを更新し忘れたときに起きる原因と、npm installでの直し方を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json', 'GitHub Actions']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json', 'GitHub Actions']
---

## やりたかったこと（症状）

個人開発しているNode.jsプロジェクトに、日付文字列の判定用ライブラリとして`is-odd`を追加したかった。急ぎの修正だったので、`npm install is-odd`を叩く代わりに`package.json`の`dependencies`に直接1行追記して済ませた。

```json
"dependencies": {
  "left-pad": "^1.3.0",
  "is-odd": "^3.0.1"
}
```

ローカルでは`node_modules`にすでに実体があると思い込んでいたため、そのまま`git add package.json`してコミットし、GitHubにpushした。

```bash
git add package.json
git commit -m "add: is-odd dependency"
git push origin main
```

pushした直後、GitHub Actionsの`build`ワークフローが赤くなった。ログを開くと、`npm ci`のステップで落ちていた。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

ローカルで`npm run build`は問題なく通っていたので、最初は何が起きているのか分からなかった。

## 環境

- OS: Ubuntu 22.04（ローカル）／`ubuntu-latest`（GitHub Actions runner）
- Node.js: v22.22.2（`actions/setup-node`でバージョン固定）
- npm: 10.9.7
- Git: 2.43.0
- CI: GitHub Actions、ワークフローのインストールステップは`npm ci`

## 試したこと

まず、CIログのエラーメッセージをそのままローカルで再現できるか試した。`node_modules`を一度削除し、`npm ci`を実行する。

```bash
rm -rf node_modules
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

CIと同じエラーがローカルでも再現した。つまりCI固有の問題ではなく、リポジトリにpushした状態そのものが壊れていることになる。

`npm run build`がローカルで通っていたのは、`node_modules`の中に以前`npm install`した際の`is-odd`の実体がたまたま残っていたためだった。`npm ci`は`node_modules`を毎回消してから`package-lock.json`の記述だけを頼りにインストールする仕様のため、`node_modules`にファイルが物理的に存在するかどうかとは無関係に、ロックファイルの整合性だけを厳密にチェックする。

次に`package-lock.json`の中身を確認した。

```bash
grep -A2 '"is-odd"' package-lock.json
```

`dependencies`側の`package.json`には`is-odd`が追記されているのに対し、`package-lock.json`側にはそのエントリが存在しないことを確認した。`package.json`を直接編集しただけでは、`package-lock.json`は自動更新されないという単純な事実に、ここでようやく気づいた。

## 原因

`npm ci`は`npm install`と違い、依存関係の解決を一切行わない。`package-lock.json`（または`npm-shrinkwrap.json`）に書かれているバージョン・依存ツリーをそのまま信頼して、それを厳密に`package.json`の内容と突き合わせる。両者が1件でも食い違っていると、`npm ci`はインストールを進めず`EUSAGE`エラーで即座に止まる仕様になっている。

今回の場合、`package.json`の`dependencies`に`is-odd`を手で追記した一方、`package-lock.json`は`npm install`を実行しない限り更新されない。ローカルで一度でも`npm install`を実行していれば、その時点でロックファイルが更新され気づけたはずだが、直接ファイルを編集して済ませたためロックファイルとの乖離に気づかないままコミットしてしまった。

GitHub Actionsのワークフローは高速化・再現性のために`npm install`ではなく`npm ci`を使う設定になっていることが多い。`npm ci`は依存解決をしないぶん高速でCI向きだが、その代償として「ロックファイルと`package.json`が完全に一致していること」を前提とする。ローカルで`npm install`ベースの開発フローに慣れていると、この前提を意識せずに`package.json`だけを編集してしまいがちで、今回のようにCIで初めて発覚するケースが多い。

## 解決手順

### 1. package.jsonの変更内容を確認する

まず、追記した依存が意図通りかを再確認した。

```bash
cat package.json
```

`is-odd`が`"^3.0.1"`で入っていることを確認した。

### 2. npm installでロックファイルを更新する

`package.json`の内容を正としてロックファイルを再生成する。

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 484ms

found 0 vulnerabilities
```

`is-odd`本体に加えて、その依存である`is-number`もロックファイルに追加されたことを`git diff`で確認した。

```bash
git diff package-lock.json | head -20
```

`is-odd`と`is-number`のエントリが新規追加されていることを確認した。

### 3. 更新されたロックファイルをコミットする

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with is-odd dependency"
git push origin main
```

`package.json`だけでなく`package-lock.json`もあわせてステージしてコミットするのが今回のポイント。片方だけをコミットすると同じ問題が再発する。

### 4. npm ciで再現しないことを確認する

pushする前に、ローカルで再度クリーンインストールを試して、CIと同じ条件で成功するか確認した。

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 333ms

found 0 vulnerabilities
```

エラーなくインストールが完了した。

## 動作確認

push後、GitHub Actionsのワークフローを再確認したところ、`npm ci`のステップが正常に完了し、後続のビルド・テストステップまで通ったことを確認した。念のため別のクリーンな作業ディレクトリにもう一度cloneし、`npm ci`だけを単独で実行して同じ結果になることも確認した。

```bash
git clone https://github.com/example-user/example-app.git check-clone
cd check-clone
npm ci
```

```text
added 3 packages, and audited 4 packages in 401ms

found 0 vulnerabilities
```

クリーンな環境でも問題なくインストールが完了した。

## まとめ

- `npm ci`は`package.json`と`package-lock.json`の内容を厳密に突き合わせ、1件でも食い違えば`EUSAGE`エラーで停止する。依存解決を行わないぶん高速・再現性が高い代わりに、この整合性チェックが厳しい。
- `package.json`を直接手編集して依存を追加した場合、`package-lock.json`は自動更新されない。編集後は必ず`npm install`を一度実行し、`package-lock.json`の差分もあわせてコミットする。
- ローカルで`npm run build`などが通っても安心できない。`node_modules`に古い実体が残っているだけの可能性があるため、CIと同じ条件を再現するには`rm -rf node_modules && npm ci`をローカルでも実行して確認するのが確実。

## よくある質問

**Q: `package.json`を編集したら毎回`npm install`する必要がありますか？**
`dependencies`や`devDependencies`のバージョン指定を変更・追加・削除した場合は、`npm install`（または`npm update`）を実行して`package-lock.json`を再生成し、両方をコミットする必要があります。`scripts`やその他のフィールドのみの変更であれば`package-lock.json`への影響はありません。

**Q: `npm ci`ではなく`npm install`をCIで使えば回避できますか？**
回避はできますが推奨しません。`npm install`は`package.json`と`package-lock.json`が食い違っていても依存解決してインストールを進めてしまうため、CIとローカルで異なるバージョンがインストールされる余地が生まれます。`npm ci`の厳格さは、この種の食い違いを早期に検知するための仕組みなので、CI側は`npm ci`のまま、ロックファイルの管理を徹底する方が安全です。

**Q: マージコンフリクトで`package-lock.json`を解決するときの注意点は？**
`package.json`側の依存を解決したら、`package-lock.json`は手で編集せず、コンフリクト解決後に`npm install`を一度実行して再生成するのが確実です。`package-lock.json`は自動生成ファイルのため、手動でのコンフリクト解決はほぼ確実に整合性を崩します。

## 関連記事

- [npm installでERESOLVEエラーが出た時の対処法](/posts/npm-eresolve-error)
- [npm installでEACCES権限エラーが出た時の対処法](/posts/npm-install-permission-denied)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)

## おすすめのVPS
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
