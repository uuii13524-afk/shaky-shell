---
title: 'npm ciが「package.json and package-lock.json...are in sync」で失敗する原因と解決手順'
date: '2026-08-29'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub Actionsのデプロイワークフローでnpm ciがEUSAGEエラーで失敗し、package.jsonとpackage-lock.jsonが同期していないと表示される症状を解説。npm installでロックファイルを再生成して解決する手順を紹介します。'
ja_tags: ['Node.js', 'npm ci', 'package-lock.json']
en_tags: ['Node.js', 'npm ci', 'package-lock.json']
---

## やりたかったこと（症状）

VPS上のNode.jsアプリを、GitHub ActionsからSSH経由でデプロイしている。ワークフローの中身はシンプルで、依存関係のインストールに`npm install`ではなく`npm ci`を使っている。CIでは決定的な依存解決をしたいので、これは意図した選択だった。

```yaml
- name: Install dependencies
  run: npm ci

- name: Build
  run: npm run build
```

チームメンバーが日付処理用に`dayjs`を追加したいというので、`package.json`の`dependencies`に直接1行追記してpushした。手元では`npm install`を実行し忘れていたが、`node_modules`にはすでに`dayjs`が入っていたため、ローカルの動作確認では何の問題も起きなかった。

そのままpushしたところ、GitHub Actions上の`npm ci`ステップが失敗した。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: dayjs@1.11.23 from lock file
```

手元では一度も再現しなかったため、最初は「CI環境固有のキャッシュ問題か何かだろう」と思い込んだ。

## 環境

- OS: Ubuntu 24.04.4 LTS（GitHub Actions runner / デプロイ先VPSとも同一系統）
- Node.js: v22.22.2
- npm: 10.9.7
- `package-lock.json`: `lockfileVersion: 3`
- CI: GitHub Actions（`npm ci`でクリーンインストール後に`npm run build`）

## 試したこと

まずCI側の問題を疑い、`actions/setup-node`のキャッシュ設定を見直した。`cache: 'npm'`は指定していたが、キャッシュキーは`package-lock.json`のハッシュを使っているだけで、内容自体が壊れているとは考えにくかった。念のためワークフローに`cache: false`を一時的に入れて再実行してみたが、結果は同じエラーだった。

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: false
```

キャッシュが原因でないと分かった時点で、エラーメッセージをもう一度読み直した。`Missing: dayjs@1.11.23 from lock file`という行があり、`package-lock.json`側に`dayjs`のエントリがないことをnpmがそのまま教えてくれていた。ここでようやく「CIの問題ではなく、pushしたコミット自体がおかしい」と気づいた。

手元のリポジトリで確認すると、案の定`package-lock.json`に`dayjs`のエントリが存在しなかった。

```bash
grep '"dayjs"' package-lock.json || echo "dayjs is NOT in package-lock.json"
```

```text
dayjs is NOT in package-lock.json
```

`package.json`だけを手編集して`npm install`を実行しなかったため、依存グラフを再計算する機会がなく、ロックファイルが古いまま取り残されていた。

## 原因

`npm ci`と`npm install`は似ているようで、依存解決の挙動が根本的に違う。`npm install`は`package.json`を正としてロックファイルを必要に応じて更新するが、`npm ci`は逆に`package-lock.json`（または`npm-shrinkwrap.json`）を厳密な正として扱い、`package.json`との整合性が取れていない場合はインストールを実行せずに即座にエラーで終了する。CIやDockerビルドで`npm ci`が推奨されるのはこの厳密さゆえで、「ロックファイル通りに1バイトも狂わずインストールする」ことを保証するための仕様であり、バグではない。

今回起きていたのは次の流れだった。

1. `package.json`の`dependencies`に`dayjs`を手で追記した。
2. `npm install`を実行しなかったため、`package-lock.json`は`dayjs`を認識していない古い状態のまま残った。
3. ローカルの`node_modules`には別の作業でたまたま`dayjs`が入っていたため、`npm run dev`などは問題なく動いてしまい、矛盾に気づけなかった。
4. その状態のまま`package.json`と（古いままの）`package-lock.json`をコミット・pushした。
5. GitHub Actionsのまっさらな環境で`npm ci`が実行され、`package.json`にはあるのに`package-lock.json`にはない`dayjs`を検出してEUSAGEエラーになった。

つまり原因はCI側ではなく、「ロックファイルを更新しないまま`package.json`だけを変更したコミット」そのものにあった。ローカルに既存の`node_modules`が残っていると矛盾を隠してしまう点が、この問題を見つけにくくしている。

## 解決手順

### 1. package-lock.jsonの状態を確認する

```bash
grep '"dayjs"' package-lock.json || echo "dayjs is NOT in package-lock.json"
```

```text
dayjs is NOT in package-lock.json
```

追加した依存がロックファイル側に反映されていないことを確認した。

### 2. npm installでロックファイルを再生成する

```bash
npm install
```

```text
added 1 package, and audited 71 packages in 641ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

`npm install`は`package.json`を見て不足分だけを解決するため、既存の依存関係のバージョンを不必要に変えることはない。今回も`dayjs`関連の1パッケージだけが追加された。

### 3. package-lock.jsonに反映されたことを確認する

```bash
grep -m1 '"dayjs"' package-lock.json
```

```text
"dayjs": "^1.11.11",
```

`dependencies`のエントリにも実体の解決先にも、`dayjs`が正しく追加されていることを確認した。

### 4. ローカルでnpm ciを再現して確認する

CIに再度pushする前に、ローカルでも同じ検証ができる。

```bash
npm ci
```

```text
added 70 packages, and audited 71 packages in 998ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

エラーなく完了した。これでCI環境でも同じ結果になることが期待できる。

### 5. package-lock.jsonごとコミットしてpushする

```bash
git add package.json package-lock.json
git commit -m "fix: sync package-lock.json after adding dayjs"
git push
```

`package.json`だけをコミットしてしまい、`package-lock.json`の更新をコミットに含め忘れるケースもあるため、`git status`で両方がステージされているか必ず確認してからコミットする。

## 動作確認

pushしたコミットでGitHub Actionsのワークフローが再実行され、`npm ci`ステップがエラーなく完了することを確認した。ローカルでも改めてクリーンな状態から検証した。

```bash
rm -rf node_modules
npm ci
```

```text
added 70 packages, and audited 71 packages in 998ms

16 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

`node_modules`を消した状態からでも、ロックファイル通りに依存関係が再現されることを確認できた。

## まとめ

- `npm ci`は`package-lock.json`を厳密な正として扱い、`package.json`との不整合があれば即座にEUSAGEエラーで停止する。これは仕様であり、CIやDockerビルドで再現性を担保するための挙動。
- 手元の`node_modules`に対象パッケージがすでに存在していると、ローカルでは矛盾に気づけない。`package.json`を手編集したら、コミット前に必ず`npm install`を実行してロックファイルを更新する習慣が有効。
- pushする前にローカルで`npm ci`を実行しておけば、CIで初めて失敗するという手戻りを防げる。`package.json`と`package-lock.json`は必ずセットでコミットする。

## よくある質問

**Q: `npm install`ではなく、なぜ`npm ci`をCIやDockerビルドで使うべきなのですか？**
`npm install`は`package.json`のバージョン範囲（`^`や`~`）に応じて、実行のたびに微妙に異なるバージョンをインストールする可能性がある一方、`npm ci`は`package-lock.json`に記録された正確なバージョンだけをインストールする。ビルドのたびに依存関係が変わらないことを保証したいCI・Dockerビルドでは`npm ci`のほうが適している。

**Q: `--legacy-peer-deps`や`--force`を付ければ回避できませんか？**
このエラーはpeer dependencyの衝突ではなく、`package.json`と`package-lock.json`の内容そのものが食い違っていることが原因のため、これらのオプションでは解決しない。根本的な対処は`npm install`でロックファイルを`package.json`に合わせて再生成することのみ。

**Q: `package-lock.json`をコミットしない運用でもよいですか？**
`npm ci`はロックファイルの存在を前提とするコマンドなので、`package-lock.json`をリポジトリから除外すると`npm ci`自体が使えなくなる。依存バージョンを固定したい場合は、必ず`package-lock.json`もコミット対象に含める。

## 関連記事

- [npmでERESOLVEエラーが出てインストールできない原因と解決手順](/posts/npm-eresolve-error)
- [npmインストール時にEACCESパーミッションエラーが出る原因と解決手順](/posts/npm-install-permission-denied)
- [npmキャッシュのクリア方法まとめ](/posts/npm-cache-clear)
- [GitHub Actionsでnode_modulesをキャッシュして高速化する方法](/posts/github-actions-node-cache)
- [nvmでNode.jsのバージョンを切り替える方法](/posts/node-version-management-nvm)
