---
title: 'npm ciで「can only install packages when your package.json and package-lock.json are in sync」の原因と解決手順'
date: '2026-08-01'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'CI環境でnpm ciを実行すると「can only install packages when your package.json and package-lock.json are in sync」で失敗する症状を解説。package.jsonを手編集してpackage-lock.jsonを更新し忘れた場合の原因と、正しいロックファイルの再生成・コミット手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'package-lock.json']
---

## やりたかったこと（または「症状」）

ローカルで新しいライブラリを使いたくなり、`npm install`ではなく`package.json`の`dependencies`に直接1行追記して、そのままコミット・プッシュした。ローカルでは`node_modules`がすでにあるので普通に動いていたが、GitHub ActionsのCIで`npm ci`を実行するステップだけが失敗するようになった。

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Invalid: lock file's dayjs@1.11.10 does not satisfy dayjs@1.11.11
npm error
npm error Clean install a project
```

ローカルの`npm install`は毎回何も言わずに通っていたので、最初は何が「同期していない」のか分からなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS（GitHub Actions `ubuntu-latest`ランナー）
- Node.js: v20.14.0
- npm: 10.7.0
- CI: GitHub Actions（`actions/setup-node@v4` + `npm ci`）
- 手編集した箇所: `package.json`の`dependencies`に`"dayjs": "^1.11.11"`を追記（`package-lock.json`は未更新のままコミット）

## 試したこと

まず、ローカルでもう一度`npm ci`を実行して同じエラーが再現するか確認した。

```bash
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error Invalid: lock file's dayjs@1.11.10 does not satisfy dayjs@1.11.11
```

ローカルでも同じエラーが出た。つまり「CI特有の問題」ではなく、リポジトリにコミットした`package-lock.json`自体が`package.json`と食い違っている状態だった。`git diff`で確認すると、直近のコミットで`package.json`だけが変更されており、`package-lock.json`は変更されていなかった。

```bash
git log --oneline -3 -- package.json package-lock.json
```

```text
a1b2c3d Update dependency version in package.json
```

`package-lock.json`を触るコミットが1つも無いことが分かり、手編集が原因だと確定した。

## 原因

`npm install`は実行するたびに`package.json`の内容を見て、必要なら`package-lock.json`を自動的に更新する。一方`npm ci`は逆で、**`package-lock.json`に書かれている内容を「正」として、そのバージョンを寸分違わずインストールするだけ**のコマンドで、依存関係の解決自体は行わない。

今回は`package.json`の`dependencies`を直接編集して`dayjs`のバージョン指定を`^1.11.10`から`^1.11.11`に変更したが、`package-lock.json`内の該当エントリは古いバージョン（`1.11.10`）のまま残っていた。`npm ci`はこの2つのファイルの内容が一致しているかを事前に検証しており、一致しない場合はインストールを実行せずにエラーで停止する仕様になっている。ローカルの`npm install`でエラーが出なかったのは、`npm install`が食い違いを見つけても自動修正して黙って進めてしまうためで、これが「壊れていることに気づけなかった」直接の原因だった。

## 解決方法

### 1. ロックファイルの状態を確認する

```bash
npm ci --dry-run
```

`EUSAGE`が出ることを確認し、どのパッケージが不一致かをエラーメッセージから特定する。

### 2. `npm install`でロックファイルを再生成する

`package.json`の内容を正として、`package-lock.json`を再生成する。

```bash
npm install
```

```text
added 0 packages, removed 0 packages, changed 1 package, and audited 842 packages in 3s
```

### 3. 差分を確認する

`package-lock.json`の該当パッケージのバージョンが更新されているか確認する。

```bash
git diff package-lock.json | grep -A 2 '"dayjs"'
```

```diff
-      "version": "1.11.10",
+      "version": "1.11.11",
```

### 4. 更新したロックファイルをコミットする

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json with package.json"
git push
```

### 5. `npm ci`で再検証する

```bash
rm -rf node_modules
npm ci
```

ローカルで`npm ci`が通ることを確認してからプッシュすると、CI側の失敗も同時に解消できる。

## 動作確認

```bash
npm ci
```

```text
added 842 packages, and audited 843 packages in 12s
found 0 vulnerabilities
```

エラーなくインストールが完了し、GitHub Actions側の`npm ci`ステップも成功に変わったことをワークフローの再実行で確認した。

## ハマったポイント

- `npm install`は`package.json`と`package-lock.json`の食い違いを自動修正して黙って通してしまうため、ローカルでは問題に気づけなかった。依存関係を追加・変更するときは、`package.json`を直接編集するのではなく、常に`npm install <package>@<version>`のようにnpmコマンド経由で変更する習慣にした方が安全だと分かった。
- CIでは必ず`npm ci`を使う設計にしていたおかげで、ロックファイルの不整合を早い段階（マージ前）で検知できた。もし本番デプロイでも`npm install`を使っていたら、意図しないバージョンのままリリースされていた可能性がある。
- `package-lock.json`はコンフリクトが起きやすいファイルだが、手で編集して解消するとバージョン不整合の温床になる。コンフリクトした場合は編集せず`npm install`で再生成するのが確実だった。

## よくある質問

**Q: `package.json`を編集したら毎回`npm install`を実行する必要がありますか？**
はい。`dependencies`や`devDependencies`を直接編集した場合は、コミット前に必ず`npm install`を実行して`package-lock.json`を同期させる必要がある。`npm install <package>@<version>`のようにnpm経由で追加・変更すれば、この手順を忘れることがない。

**Q: `npm ci`と`npm install`はCIでどちらを使うべきですか？**
CIやデプロイなど再現性が求められる環境では`npm ci`を使うべき。依存関係の解決を行わずロックファイルの内容をそのままインストールするため高速で、かつ今回のようなロックファイルの不整合を早期に検知できる。

**Q: `package-lock.json`をリポジトリにコミットしなくてもよいですか？**
アプリケーション開発では基本的にコミットするべき。コミットしないと、チームメンバーやCI環境ごとに解決される依存バージョンがずれる可能性があり、`npm ci`自体も利用できなくなる。

## 関連記事

- [npm ERESOLVEエラーの原因と解決方法](/posts/npm-eresolve-error)
- [npm installで権限エラーが出るときの対処法](/posts/npm-install-permission-denied)
- [npmキャッシュのクリア方法](/posts/npm-cache-clear)
- [npmとyarnの違い](/posts/npm-vs-yarn)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
