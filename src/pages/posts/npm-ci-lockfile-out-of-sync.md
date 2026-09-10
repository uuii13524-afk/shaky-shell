---
title: 'npm ciが「Missing: … from lock file」で失敗する原因と解決手順'
date: '2026-09-10'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに依存パッケージを手動追記した後にnpm ciを実行すると「Missing: is-odd@3.0.1 from lock file」でCIが失敗する症状を解説。npm installでpackage-lock.jsonを再同期し、npm ciを通す手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci']
en_tags: ['Node.js', 'npm', 'npm ci']
---

## やりたかったこと（症状）

小さなNode.jsのユーティリティスクリプトに、数値が奇数かどうかを判定する処理を急いで足す必要があった。すでに`left-pad`だけを依存関係に持つ小さなプロジェクトで、`is-odd`を使えばすぐ実装できると分かっていたので、`npm install is-odd`を実行する代わりに、手っ取り早く`package.json`の`dependencies`に直接1行追記した。

```json
{
  "dependencies": {
    "left-pad": "^1.3.0",
    "is-odd": "^3.0.1"
  }
}
```

ローカルではこれで`require('is-odd')`が動くだろうと決めつけ、そのままコミットしてpushした。ところがCI（GitHub Actions）のビルドステップで使っている`npm ci`が、見たことのないエラーで落ちた。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: is-odd@3.0.1 from lock file
npm error Missing: is-number@6.0.0 from lock file
```

ローカルで`npm run build`は問題なく通っていたので、最初は「CI側の環境が壊れているのでは」と疑ってしまった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象コマンド: `npm ci`（CI/Dockerビルドで使用。`npm install`ではない）
- 変更内容: `package.json`の`dependencies`に`is-odd`を手動追記（`package-lock.json`は未更新）

## 試したこと

まずローカルでも同じコマンドを再現できるか確認した。ローカルでは`npm install`しか実行していなかったため、試しに`npm ci`をそのまま実行してみた。

```bash
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

ローカルでも同じ`EUSAGE`エラーが再現した。この時点で「CI環境の問題」という仮説は誤りだと分かった。

次に、`package-lock.json`の中身を`is-odd`で検索してみた。

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

`package.json`には`is-odd`が書かれているのに、`package-lock.json`には一切記載がなかった。ここで初めて、`package.json`を直接編集しただけでは`package-lock.json`が自動更新されないことに思い当たった。`npm install`を一度も実行していなかったのが原因だと確信した。

## 原因

`npm ci`は`npm install`とは異なり、依存解決を一切行わない。`package-lock.json`（存在すれば`npm-shrinkwrap.json`）に記録された内容をそのまま`node_modules`へ展開するだけのコマンドで、その代わりに「`package.json`と`package-lock.json`が完全に一致しているか」を厳密にチェックする。1つでも食い違いがあれば、依存解決を試みることなく`EUSAGE`エラーで即座に失敗する仕様になっている。

今回のケースでは、`package.json`の`dependencies`に`is-odd@^3.0.1`を手で追記しただけで、実際にパッケージを解決・ダウンロードする`npm install`を実行していなかった。そのため`package-lock.json`には`is-odd`本体はもちろん、その依存先である`is-number`のエントリも一切存在しない状態になっていた。エラーメッセージの`Missing: is-odd@3.0.1 from lock file`と`Missing: is-number@6.0.0 from lock file`は、まさにこの「lockファイル上に存在しない」という事実をそのまま示していた。

`npm install`はpackage.jsonの変更を見て自動的にlockファイルを更新してくれるが、`npm ci`は意図的にその挙動を持たない。CI/CDやDockerビルドで再現性を担保するために厳格な一致を要求する、npm ci本来の設計であり、バグではなかった。

## 解決手順

### 1. package-lock.jsonの不整合を再確認する

```bash
grep -c '"is-odd"' package-lock.json
```

```text
0
```

`is-odd`のエントリが存在しないことを確認し、lockファイル未更新が原因だと確定させた。

### 2. npm installでlockファイルを再同期する

```bash
npm install
```

```text
added 2 packages, and audited 4 packages in 358ms

found 0 vulnerabilities
```

`npm install`を実行すると、`package.json`に追記した`is-odd`とその依存関係である`is-number`が解決され、`package-lock.json`に書き込まれた。

### 3. package-lock.jsonに反映されたか確認する

```bash
grep -c '"is-odd"' package-lock.json
```

```text
1
```

先ほど`0`だった件数が`1`になり、`package-lock.json`に`is-odd`のエントリが追加されたことを確認できた。

### 4. npm ciが通ることを確認する

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 354ms

found 0 vulnerabilities
```

エラーなく`npm ci`が完了した。`left-pad`の非推奨警告は元から出ていたものでエラーではないため、そのまま無視してよい。

## 動作確認

`node_modules`に想定通りのパッケージが展開されているかを確認した。

```bash
ls node_modules | grep -E "left-pad|is-odd|is-number"
```

```text
is-number
is-odd
left-pad
```

`is-odd`本体と、その依存である`is-number`の両方が正しくインストールされていることを確認できた。この状態で更新した`package.json`と`package-lock.json`をあわせてコミット・pushし、CIの`npm ci`ステップも問題なく通過することを確認した。

## まとめ

- `npm ci`は依存解決を行わず、`package-lock.json`の内容をそのまま復元するコマンドである。`package.json`との間に1件でも不一致があれば`EUSAGE`エラーで即座に失敗する。
- `package.json`を手で編集しただけでは`package-lock.json`は自動更新されない。パッケージを追加・変更したら、必ず`npm install`を実行してlockファイルを同期させる。
- エラーメッセージの`Missing: <package>@<version> from lock file`は、「そのパッケージがlockファイルに存在しない」ことをそのまま示している。同じ形式のエラーが出た場合は、まず`package.json`と`package-lock.json`の該当パッケージ名を`grep`で突き合わせるのが最短の切り分け方法。

## よくある質問

**Q: package.jsonを直接編集せず、npm installコマンド経由で追加すれば防げますか？**
防げます。`npm install <package>`を使えば、`package.json`と`package-lock.json`が同時に更新されるため、今回のような不整合は発生しません。今回のケースは「急いでいたのでエディタで直接1行書き足した」ことが原因でした。

**Q: CIでは常にnpm installではなくnpm ciを使うべきですか？**
はい。`npm ci`は`package-lock.json`をそのまま復元するため、ローカルとCIで依存関係のバージョンが完全に一致し、再現性の高いビルドになります。今回のようにlockファイルとの不整合を早期に検知できる点も、CIで`npm ci`を使う利点です。

**Q: lockファイルをgit管理から外してしまえば、この種のエラーは起きなくなりますか？**
起きなくなりますが、代わりに依存バージョンの再現性が失われ、別の問題（環境ごとに異なるバージョンが入る）を招きます。`package-lock.json`はコミット対象に含めたうえで、変更時は必ず`npm install`で同期する運用が推奨されます。

## 関連記事

- [npmでERESOLVEエラーが出て依存関係のインストールに失敗する原因と解決手順](/posts/npm-eresolve-error)
- [npm installがPermission deniedで失敗する原因と解決手順](/posts/npm-install-permission-denied)
- [npmキャッシュのクリア方法まとめ（npm cache clean）](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [GitHub ActionsでNode.jsのキャッシュを設定する方法](/posts/github-actions-node-cache)
