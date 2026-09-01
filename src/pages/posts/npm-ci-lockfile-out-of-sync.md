---
title: 'npm ciで「in sync」エラーが出てCIが失敗する原因と解決手順'
date: '2026-09-01'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'package.jsonに依存パッケージを手動で追記した直後、npm ciがEUSAGEエラーで失敗する症状を解説。package-lock.jsonとの不整合が原因で、npm installでロックファイルを更新して解決する手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

ローカルで動かしているツール用のNode.jsプロジェクトに、日付操作用のライブラリ`dayjs`を追加しようとした。急いでいたので`npm install dayjs`を叩かず、`package.json`の`dependencies`に直接1行書き足すという手を使った。

```json
"dependencies": {
  "lodash": "^4.17.21",
  "dayjs": "^1.11.10"
}
```

その状態のままコミットする前に、ローカルでCIと同じ手順を再現しようと`npm ci`を実行したところ、インストールが1つも走らずにいきなりエラーで止まった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
npm error
npm error Clean install a project
```

普段`npm install`で追加する時はこんなエラーを見たことがなかったので、最初は`package.json`の書き方自体が間違っているのかと思い込み、JSON構文をしばらく見直していた。

## 環境

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象パッケージ: `dayjs@^1.11.10`（`package.json`にのみ手動追記した状態）
- ロックファイル形式: `lockfileVersion: 3`

## 試したこと

まず`package.json`のJSON構文を疑い、カンマの付け忘れやクォートの閉じ忘れがないか確認した。

```bash
node -e "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))"
```

エラーなく通ったので、JSON自体は正しいことが分かった。次に、`npm ci`をもう一度そのまま実行してみたが、結果は変わらなかった。

```text
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync.
```

ここでようやくエラーメッセージの2行目、`Missing: dayjs@1.11.23 from lock file`を読み直した。`package-lock.json`の中身を`grep`してみると、案の定`dayjs`のエントリがどこにも存在しなかった。

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`package.json`には書いたが`package-lock.json`には一切反映されていない、という単純な不整合だった。

## 原因

`npm ci`は`npm install`と違い、依存関係の解決を一切行わない。`package-lock.json`（または`npm-shrinkwrap.json`）に記録された内容だけを信頼し、その通りに`node_modules`を再構築するコマンドになっている。これはCI環境で「常に同じ依存関係ツリーを再現する」ことを保証するための仕様で、`npm install`のように`package.json`のバージョン範囲（`^1.11.10`など）を見て解決し直す、という柔軟な処理はしない。

今回のケースでは、`package.json`に`dayjs`を手で追記しただけで、`package-lock.json`側の更新コマンドを一度も実行していなかった。そのため`npm ci`から見ると「`package.json`は`dayjs`を要求しているのに、ロックファイルにはその解決結果が記録されていない」という矛盾した状態になり、`npm`は勝手に解決せずEUSAGEエラーで処理を止める。これは壊れているのではなく、`npm ci`が本来の役割どおりに「信頼できない状態でのインストールを拒否した」だけだと分かった。

## 解決手順

### 1. package-lock.jsonの現状を確認する

```bash
grep -c '"dayjs"' package-lock.json
```

```text
0
```

`dayjs`のエントリが存在しないことを確認し、ロックファイル側が古いままであることを確定させた。

### 2. npm installでロックファイルを更新する

```bash
npm install
```

```text
added 1 package, and audited 3 packages in 755ms

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

`npm install`は`package.json`を読み、不足している`dayjs`を解決して`node_modules`にインストールすると同時に、`package-lock.json`にも解決結果を書き込む。`npm audit`の警告は今回の依存不整合とは無関係な既知の脆弱性通知なので、まずは無視して進めた。

### 3. package-lock.jsonに反映されたか確認する

```bash
grep -A2 '"dayjs"' package-lock.json
```

```text
"dayjs": "^1.11.10",
"lodash": "^4.17.21"
}
```

`dependencies`欄に加えて、`node_modules/dayjs`のエントリとして解決済みバージョン`1.11.23`も記録されていることを確認した。

### 4. npm ciを再実行してCIと同じ手順を再現する

```bash
npm ci
```

```text
added 2 packages, and audited 3 packages in 1s

1 high severity vulnerability

To address all issues, run:
  npm audit fix
```

エラーなく`node_modules`が再構築され、`npm ci`が正常終了した。

## 動作確認

インストールされた`dayjs`が意図したバージョンで解決されているか、実際に読み込んで確認した。

```bash
node -e "console.log(require('./node_modules/dayjs/package.json').version)"
```

```text
1.11.23
```

`package.json`で指定した`^1.11.10`の範囲内で、`package-lock.json`に記録された`1.11.23`が実際にインストールされていることを確認できた。この状態であれば、CI環境で`npm ci`を実行しても同じ結果が再現される。

## まとめ

- `npm ci`は`package-lock.json`の内容だけを信頼して再現インストールを行うコマンドで、`package.json`のバージョン範囲から自動で依存解決はしない。
- `package.json`に依存パッケージを手動追記しただけの状態では`package-lock.json`が古いままになり、`npm ci`は`EUSAGE`エラーで止まる。エラーメッセージの`Missing: <パッケージ名>@<バージョン> from lock file`が原因の特定に直結する。
- 依存パッケージの追加・変更は、`package.json`を手で編集する場合でも最後に必ず`npm install`を1回実行し、`package-lock.json`を同期させてからコミットする。CIで`npm ci`を使っているプロジェクトほど、この同期漏れがローカルでは気づかれずCIだけ失敗する原因になりやすい。

## よくある質問

**Q: `npm install`ではなく`npm ci`を使うメリットは何ですか？**
`npm ci`は`package-lock.json`の内容をそのまま信頼して`node_modules`を再構築するため、依存解決のブレがなく、実行速度も`npm install`より速い。CI環境やDockerビルドなど「常に同じ依存関係を再現したい」場面に向いている。

**Q: `package.json`と`package-lock.json`のどちらが正しいか分からなくなった場合はどうすればいいですか？**
`package-lock.json`を一度削除して`node_modules`ごと`npm install`をやり直すと、`package.json`の内容から依存関係を解決し直せる。ただしその場合、間接依存のバージョンが変わる可能性があるため、テストを通してから変更をコミットするのが安全。

**Q: `Missing`ではなく`Invalid`というエラーが出ることもありますが、違いは何ですか？**
`Missing`はロックファイルに該当パッケージの記録が存在しない場合、`Invalid`は記録はあるがバージョンが`package.json`の要求範囲と食い違っている場合に出る。どちらも対処法は同じで、`npm install`を実行してロックファイルを最新の状態に合わせ直せば解消する。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npm installでpermission deniedが出た時の対処法](/posts/npm-install-permission-denied)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
