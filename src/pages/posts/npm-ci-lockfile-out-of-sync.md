---
title: 'GitHub Actionsのnpm ciが「in sync」エラーで失敗する原因と解決手順'
date: '2026-09-28'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub ActionsのCIでnpm ciがEUSAGEエラーとなり、package.jsonとpackage-lock.jsonが同期していないと表示されて失敗する症状を解説。npm installでロックファイルを更新し直し、CIを再び通すまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'GitHub Actions']
en_tags: ['Node.js', 'npm', 'GitHub Actions']
---

## やりたかったこと（症状）

チームで運用している内部ツールのリポジトリに、ちょっとした日付フォーマット処理を追加するため`package.json`の`dependencies`に直接手でパッケージ名とバージョンを書き足した。

```json
{
  "name": "npm-ci-repro",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

ローカルでは`npm install`済みの`node_modules`がそのまま残っていたので、追加したパッケージを使ったコードは普通に動いた。そのままコミットしてpushしたところ、GitHub Actions側のCIジョブが赤くなった。CIのワークフローは`actions/setup-node`でNode.jsをセットアップした後、依存関係のインストールに`npm ci`を使っている。

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
- run: npm ci
- run: npm test
```

ログを開くと、`npm test`より前の`npm ci`の時点で止まっていた。

## 環境

- CI: GitHub Actions（`ubuntu-24.04`ランナー）
- Node.js: v22.22.2（`actions/setup-node@v4`で指定）
- npm: 10.9.7
- ローカル環境: Ubuntu 24.04 LTS
- リポジトリ: 内部ツール（`package-lock.json`をリポジトリにコミットして管理）

## 試したこと

最初はテストコード側の問題かと思い、`npm test`のログを先に確認しようとしたが、そもそもその手前の`npm ci`ステップで失敗して以降のステップが実行されていなかった。`npm ci`のログを見ると、以下のように出力されていた。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
npm error
npm error Clean install a project
```

一瞬「CIランナー側のキャッシュが壊れているのでは」と疑い、`actions/setup-node`の`cache: npm`設定を外してキャッシュなしで再実行してみたが、結果は同じ`EUSAGE`エラーだった。ここでキャッシュの問題ではないと分かった。

次にメッセージをよく読み返すと、`Missing: is-odd@3.0.1 from lock file`という行があった。自分がローカルで`package.json`に手書きで追加した`is-odd`と、そのサブ依存の`is-number`が、`package-lock.json`側には一切記録されていないことに気づいた。

ローカルの手元では`node_modules`に`is-odd`の実体がすでに入っていたため`require`は普通に解決でき、動作確認では問題が表面化しなかった。しかし`package-lock.json`自体は更新されておらず、コミットされたのは「`dependencies`だけ書き換わったpackage.json」と「古いままのpackage-lock.json」の組み合わせだった。

再現性を確認するため、ローカルでも一度`node_modules`を削除してから`npm ci`を実行してみた。

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

CIと全く同じエラーがローカルでも再現した。これで「CI環境固有の問題」ではなく「コミットした`package-lock.json`自体が古い」ことがはっきりした。

## 原因

`npm ci`は`npm install`と違い、`package.json`を見て依存関係を解決し直すことをしない。`package-lock.json`（または`npm-shrinkwrap.json`）に書かれている内容をそのまま信頼し、そこに列挙されたバージョンだけを`node_modules`に展開するコマンドになっている。そのため、`package.json`と`package-lock.json`の内容に食い違いがあると、npmは黙って解決し直すのではなくエラーで止まる。これは「CIやチーム開発で、ロックされたはずの依存関係が意図せず変わってしまう」事故を防ぐための意図的な仕様だった。

今回の根本原因は、`package.json`の`dependencies`を手で編集した後に`npm install`を実行し忘れ、`package-lock.json`を更新しないままコミット・pushしたことだった。ローカルで動いてしまっていたのは、たまたま以前の`npm install`で作られた`node_modules`が手元に残っており、`npm ci`（＝ロックファイルとの整合性チェックを伴うクリーンインストール）を経由していなかったためだと考えられる。

## 解決手順

### 1. ローカルで`npm install`を実行してロックファイルを更新する

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 409ms

found 0 vulnerabilities
```

`npm install`は`package.json`を見て依存関係を再解決し、不足していた`is-odd`とその依存の`is-number`を`package-lock.json`に書き足してくれる。実行後の`package-lock.json`を確認すると、追加した依存が反映されていた。

```bash
grep -A2 '"is-odd"' package-lock.json
```

```text
    "is-odd": "^3.0.1",
    "left-pad": "^1.3.0"
  }
```

### 2. 更新された`package-lock.json`だけを確認してコミットする

```bash
git diff package-lock.json
```

差分が「新しく追加した依存とそのサブ依存の追記」だけになっていることを確認した。他の依存のバージョンが意図せず変わっていないかもここで必ず見ておく。

```bash
git add package.json package-lock.json
git commit -m "fix: update package-lock.json after adding is-odd dependency"
```

### 3. ロックファイルとの整合性が取れたことを`npm ci`で再確認する

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 352ms

found 0 vulnerabilities
```

先ほどとは違い、エラーなく完了した。ローカルで`npm ci`が通ることを確認してからpushした。

### 4. GitHub Actions側で再実行して確認する

pushしたコミットに対してCIが再実行され、`npm ci`のステップがエラーなく完了し、後続の`npm test`まで進むようになった。

## 動作確認

ローカルで`npm ci`を再実行し、依存関係が正しくインストールされることを確認した。

```bash
npm ci
```

```text
added 3 packages, and audited 4 packages in 352ms

found 0 vulnerabilities
```

CI側のログでも、以前は`npm ci`の直後に出ていた`npm error code EUSAGE`が消え、`npm test`まで到達していることを確認した。念のため、`package.json`と`package-lock.json`が同期しているかどうかを事前にチェックするコマンドも控えておいた。

```bash
npm ci --dry-run
```

このコマンドはインストールを実際には行わず整合性チェックだけを行うため、pushする前のローカル確認に使える。

## まとめ

- `npm ci`は`package.json`を見て依存関係を解決し直すのではなく、`package-lock.json`の内容をそのまま信頼してインストールするコマンドなので、両者がずれていると`EUSAGE`エラーで止まる。
- `dependencies`を手で編集した場合は、必ず`npm install`を実行して`package-lock.json`を更新してからコミットする。ローカルに古い`node_modules`が残っていると、この食い違いに気づかないまま動作確認をパスしてしまうので注意する。
- 同種のエラーは、複数人がそれぞれ別のブランチで依存関係を追加してマージした場合にも起きやすい。マージ後は`rm -rf node_modules && npm ci`をローカルで一度通してからpushすると、CIで初めて気づくより早い段階で検出できる。

## よくある質問

**Q: `npm install`ではなく`npm ci`を使うメリットは何ですか？**
`npm ci`は`package-lock.json`に記録された内容だけを厳密に展開するため、CI環境やチームメンバー間で「ローカルでは動くのに本番やCIでは動かない」という依存関係のズレを防ぎやすくなります。その代わり、ロックファイルが古いままだと今回のように明示的にエラーで止まる仕様です。

**Q: `package-lock.json`の差分レビューで特に見るべき点はどこですか？**
自分が意図して追加・更新した依存とそのサブ依存だけが変わっているかを確認します。関係のないパッケージのバージョンまで大きく変わっている場合、npmのバージョン差やレジストリ側の更新が影響している可能性があるため、`npm ci`をローカルで通してから慎重にコミットするようにしています。

**Q: CIでこのエラーが出た時に、ロックファイルを直さずその場で回避する方法はありますか？**
`npm ci`を`npm install`に置き換えれば一時的にCIは通りますが、それは根本原因を先送りしているだけで、ロックファイルによる再現性の保証が失われます。恒久対応としては、ローカルで`npm install`を実行してロックファイルを正しく更新し、それをコミットするのが適切です。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [Node.jsのバージョンをnvmで管理する方法（Windows/Mac）](/posts/node-version-management-nvm)
