---
title: 'npm ciが「in sync」エラーで失敗する原因と解決手順'
date: '2026-08-08'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub ActionsのCIでnpm ciを実行すると「package.jsonとpackage-lock.jsonが同期していません」というEUSAGEエラーで失敗する症状を解説。マージコンフリクト解消時のミスが原因になるケースと、npm installでロックファイルを再同期させる手順を紹介します。'
ja_tags: ['Node.js', 'npm', 'GitHub Actions']
en_tags: ['Node.js', 'npm', 'GitHub Actions']
---

## やりたかったこと（症状）

APIクライアント用に`axios`を追加するプルリクエストを作った。ローカルで動作確認まで済ませてpushし、GitHub Actions上のCIが通ることを確認するだけのはずだった。

```bash
npm install axios
git add package.json package-lock.json
git commit -m "feat: add axios for API client"
```

ところが直後にmainブランチで別PRがマージされたため、pushする前に一度mainを取り込む必要が生じた。

```bash
git fetch origin main
git merge origin/main
```

`package-lock.json`でコンフリクトが発生した。差分を細かく見るのが面倒だったので、「自分の変更を優先すればいいはず」と判断し、`--ours`で解決した。

```bash
git checkout --ours package-lock.json
git add package-lock.json
git commit -m "merge: resolve lockfile conflict"
git push
```

ローカルでは`npm run build`も`npm test`も問題なく通っていたので安心してpushしたが、GitHub Actions側のCIが赤くなった。ログを開くと以下のエラーだった。

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Missing: axios@1.7.7 from lock file
npm error
npm error Clean install a project
```

ローカルでは再現しないのに、CIだけが落ちるという状態だった。

## 環境

- OS: macOS Sonoma 14.5（ローカル）／ Ubuntu 22.04（GitHub Actions `ubuntu-latest`）
- Node.js: 20.11.1
- npm: 10.2.4
- CI: GitHub Actions、`actions/setup-node@v4` + `npm ci`
- 該当パッケージ: `axios@1.7.7`

## 試したこと

最初はCIのキャッシュが古いのではと疑い、GitHub Actionsのキャッシュを手動で削除して再実行した。

```yaml
# .github/workflows/ci.yml（該当部分）
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'
- run: npm ci
```

結果は同じエラーで失敗した。次に、ローカルの`node_modules`を消して`npm ci`をローカルでも実行してみた。

```bash
rm -rf node_modules
npm ci
```

```text
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error Missing: axios@1.7.7 from lock file
```

ローカルでも同じエラーが出た。これまで`npm install`しか使っておらず`npm ci`を実行していなかったため、「動いているように見えていただけ」だったと分かった。`npm install`はpackage.jsonとlockファイルにずれがあっても不足分を補ってインストールしてしまうため、ずれに気づけていなかった。

`package-lock.json`の中身を確認すると、`dependencies`に`axios`のエントリが存在しなかった。

```bash
grep -c '"axios"' package-lock.json
```

```text
0
```

一方`package.json`には`axios`が追加されている。ここで、直前のマージコンフリクト解消で`git checkout --ours`を使ったことを思い出した。

## 原因

`git checkout --ours package-lock.json`は、コンフリクトの自分側（この場合はマージ元のfeatureブランチ）の内容をそのまま採用するコマンドである。マージコンフリクトが起きた時点の`package-lock.json`は、`axios`追加前の古いコミット時点の内容だったため、`--ours`で解決した結果、`package.json`には`axios`が残ったまま`package-lock.json`だけが追加前の状態に巻き戻ってしまった。

`npm install`はこのズレを許容し、`package.json`を正として不足分を自動でインストールしてしまうため、ローカル開発では問題が表面化しない。一方`npm ci`は「`package-lock.json`が`package.json`と厳密に一致していること」を前提にした再現性重視のコマンドで、一致しない場合はインストールを行わずEUSAGEエラーで停止する仕様になっている。GitHub ActionsのワークフローがCIの高速化・再現性のために`npm ci`を使っていたため、このズレがCIでのみ露呈した。

## 解決手順

### 1. ローカルでロックファイルを再生成する

`package.json`を正として、`package-lock.json`を再同期させる。

```bash
npm install
```

```text
added 1 package, and audited 842 packages in 3s
```

### 2. 差分を確認する

```bash
git diff package-lock.json | head -20
```

```diff
+    "node_modules/axios": {
+      "version": "1.7.7",
+      "resolved": "https://registry.npmjs.org/axios/-/axios-1.7.7.tgz",
+      "integrity": "sha512-S4kL7XrjYTOVwqZH2WVGGNcpaVMLtQmxWn0LN8m6dV0KKa3sB79pDNwbwSlmiVfmSaYbAX6P4x8bIReXQTLyxg==",
```

`axios`のエントリが追加されたことを確認した。

### 3. npm ciで再同期を検証する

```bash
rm -rf node_modules
npm ci
```

```text
added 843 packages, and audited 843 packages in 8s
found 0 vulnerabilities
```

エラーなくインストールが完了した。

### 4. コミットしてpushする

```bash
git add package-lock.json
git commit -m "fix: resync package-lock.json with package.json"
git push
```

## 動作確認

pushしたコミットでGitHub ActionsのCIが再実行されたことを確認し、`npm ci`のステップが成功していることを確認した。

```text
Run npm ci
added 843 packages, and audited 843 packages in 6s
found 0 vulnerabilities
```

ビルド・テストのステップも問題なく完走し、PRのステータスチェックがすべてグリーンになった。

## ハマったポイント

`npm install`と`npm ci`の挙動差を理解していなかったことが根本の見落としだった。ローカルでは常に`npm install`を使っていたため、`package.json`と`package-lock.json`にズレがあってもエラーにならず、CIで`npm ci`を使って初めて表面化した。マージコンフリクトで`package-lock.json`を`--ours`や`--theirs`で機械的に解決するのは危険で、依存関係を変更したコミットが絡む場合は解決後に必ず`npm install`を実行してロックファイルを再生成するべきだった。

## よくある質問

**Q: `npm install`と`npm ci`はどちらを使うべきですか？**
ローカル開発では依存関係を追加・更新する操作を伴うため`npm install`が適しています。CIやデプロイなど「lockファイルの内容を厳密に再現したい」場面では`npm ci`を使うべきです。`npm ci`は`node_modules`を毎回削除してからクリーンインストールするため、ローカル環境との差分にも気づきやすくなります。

**Q: マージコンフリクトが起きた`package-lock.json`はどう解決するのが正しいですか？**
`--ours`や`--theirs`で機械的に解決せず、まず該当コミットを`git status`や`git diff`で確認し、双方の`package.json`の変更を反映した状態にしてから`npm install`でロックファイルを再生成するのが安全です。ロックファイル自体を手動で編集するのは避けます。

**Q: CIだけでこのエラーに気づく仕組みを事前に作れますか？**
はい。pre-commitフックやpre-pushフックで`npm ci --dry-run`相当のチェックを走らせる、あるいはPRのCIワークフローに`npm ci`のステップを早い段階で置くことで、マージやレビューの前にズレを検知できます。

## 関連記事

- [npm ERR! ERESOLVEの原因と解決方法](/posts/npm-eresolve-error)
- [npm installがEACCESで失敗する原因と解決方法](/posts/npm-install-permission-denied)
- [git pull時のマージコンフリクト解消方法](/posts/git-pull-merge-conflict)
- [GitHub Actionsでのシークレット利用方法](/posts/github-actions-secrets)
- [package.jsonのscripts活用法](/posts/npm-package-json-scripts)
