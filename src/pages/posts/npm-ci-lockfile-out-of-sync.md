---
title: 'npm ciで「lock file does not satisfy」エラーが出る原因と解決手順（2026年 Node.js 22）'
date: '2026-09-08'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'npm ci実行時に「Invalid: lock file''s ... does not satisfy ...」というEUSAGEエラーが出て、CIやクリーンインストールが止まる症状を解説。package.jsonとpackage-lock.jsonのバージョン不一致が原因で、npm installでの再同期とコミット漏れの見分け方を紹介します。'
ja_tags: ['Node.js', 'npm', 'package-lock.json']
en_tags: ['Node.js', 'npm', 'package-lock.json']
---

## やりたかったこと（または「症状」）

依存パッケージのバージョン指定を`package.json`側で手動で書き換えたあと、ローカルの`node_modules`を作り直そうと思い`npm ci`を実行した。

```bash
npm ci
```

```text
npm error code EUSAGE
npm error
npm error `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing.
npm error
npm error Invalid: lock file's left-pad@1.3.0 does not satisfy left-pad@1.1.0
npm error
npm error Clean install a project
npm error
npm error A complete log of this run can be found in: /root/.npm/_logs/2026-09-08T00_09_57_762Z-debug-0.log
```

`npm install`ではなく`npm ci`を使っていたのは、CI環境と同じ「lockfileどおりに厳密インストールする」挙動をローカルでも再現したかったからだった。ところがこの`ci`コマンドが、`package.json`を書き換えた直後に即座にエラーで止まった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- 対象パッケージ: `left-pad`（`package.json`側の指定を`^2.0.0`→`1.1.0`と手で編集、`package-lock.json`は未更新のまま）

## 試したこと

最初は「バージョン指定を書き換えただけで依存関係自体は変えていないのだから、`ci`でも問題なくインストールできるはず」と考えていた。実際に`package.json`の該当行を編集した直後の状態は次のとおりだった。

```json
{
  "name": "npm-ci-test",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "1.1.0"
  }
}
```

この状態で`npm ci`を実行すると、前述のとおり`EUSAGE`エラーで即座に停止した。エラーメッセージ自体に「`npm install`でlock fileを更新してから続けてください」と明記されていたので、まずは`npm ci`をもう一度そのまま実行して再現性を確認したが、当然ながら同じエラーが出るだけだった。

次に、`package-lock.json`を直接エディタで開いて`left-pad`のバージョン欄を手で`1.1.0`に書き換えることも考えたが、`package-lock.json`には`version`だけでなく`resolved`（tarballのURL）や`integrity`（ハッシュ値）も含まれており、これらを手で正しく揃えるのは現実的ではないと判断した。中途半端に書き換えると、今度は`integrity`不一致で別のエラーを引き起こしかねない。

## 原因

`npm ci`は`npm install`と違い、依存関係を解決し直すことをしない。`package-lock.json`に記録された内容が唯一の真実（single source of truth）であり、そこに書かれたバージョン・依存ツリーをそのまま`node_modules`に展開するだけのコマンドになっている。これは再現性を保証するための意図的な設計で、CI環境で「ローカルではビルドできたのにCIでは依存関係の解決結果が微妙に違う」という事故を防ぐ役割を持つ。

そのため、`npm ci`は実行前に必ず整合性チェックを行う。具体的には、`package.json`に書かれた各依存パッケージのバージョン範囲（今回なら`left-pad`の`1.1.0`という完全指定）と、`package-lock.json`に実際に解決済みとして記録されているバージョン（今回は`1.3.0`）を突き合わせ、後者が前者を満たさない場合は`Invalid: lock file's ... does not satisfy ...`というメッセージとともに`EUSAGE`エラーで停止する。

今回のケースでいえば、`package-lock.json`側には以前`^2.0.0`指定時代の名残として`left-pad@1.3.0`（`^2.0.0`は存在しないバージョン範囲だったため、実際には直前の`^1.3.0`指定時に解決された`1.3.0`が残っていた）が記録されており、これは新しい完全指定`1.1.0`を満たさない。壊れているのではなく、「`package.json`だけ書き換えて`package-lock.json`の再生成を忘れた」というワークフロー上の抜けが原因だった。

## 解決手順

### 1. lockfileを更新する

エラーメッセージが指示するとおり、`npm install`を実行して`package-lock.json`を`package.json`の内容に合わせて再生成する。

```bash
npm install
```

```text
npm warn deprecated left-pad@1.1.0: use String.prototype.padStart()

added 1 package, and audited 2 packages in 584ms

found 0 vulnerabilities
```

### 2. lockfileの中身が更新されたことを確認する

```bash
grep -A3 '"node_modules/left-pad"' package-lock.json
```

```text
    "node_modules/left-pad": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/left-pad/-/left-pad-1.1.0.tgz",
      "integrity": "sha512-C8cw/7VpfXLj8Yjlmux8lqb3mfIe3vEXTdik/cXTuzZ8FXJnu45UAWp94XlWWmcW7Yxl74wvHw8w10wIHNGHRQ==",
```

`version`が`1.1.0`に、`resolved`と`integrity`も新バージョンのものに揃って更新されていることを確認する。ここを手で書き換えようとしなくてよい、というのがこの手順の要点になる。

### 3. 更新後の`package-lock.json`をコミットする

```bash
git add package.json package-lock.json
git commit -m "chore: pin left-pad to 1.1.0 and sync lockfile"
```

`package.json`だけをコミットして`package-lock.json`をコミットし忘れると、CI側で同じ`EUSAGE`エラーが再発する。両方セットで変更を反映する必要がある。

## 動作確認

lockfile更新後にあらためて`npm ci`を実行し、今度はエラーなくインストールが完了することを確認した。

```bash
npm ci
```

```text
npm warn deprecated left-pad@1.1.0: use String.prototype.padStart()

added 1 package, and audited 2 packages in 466ms

found 0 vulnerabilities
```

`EUSAGE`エラーが出なくなり、依存パッケージが指定どおりのバージョンでインストールされたことを確認できた。

## ハマったポイント

- `npm ci`はネットワーク経由で依存関係を解決し直すことを一切しない。`package.json`のバージョン範囲と`package-lock.json`の記録済みバージョンを突き合わせるだけなので、`package.json`を手で編集したら必ず`npm install`でlockfileを追従させる習慣が必要だった。
- `package-lock.json`を手動編集する発想は危険。`version`だけ合わせても`integrity`（ハッシュ）が実際のパッケージ内容と食い違えば、今度は改ざん検知でインストールが失敗する。
- CIのビルドログだけを見ていると「依存関係のインストールに失敗した」としか読めず原因が分かりにくいが、エラーメッセージ中の`Invalid: lock file's <pkg>@<lock側のバージョン> does not satisfy <pkg>@<package.json側の指定>`という一行に、原因となったパッケージ名と両方のバージョンがそのまま書かれている。ここを読み飛ばさないことが切り分けの近道だった。

## よくある質問

**Q: `npm ci`の代わりに毎回`npm install`を使えば、このエラー自体を避けられますか？**
避けられますが、それは根本解決ではありません。`npm install`は依存関係を都度解決し直すため、環境によって微妙に異なるバージョンがインストールされる可能性があります。CIやデプロイ時の再現性を重視するなら`npm ci`を使い、エラーが出たら本記事の手順でlockfileを都度同期させる運用が安全です。

**Q: `package-lock.json`を`.gitignore`に入れてリポジトリから外してしまえば解決しませんか？**
おすすめしません。`package-lock.json`はチーム全員・CI環境で同じ依存関係バージョンを再現するための仕組みで、これを外すと今度は「自分の環境では動くのに他の環境では動かない」という別の問題を引き起こします。

**Q: このエラーはpackage.jsonを書き換えたとき以外にも起きますか？**
起きます。他の開発者が依存関係を追加・更新した`package-lock.json`だけをpullし忘れた場合や、マージ時に`package-lock.json`側だけコンフリクト解消を誤った場合にも同じ`EUSAGE`エラーになります。原因は常に「`package.json`と`package-lock.json`の内容が食い違っている」ことなので、対処は同じく`npm install`での再同期です。

## 関連記事

- [npm installで ERESOLVE エラーが出た時の対処法](/posts/npm-eresolve-error)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npm installでEACCES権限エラーが出た時の対処法](/posts/npm-install-permission-denied)
- [Node.jsのバージョンをnvmで管理する方法（Windows/Mac）](/posts/node-version-management-nvm)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
