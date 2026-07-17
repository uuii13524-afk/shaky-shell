---
title: 'npm installで ERESOLVE エラーが出た時の対処法'
date: '2026-07-17'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Node.js', 'npm', 'ERESOLVE', '依存関係']
en_tags: ['Node.js', 'npm', 'ERESOLVE', 'dependency']
---

## やりたかったこと（または「症状」）

React 17で動いているNext.jsプロジェクトに、テスト環境を整えるため `@testing-library/react` の最新版を追加しようとした。いつも通り `npm install --save-dev @testing-library/react` を叩いたところ、ターミナルが真っ赤なエラーで埋め尽くされてインストールが止まった。

```text
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR!
npm ERR! While resolving: my-app@0.1.0
npm ERR! Found: react@17.0.2
npm ERR! node_modules/react
npm ERR!   react@"^17.0.2" from the root project
npm ERR!
npm ERR! Could not resolve dependency:
npm ERR! peer react@"^18.0.0" from @testing-library/react@14.0.0
npm ERR! node_modules/@testing-library/react
npm ERR!   dev @testing-library/react@"^14.0.0" from the root project
npm ERR!
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --force or --legacy-peer-deps
npm ERR! to accept an incorrect (and potentially broken) dependency resolution.
npm ERR!
npm ERR! See /home/user/.npm/eresolve-report.txt for a full report.
```

`node_modules` は生成されず、`package-lock.json` も更新されない。これまで何百回も `npm install` してきたが、ここまで長いエラーは初めてで、何が原因なのか見当もつかなかった。

## 環境

- OS: Ubuntu 22.04 LTS
- Node.js: v20.11.0
- npm: 10.2.4
- React: 17.0.2
- @testing-library/react: 14.0.0（インストールしようとしたバージョン）

## 試したこと

最初はエラーメッセージの下部に書かれていた `npm ERR! See /home/user/.npm/eresolve-report.txt for a full report.` の意味が分からず、単純にもう一度 `npm install` を実行し直した。

```text
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

結果は同じで、まったく同じエラーが再び表示されただけだった。ネットワークの一時的な不具合ではなく、依存関係そのものに問題があると分かった。

次に、キャッシュが壊れているのではないかと考えて `npm cache clean --force` を実行してから再インストールした。

```bash
npm cache clean --force
npm install --save-dev @testing-library/react
```

キャッシュクリア自体は成功したが、インストールは同じ `ERESOLVE unable to resolve dependency tree` で止まった。キャッシュの問題ではなく、`package.json` に書かれたパッケージ同士のバージョン要求が矛盾していることが原因だと分かった。

## 原因

npm 7以降は、インストール対象パッケージが `peerDependencies` に指定しているバージョン条件を厳密にチェックするようになった。今回のケースでは、プロジェクトの `react` は `17.0.2` で固定されているのに対し、`@testing-library/react@14` は `peerDependencies` で `react@^18.0.0` を要求していた。

npmは「ルートプロジェクトが要求するreact 17」と「新しく入れようとしたパッケージが要求するreact 18」の両方を同時に満たす組み合わせを解決できないため、依存関係ツリーの構築自体を中断してエラーを出す。npm 6以前はpeerDependenciesの不一致があっても警告だけで処理を進めていたが、npm 7からはこれがエラー扱いになった点が、過去にnpmを使っていた人が戸惑うポイントになっている。

## 解決方法

### 1. 根本原因のバージョンを揃える

```bash
npm install --save-dev @testing-library/react@13
```

```text
added 1 package, and audited 842 packages in 4s
found 0 vulnerabilities
```

`@testing-library/react@13` は `peerDependencies` で `react@^16.8.0 || ^17.0.0 || ^18.0.0` を許容しているため、プロジェクトのreact 17と矛盾せずインストールできる。エラーメッセージに出てきたパッケージのCHANGELOGやリリースノートを確認し、今使っているメジャーバージョンと噛み合うバージョンまで下げるのが最も安全な直し方になる。

### 2. どうしてもバージョンを揃えられない場合は --legacy-peer-deps を使う

```bash
npm install --save-dev @testing-library/react --legacy-peer-deps
```

```text
npm warn ERESOLVE overriding peer dependency
npm warn Found: react@17.0.2
npm warn Could not resolve dependency:
npm warn peer react@"^18.0.0" from @testing-library/react@14.0.0
added 7 packages, and audited 849 packages in 6s
```

`--legacy-peer-deps` を付けると、npm 6以前と同じくpeerDependenciesの不一致を警告(warn)だけに留めてインストールを続行する。ビルドやテストの動作自体には影響しないことが多いが、想定外のReact APIが呼ばれた場合に実行時エラーになるリスクがあるため、根本解決の1番目を優先し、これは応急処置として使う。

### 3. インストール後、依存関係ツリーで確認する

```bash
npm ls react
```

```text
my-app@0.1.0
├── react@17.0.2
└─┬ @testing-library/react@13.4.0
  └── react@17.0.2 deduped
```

`npm ls react` で `react` がプロジェクト全体で1つのバージョンに統一されているか確認できる。複数バージョンが混在している場合は、後述の「よくある質問」にある `npm ls` での深掘りが必要になる。

## ハマったポイント

- エラーメッセージ内の `While resolving` と `Could not resolve dependency` の2つのブロックを読み飛ばし、どのパッケージ同士が衝突しているのか特定できずに30分ほど無駄にした。上のブロックが「今何を入れようとしているか」、下のブロックが「それを妨げている要求」を示している
- `--force` と `--legacy-peer-deps` を混同していた。`--force` はキャッシュ内の壊れたパッケージも含めて強制的に再取得・再構築するオプションで、`--legacy-peer-deps` はpeerDependenciesのチェックだけを緩めるオプション。今回は後者だけで十分だったのに、最初に `--force` を使って無関係なパッケージまで再インストールされてしまった
- `package-lock.json` を手動で編集してバージョン番号だけ書き換えようとしたら、`npm install` 実行時に `npm ERR! Invalid: lock file's react@18.2.0 does not satisfy react@17.0.2` という別のエラーが出た。lockファイルは直接編集せず、必ずnpmコマンド経由で更新する
- CI環境（GitHub Actions）では `npm ci` を使っていたため、ローカルで `--legacy-peer-deps` 付きで解決したはずのインストールがCI上では同じERESOLVEエラーで失敗した。`npm ci` は `.npmrc` の設定を読むので、`.npmrc` に `legacy-peer-deps=true` を追記してCIとローカルの挙動を揃える必要があった

## よくある質問

**Q: `npm install --force` と `--legacy-peer-deps` はどちらを使えばいいですか？**
まずは `--legacy-peer-deps` を試す。peerDependenciesのチェックだけを緩めるため影響範囲が小さい。`--force` はキャッシュや既存パッケージまで強制的に上書きするため、意図しない副作用が起きやすい。両方試してもエラーが解消しない場合のみ `--force` を検討する。

**Q: ERESOLVEエラーを毎回オプション付きで回避するのが面倒です。設定で固定できますか？**
プロジェクト直下に `.npmrc` を作成し、`legacy-peer-deps=true` を1行書いておくと、以降は `npm install` だけでオプションなしでも同じ挙動になる。

```text
# .npmrc
legacy-peer-deps=true
```

**Q: どのパッケージ同士が競合しているのか、エラーメッセージだけでは分かりにくいです。**
`npm ls <パッケージ名>` を実行すると、そのパッケージが依存関係ツリーのどこから複数バージョン要求されているかツリー表示で確認できる。

```bash
npm ls react
```

## 関連記事

- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
