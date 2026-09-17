---
title: 'npm ciで「in sync」エラーが出てCIが落ちる原因と解決手順'
date: '2026-09-17'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub ActionsのCIでnpm ciを実行すると「package.jsonとpackage-lock.jsonがin syncではない」というEUSAGEエラーで落ちる症状を解説。依存パッケージを追加したのにlockファイルを更新し忘れたことが原因で、npm installで直す手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'CI/CDエラー']
en_tags: ['Node.js', 'npm', 'CI/CD error']
---

## やりたかったこと（症状）

作業中のプロジェクトに新しい依存パッケージ（`is-odd`）を追加したかった。ローカルでは以下のように普通に`package.json`を編集し、`npm install`ではなく手癖で直接インストールコマンドを打たずに、まず`package.json`だけ手で書き換えてから動作確認をしようとした。

```json
{
  "name": "npmci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "1.3.0",
    "is-odd": "3.0.1"
  }
}
```

`package.json`を書き換えた直後、ローカルの`package-lock.json`はまだ古い状態（`is-odd`を追加する前の内容）のままだった。この状態でCIと同じ条件を再現するために`npm ci`を実行したところ、以下のエラーで即座に失敗した。

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

GitHub ActionsのワークフローでもステップはずっとRun: npm ciのままで、ローカルで一度も`npm install`を実行せずに`package.json`だけコミットしてpushした場合、CI側でもまったく同じエラーで落ちることになる。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象コマンド: `npm ci`（`npm install`ではなく、CIで使われるクリーンインストール用コマンド）

## 試したこと

最初は「`package-lock.json`が壊れているのでは」と思い、`node_modules`と`package-lock.json`を両方削除して`npm install`からやり直そうとしたが、それをする前にまず現象を正確に切り分けたかったので、`package-lock.json`はそのままに`npm ci`だけを再実行してエラー内容を読み直した。

```bash
npm ci
```

エラーメッセージの`Missing: is-odd@3.0.1 from lock file`という行が決定的だった。「lock fileに書かれていないパッケージがある」と明示されている。ここで、直前に`package.json`だけを編集して`package-lock.json`を更新していなかったことに気づいた。

念のため、`package-lock.json`の中身を`grep`して`is-odd`が存在するか確認した。

```bash
grep -c "is-odd" package-lock.json
```

```text
0
```

やはり`package-lock.json`側には`is-odd`の情報が一切なかった。`package.json`と`package-lock.json`が食い違っている状態、つまりエラー文にある「in sync」ではない状態そのものだった。

## 原因

`npm ci`は`npm install`と違い、依存関係の解決を一切行わない。`package-lock.json`に書かれている内容だけを厳密に信頼し、その通りに`node_modules`を作り直すコマンドである。そのため、`package.json`に新しい依存を追加しても`package-lock.json`を更新しないまま`npm ci`を実行すると、npmは「指定された依存関係がlockファイルの記録と一致しない」と判断して即座にエラーを出す。

これは仕様であり不具合ではない。`npm ci`が依存解決をスキップして高速・再現可能なインストールを実現している以上、`package.json`と`package-lock.json`の内容が完全に一致していることが前提条件になる。今回は`package.json`を手で編集した後に`npm install`を一度も実行しなかったため、`package-lock.json`が古いまま取り残され、この前提が崩れていた。

CI環境で同じ症状が出る場合の可能性が高い原因は次の2つだった。

1. ローカルで`package.json`を直接編集し、`npm install`を実行せずにコミット・pushした。
2. 複数人で作業している場合、他の人が依存を追加して`package.json`をpushしたが、`package-lock.json`のpushを忘れた（またはコンフリクト解消時に片方だけ取り込んだ）。

## 解決手順

### 1. 症状を再現し、エラー内容を確認する

```bash
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
```

エラーメッセージ自体が対処法（`npm install`でlockファイルを更新する）を明示しているので、まずはこの指示に従う。

### 2. `npm install`でlockファイルを更新する

```bash
npm install
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 315ms

found 0 vulnerabilities
```

`npm install`は`package.json`の内容を見て依存関係を再解決し、`package-lock.json`を追加された`is-odd`とその依存先である`is-number`の情報で更新する。

### 3. `package-lock.json`が更新されたことを確認する

```bash
grep -A2 '"is-odd"' package-lock.json
```

```text
        "is-odd": "3.0.1",
        "left-pad": "1.3.0"
      }
```

`is-odd`のエントリが`package-lock.json`に追加されていることを確認した。

### 4. 更新した`package-lock.json`をコミットする

```bash
git add package.json package-lock.json
git commit -m "chore: add is-odd dependency"
```

`package.json`と`package-lock.json`は必ずセットでコミットする。片方だけをpushすると、CIで再び同じ`EUSAGE`エラーに戻る。

### 5. `npm ci`が通ることを確認する

```bash
rm -rf node_modules
npm ci
```

```text
npm warn deprecated left-pad@1.3.0: use String.prototype.padStart()

added 3 packages, and audited 4 packages in 316ms

found 0 vulnerabilities
```

`node_modules`を一度完全に削除してから`npm ci`を実行し、エラーなくクリーンインストールが完了することを確認した。

## 動作確認

`npm ci`の終了コードも合わせて確認し、CIのステップとして通ることを裏付けた。

```bash
npm ci; echo "exit: $?"
```

```text
added 3 packages, and audited 4 packages in 316ms
found 0 vulnerabilities
exit: 0
```

`exit: 0`が返っており、この状態でGitHub Actionsの`npm ci`ステップも同様に成功することが確認できた。

## まとめ

- `npm ci`は依存解決を行わず、`package-lock.json`の内容をそのまま`node_modules`に反映するコマンド。`package.json`と`package-lock.json`が食い違っていると`EUSAGE`エラーで即座に失敗する。
- 原因のほぼ全ては「`package.json`を編集した後に`npm install`を実行せずコミットした」こと。エラー文の`Missing: <パッケージ名> from lock file`を見れば、どの依存が原因かすぐに分かる。
- 対処は`npm install`でlockファイルを更新し、`package.json`と`package-lock.json`を必ずセットでコミット・pushすること。CIでは`npm ci`を使い続け、ローカルの運用を変える方が安全。

## よくある質問

**Q: CIでも`npm ci`の代わりに`npm install`を使えばこのエラーは起きませんか？**
起きなくなりますが、`npm install`は依存解決を毎回行うため実行時間が長くなり、かつローカルとCIでインストール結果が微妙に食い違う可能性が残ります。エラーを消すために`npm install`に変えるのではなく、`package-lock.json`を正しく更新してコミットする運用に直す方が安全です。

**Q: `package-lock.json`をgitignoreしてリポジトリに含めない運用は問題ないですか？**
`npm ci`は`package-lock.json`が存在しないとそもそも実行できません（別のエラーになります）。lockファイルはライブラリでも必ずコミットし、`.gitignore`に入れないのが基本です。

**Q: 複数人で作業していて、pull時に`package-lock.json`だけコンフリクトした場合はどうすればいいですか？**
コンフリクトマーカーを手で解消しようとせず、`package-lock.json`を削除してから`npm install`を再実行してlockファイルを再生成する方が確実です。その後、差分が意図した依存の追加だけになっているかを確認してコミットします。

## 関連記事

- [npmでERESOLVEエラーが出てインストールできない原因と解決手順](/posts/npm-eresolve-error)
- [GitHub Actionsでnpmキャッシュを設定してCIを高速化する方法](/posts/github-actions-node-cache)
- [DockerfileでNode.jsアプリをビルドする基本とレイヤーキャッシュの効かせ方](/posts/docker-dockerfile-basics)
- [npmキャッシュをクリアする方法とトラブルシューティング](/posts/npm-cache-clear)
