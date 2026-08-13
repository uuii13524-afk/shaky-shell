---
title: 'npm ciが「package.jsonとpackage-lock.jsonが同期していません」で失敗する原因と解決手順'
date: '2026-08-13'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub Actionsのビルドで npm ci が EUSAGE エラーで止まる症状を解説。package.jsonに依存パッケージを追記してもpackage-lock.jsonを更新し忘れると再現する。原因の切り分けから npm install での復旧手順まで紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

Node.js製の小さなツールに、新しく`is-odd`パッケージを依存として追加したかった。手元のエディタで`package.json`の`dependencies`に直接`"is-odd": "^3.0.1"`を書き足し、コミットしてpushした。

```bash
git add package.json
git commit -m "add is-odd dependency"
git push origin main
```

ローカルではまだ`npm install`を実行していなかったが、「CI側で`npm ci`が依存関係を入れてくれるはず」と考え、そのままpushした。ところがGitHub Actions側のビルドが失敗し、ログに以下のエラーが出力された。

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

ローカルでは`package.json`を編集しただけで`npm install`も`npm run build`も試していなかったため、まず自分の環境で同じ手順を再現できるか確認することにした。

## 環境

- OS: Ubuntu（コンテナ環境上のCIランナーおよび検証用サンドボックス）
- Node.js: v22.22.2
- npm: 10.9.7
- 対象パッケージ: `left-pad@1.3.0`（既存依存）、`is-odd@3.0.1`（新規追加分）
- CI: GitHub Actions（`npm ci`をインストールステップに使用）

## 試したこと

まず、ローカルの作業ディレクトリで`node_modules`を一度削除し、CIと同じ`npm ci`コマンドを実行して再現するか確かめた。

```bash
rm -rf node_modules
npm ci
```

CIのログとまったく同じ`EUSAGE`エラーが手元でも再現した。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

これで「CI固有の環境差分」ではなく、リポジトリにpushした状態そのものに問題があると分かった。次に、`package-lock.json`の中身に`is-odd`が含まれているか`grep`で確認した。

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

`package.json`には`is-odd`を追記したが、`package-lock.json`は一切更新していなかったため、当然ながら該当エントリは存在しなかった。さらにエラーメッセージをよく読むと、`is-odd`本体だけでなく`is-odd`が依存している`is-number@6.0.0`も「lock fileに存在しない」と指摘されていた。`npm ci`は`package-lock.json`に書かれた依存ツリーを一字一句そのままインストールするコマンドであり、`package.json`側の変更を自分で解決してlockを書き換える機能を持たない、という前提を見落としていたことに気づいた。

## 原因

`npm install`と`npm ci`は似ているようで役割が異なる。`npm install`は`package.json`を読み、必要に応じて依存関係を解決しながら`package-lock.json`を更新する「解決してインストールする」コマンドである。一方`npm ci`は`package-lock.json`（または`npm-shrinkwrap.json`）に記録された依存ツリーをそのままの内容で高速にインストールする「再現インストール」専用のコマンドで、依存解決は一切行わない。

そのため、`package.json`の`dependencies`に新しいパッケージを追記しても、対応する`package-lock.json`の更新を忘れたまま`npm ci`を実行すると、npm自身が「package.jsonとlockファイルの内容が一致していない」と判断してインストールを拒否する。これはCI環境固有のバグではなく、`npm install`を一度も実行していない状態でpushしたことによる、npm仕様どおりの挙動だった。

## 解決手順

### 1. ローカルで`npm install`を実行し、lockファイルを更新する

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 425ms

found 0 vulnerabilities
```

`is-odd`本体と、その依存である`is-number`が追加でインストールされ、`package-lock.json`が更新された。

### 2. `package-lock.json`に対象パッケージが追加されたことを確認する

```bash
grep -c '"is-odd"' package-lock.json
```

```text
1
```

```bash
node -p "require('./package-lock.json').packages['node_modules/is-odd'].version"
```

```text
3.0.1
```

`package-lock.json`の`packages`エントリに`is-odd@3.0.1`が正しく記録されていることを確認した。

### 3. `npm ci`が通ることをローカルで確認してからpushする

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 413ms

found 0 vulnerabilities
```

今度は`EUSAGE`エラーが出ず、正常にインストールが完了した。

### 4. `package.json`と`package-lock.json`を両方コミットしてpushする

```bash
git add package.json package-lock.json
git commit -m "sync package-lock.json with is-odd dependency"
git push origin main
```

`package.json`だけでなく`package-lock.json`もセットでコミットするのが今回の根本対応になる。

## 動作確認

pushした後、GitHub Actionsのビルドログで`npm ci`ステップが正常終了することを確認した。ローカルでも改めてクリーンな状態から手順を再現し、`EUSAGE`が発生しないことを確認できた。

```bash
rm -rf node_modules package-lock.json
npm install
rm -rf node_modules
npm ci
```

```text
added 3 packages, and audited 4 packages in 0.9s

found 0 vulnerabilities
```

`package-lock.json`を作り直した状態からでも、`npm install`→`npm ci`の順で問題なく完了することを確認した。

## まとめ

- `npm ci`は`package-lock.json`の内容をそのまま再現するコマンドで、`package.json`との差分を自動解決してはくれない。`package.json`を手で編集したら、必ず`npm install`を実行して`package-lock.json`を追随させる必要がある。
- エラーメッセージの`Missing: <パッケージ名>@<バージョン> from lock file`は、追加した本体だけでなく、その依存パッケージも含めてlockファイルに反映されていないことを教えてくれる。ここを読めば「何が足りないか」の切り分けは難しくない。
- CIで`npm ci`を使っている場合、pushする前にローカルで`rm -rf node_modules && npm ci`を一度実行しておくと、この種の同期ズレをpush前に検知できる。

## 関連記事

- [npm installでERESOLVEエラーが出た時の対処法](/posts/npm-eresolve-error)
- [npm installがEACCESで失敗する原因と解決手順](/posts/npm-install-permission-denied)
- [npmキャッシュのクリア方法](/posts/npm-cache-clear)
- [GitHub Actionsでnode_modulesをキャッシュする方法](/posts/github-actions-node-cache)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
