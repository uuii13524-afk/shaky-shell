---
title: 'npm ci が EUSAGEで失敗する「package-lock.jsonが同期していません」エラーの原因と解決手順'
date: '2026-08-05'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'npm ciを実行するとEUSAGEエラーでインストールが止まり、package.jsonとpackage-lock.jsonが同期していないと言われる症状を解説。原因を切り分け、ロックファイルを正しく更新して再度npm ciを通すまでの手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'npm ci']
en_tags: ['Node.js', 'npm', 'npm ci']
---

## やりたかったこと（症状）

CI環境で使っているDockerfileと同じ手順をローカルでも再現しようとして、`npm install`ではなく`npm ci`でクリーンインストールを試した。

```bash
rm -rf node_modules
npm ci
```

ところが途中で止まり、次のエラーで終了した。

```text
npm ERR! code EUSAGE
npm ERR!
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm ERR!
npm ERR! Invalid: lock file's date-fns@2.30.0 does not satisfy date-fns@3.6.0
npm ERR!
npm ERR! Missing: zod@3.23.8 from lock file
```

`npm install`のときは何も問題なく通っていたのに、`npm ci`だけがこのエラーで落ちる状況だった。

## 環境

- OS: Ubuntu 22.04（WSL2）
- Node.js: v20.11.1
- npm: 10.2.4
- リポジトリ: 個人開発中のNext.jsプロジェクト（`package-lock.json`をGit管理下に置いている）

## 試したこと

まず`npm install`をもう一度実行してみたところ、こちらは特にエラーも警告もなく成功した。

```bash
npm install
```

`node_modules`は正常に作られたので、依存関係の解決自体には問題がなさそうだった。次に、`package.json`と`package-lock.json`の該当箇所を見比べてみた。

```bash
grep -A2 '"date-fns"' package.json
grep -A2 '"date-fns"' package-lock.json | head -5
```

`package.json`側は`"date-fns": "^3.6.0"`と書かれているのに対し、`package-lock.json`の`packages`セクションには`date-fns`のバージョンが`2.30.0`のまま残っていた。さらに`zod`は`package.json`の`dependencies`に追加済みだったが、`package-lock.json`には一切エントリがなかった。

ここで直近のコミット履歴を確認した。

```bash
git log --oneline -- package.json package-lock.json | head -5
```

出てきたのは、`package.json`の`dependencies`だけを手で書き換えたコミットだった。エディタで`date-fns`のバージョン指定を直接`^2.x`から`^3.x`に書き換え、`zod`を新規追加した際に、`npm install`を実行し忘れてそのまま`git commit`していた。

## 原因

`npm install`は`package.json`と`package-lock.json`の食い違いを許容し、その場で依存解決をやり直して両方を更新できる。一方`npm ci`は「`package-lock.json`に書かれている内容だけを信頼してそのままインストールする」動作のため、`package.json`との内容が一致しない場合はインストールを進めずにエラーで止まる仕様になっている。

今回のケースでは、`package.json`を直接手編集してバージョン指定を変えたにもかかわらず、`npm install`を実行して`package-lock.json`を追従更新するステップを踏まずにコミットしてしまったことが原因だった。ローカルでは`npm install`しか使っていなかったため気づかず、CI用に`npm ci`を試したタイミングで初めて表面化した形になる。

## 解決手順

`package.json`の内容に合わせて`package-lock.json`を再生成する。

```bash
npm install
```

このコマンドで`package-lock.json`が`package.json`の依存内容に沿って更新される。差分を確認する。

```bash
git diff package-lock.json | head -30
```

`date-fns`のバージョンが`3.6.0`系に更新され、`zod`のエントリが追加されたことを確認した。更新されたロックファイルをコミットする。

```bash
git add package-lock.json
git commit -m "fix: update package-lock.json to match package.json"
```

コミット後、改めて`npm ci`が通るか確認する。

```bash
rm -rf node_modules
npm ci
```

## 動作確認

```bash
npm ci
```

```text
added 412 packages, and audited 413 packages in 8s

52 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

エラーなくインストールが完了し、`node_modules`が生成されたことを確認した。念のためインストールされたバージョンも確認しておく。

```bash
npm ls date-fns zod
```

```text
myapp@1.0.0 /home/dev/myapp
├── date-fns@3.6.0
└── zod@3.23.8
```

`package.json`で指定した通りのバージョンが入っていることを確認できた。

## ハマったポイント

- `package.json`を手で直接編集した後は、たとえ依存関係の追加が1件だけでも必ず`npm install`を実行して`package-lock.json`を同期させる必要がある。「バージョン指定を書き換えただけだから大丈夫」という思い込みが原因だった
- ローカル開発中はずっと`npm install`だけを使っていたため、ロックファイルのズレに気づく機会がなかった。CI・Dockerビルドなど`npm ci`を使う環境を用意して初めて検知できる問題だった
- エラーメッセージの`Invalid: lock file's ... does not satisfy ...`は、パッケージ名とバージョンが具体的に出るため、どのパッケージが原因かはすぐ特定できる。焦って`package-lock.json`を丸ごと削除して作り直す前に、まずこのメッセージで差分箇所を絞り込むべきだった

## よくある質問

**Q: `package-lock.json`を削除してから`npm install`し直しても直りますか？**
直る。ただしその場合、他の依存パッケージのバージョンも意図せず更新されてしまう可能性があるため、まずは`npm install`で差分更新できないか試す方が安全。

**Q: CIでこのエラーを未然に防ぐ方法はありますか？**
プルリクエストのCIに`npm ci`を含めておけば、`package-lock.json`の同期漏れがマージ前に検知できる。`npm install`だけをCIで使っていると同じ問題を見逃す。

**Q: `npm-shrinkwrap.json`がある場合も同じ対処でよいですか？**
同じ考え方でよい。`npm-shrinkwrap.json`は`package-lock.json`と同様に`package.json`との整合性が求められるため、手編集後は`npm install`で同期させる。

## 関連記事

- [npm ERR! ERESOLVEエラーの原因と解決手順](/posts/npm-eresolve-error)
- [npmキャッシュのクリア方法まとめ](/posts/npm-cache-clear)
- [npm installで権限エラーが出るときの対処法](/posts/npm-install-permission-denied)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [GitHub Actionsでnpmキャッシュを使う方法](/posts/github-actions-node-cache)
