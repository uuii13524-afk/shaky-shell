---
title: 'npm ci が「can only install packages when...are in sync」で失敗する原因と解決手順'
date: '2026-09-06'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに依存を追加した直後、CIのnpm ciがロックファイル不一致エラーで止まる症状を解説。npm installでpackage-lock.jsonを更新してから再度npm ciを通すまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci']
en_tags: ['Node.js', 'npm', 'npm ci']
---

## やりたかったこと（症状）

社内の検証用プロジェクトに`dayjs`を新しい依存として追加した。手元では`package.json`を直接編集しただけで、`package-lock.json`は更新していなかった。その状態で、CIと同じ手順を再現するために`npm ci`をローカルで実行した。

```bash
cd npmci-repro
npm ci
```

インストールが始まるどころか、いきなりエラーで止まった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

普段`npm install`しか使っていなかったので、「`package.json`に依存を書いただけなのに、なぜ`npm install`を経由しないとダメなのか」がすぐには理解できなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象プロジェクト: 依存が`lodash`のみの状態から`dayjs`を`package.json`に追記しただけ（`package-lock.json`は未更新）

## 試したこと

まず、エラーメッセージの`code EUSAGE`という文字列だけを見て、npmのバージョンが古いのではないかと疑った。`npm -v`を確認したが10.9.7で、特に極端に古いわけではなかった。

次に、`node_modules`を丸ごと削除してから`npm ci`を再実行すれば直るのではないかと考えた。

```bash
rm -rf node_modules
npm ci
```

結果は同じで、`Missing: dayjs@1.11.23 from lock file`というメッセージがまた出た。`node_modules`の状態は今回の原因とは無関係だと分かった。

ここでようやく、`package-lock.json`の中身を`grep`で確認した。

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`には`dayjs`が書かれているのに、`package-lock.json`側には`dayjs`のエントリが1件も存在しなかった。ここで初めて「`npm ci`は`package.json`を見て依存関係を解決するコマンドではない」ということに思い至った。

## 原因

`npm install`は実行のたびに`package.json`の内容を解釈し、必要であれば`package-lock.json`を更新しながら依存を解決する。一方`npm ci`は、`package-lock.json`（または`npm-shrinkwrap.json`）に記録されている内容を**そのまま厳密に**インストールするコマンドで、`package.json`の内容と食い違いがあれば依存解決を行わずにエラーで停止する仕様になっている。

今回は`package.json`に`dayjs`を追記したにもかかわらず、`npm install`を一度も実行していなかったため、`package-lock.json`側にはまだ`dayjs`の情報が存在しなかった。この「片方だけ更新されている」状態を`npm ci`が検知し、`EUSAGE`エラーとして拒否していた。

エラーメッセージの`Missing: dayjs@1.11.23 from lock file`という一文は、`package.json`側が要求しているバージョン範囲（`^1.11.10`）に対して、ロックファイルに解決済みバージョンが記録されていないことを指している。`npm ci`はこの不一致を自動修復せず、明示的に`npm install`を先に実行するよう案内するだけで処理を止める。CI環境で`npm ci`を使う理由（インストール内容を完全に固定し、想定外のバージョン解決を防ぐ）を考えれば、この挙動は意図された安全装置だと理解できた。

## 解決手順

### 1. ロックファイルの状態を確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`に書いた依存が`package-lock.json`に反映されていないことを確認した。

### 2. npm install でロックファイルを同期する

```bash
npm install
```

```text
added 2 packages, and audited 3 packages in 923ms

found 0 vulnerabilities
```

このコマンドで`package.json`の内容がロックファイルに反映される。

### 3. ロックファイルに依存が追加されたことを確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
1
```

先ほどは0件だった`dayjs`のエントリが1件になっていることを確認した。

### 4. npm ci を再実行する

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 833ms

found 0 vulnerabilities
```

エラーなくインストールが完了した。

## 動作確認

`node_modules`の中身を確認し、期待通り2パッケージ（`lodash`と`dayjs`）分のディレクトリが展開されていることを確認した。

```bash
ls node_modules | wc -l
```

```text
2
```

これで、CI環境でも同じ`npm ci`が通ることを確認できた。以後は「`package.json`を編集したら、コミット前に必ず`npm install`を実行してロックファイルの差分もあわせてコミットする」という運用に統一した。

## まとめ

- `npm ci`は`package.json`を見て依存解決を行うコマンドではなく、`package-lock.json`に記録済みの内容をそのまま再現するコマンド。両者が食い違うと`EUSAGE`エラーで停止する。
- `package.json`に依存を追記しただけでコミットすると、ロックファイルとの不一致でCIの`npm ci`が失敗する。追記後は必ず`npm install`を実行し、更新された`package-lock.json`も一緒にコミットする。
- エラーメッセージの`Missing: <package>@<version> from lock file`は、どのパッケージがロックファイル未反映かをそのまま教えてくれるので、まずここを読んでからロックファイルの中身を`grep`で確認すると切り分けが速い。

## よくある質問

**Q: `npm install`ではなく`npm ci`をCIで使う理由は何ですか？**
`npm install`は実行環境やタイミングによって依存関係の解決結果が微妙に変わる可能性がありますが、`npm ci`は`package-lock.json`の内容を厳密に再現するため、ローカルとCIで同じ依存構成を保証しやすくなります。そのぶん、ロックファイルとの不一致には一切妥協せずエラーにする、という設計になっています。

**Q: `package-lock.json`をGit管理から外してもよいですか？**
おすすめしません。`npm ci`は`package-lock.json`の存在を前提としたコマンドなので、外してしまうとCIでの再現性という`npm ci`本来のメリットが失われます。

**Q: 依存を1つ追加しただけなのに、`npm install`のたびに無関係な差分が大量に出るのが気になります。**
他の依存のバージョン範囲が緩い場合、npmのバージョン解決アルゴリズムの更新やレジストリ側の情報更新によって、意図しないパッケージの差分が出ることがあります。気になる場合は`npm install <package>`のように対象を絞ってインストールすると、差分を最小限に抑えやすくなります。

## 関連記事

- [Node.jsのバージョン管理（nvm）まとめ](/posts/node-version-management-nvm)
- [npm installで発生するERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error)
- [npmキャッシュのクリア方法まとめ](/posts/npm-cache-clear)
- [GitHub ActionsでNode.jsの依存キャッシュを使う方法](/posts/github-actions-node-cache)
