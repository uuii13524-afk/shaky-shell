---
title: 'git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順'
date: '2026-08-19'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git clone直後、.gitmodulesはあるのにsubmoduleのディレクトリが空のままで、npm run buildがモジュール解決エラーで失敗する症状を解説。git submodule update --init --recursiveで実体を取得するまでの手順を紹介します。'
ja_tags: ['Git', 'Git Submodule', 'ビルドエラー']
en_tags: ['Git', 'Git Submodule', 'build error']
---

## やりたかったこと（症状）

社内の`internal-dashboard`リポジトリを新しいマシンにセットアップしようとした。このリポジトリは共通UIコンポーネント群を`packages/ui-kit`というsubmoduleとして参照している。

```bash
git clone git@github.com:example-org/internal-dashboard.git
cd internal-dashboard
npm install
npm run build
```

`npm install`までは問題なく終わったが、`npm run build`でビルドが止まった。

```text
[vite]: Rollup failed to resolve import "../../packages/ui-kit/dist/index.js" from "src/App.tsx".
This is most likely unintended because it can break your application at runtime.
If you do want to externalize this module explicitly add it to
`build.rollupOptions.external`
```

`packages/ui-kit`というディレクトリ自体は存在していたので、最初はビルド設定側の解決パス（`vite.config.ts`のエイリアス設定）がおかしいのだと思い込み、そちらを疑った。

## 環境

- OS: Ubuntu 24.04 LTS
- Git: 2.45.2
- Node.js: v20.14.0
- npm: 10.7.0
- リポジトリ: `internal-dashboard`（GitHub、submoduleとして`packages/ui-kit`を参照）
- ビルドツール: Vite 5.3（Astroではなく素のReact+Viteプロジェクト）

## 試したこと

まず`vite.config.ts`のエイリアス設定を確認したが、パス自体は正しかった。次に、`packages/ui-kit`の中身を直接見てみた。

```bash
ls -la packages/ui-kit
```

```text
total 8
drwxr-xr-x  2 user user 4096 Aug 19 10:02 .
drwxr-xr-x 12 user user 4096 Aug 19 10:02 ..
```

ディレクトリはあるのに中身が一切ない。ここで初めて「ビルド設定の問題ではなく、そもそもファイルが存在していない」ことに気づいた。

念のため`git status`も確認したが、何も異常を示さなかった。

```bash
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

`git status`が「clean」と報告するため、submoduleが未取得であることに気づきにくい。これに惑わされて、しばらくビルド設定側を疑い続けてしまった。

次に`.gitmodules`の中身を確認した。

```bash
cat .gitmodules
```

```text
[submodule "packages/ui-kit"]
	path = packages/ui-kit
	url = git@github.com:example-org/ui-kit.git
	branch = main
```

submoduleとしての定義自体は正しく存在している。ここでようやく`git submodule status`を実行してみた。

```bash
git submodule status
```

```text
-4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit
```

行頭に`-`（マイナス記号）が付いている。これがsubmodule未初期化を示すサインだった。

## 原因

`git clone`は、対象リポジトリに`.gitmodules`ファイルと、submoduleが指す特定コミットへの参照（gitlink）だけを取得する。submoduleの実際のファイル内容までは、デフォルトでは取得しない。そのため`packages/ui-kit`というディレクトリ自体はcloneの時点で作られるが、中身は空のまま残る。

`git submodule status`の出力先頭に付く記号には意味があり、`-`は「未初期化（登録されているがローカルに一度もcheckoutされていない）」、`+`は「初期化済みだが、記録されているコミットとローカルの内容が食い違っている」、記号なしは「初期化済みかつ最新」を意味する。今回は`-`だったので、`init`すら行われていない状態だった。

さらに厄介なのは、`git status`が通常このsubmodule未初期化を警告しない点だった。`packages/ui-kit`は追跡対象のgitlinkとして記録されているだけで、その配下のファイル状態はデフォルトの`git status`が関知する範囲外になる。結果として、リポジトリ自体は「clean」に見えるのに、ビルドだけが失敗するという分かりにくい状況が発生していた。

## 解決手順

### 1. submoduleの状態を確認する

```bash
git submodule status
```

```text
-4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit
```

`-`が付いていることを再確認し、未初期化だと確定させた。

### 2. submoduleを初期化して実体を取得する

```bash
git submodule update --init --recursive
```

```text
Submodule 'packages/ui-kit' (git@github.com:example-org/ui-kit.git) registered for path 'packages/ui-kit'
Cloning into '/home/user/internal-dashboard/packages/ui-kit'...
Submodule path 'packages/ui-kit': checked out '4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f'
```

`--recursive`を付けているのは、`ui-kit`自体がさらに別のsubmoduleを持つ可能性を考慮したため（今回は実際にはネストしたsubmoduleはなかったが、癖として付けている）。

### 3. ディレクトリの中身を再確認する

```bash
ls packages/ui-kit
```

```text
dist  package.json  src  tsconfig.json
```

空だったディレクトリに、期待通りのファイル一式が展開されていた。

### 4. submoduleの状態を再確認する

```bash
git submodule status
```

```text
 4f2a9c1e8b3d7a6f5e4d3c2b1a0f9e8d7c6b5a4f packages/ui-kit (heads/main)
```

先頭の`-`が消え、記録されているコミットと一致していることが分かる。

### 5. ビルドを再実行する

```bash
npm run build
```

```text
vite v5.3.1 building for production...
✓ 214 modules transformed.
dist/index.html                  0.46 kB
dist/assets/index-C8kQmZ1a.js  186.32 kB
✓ built in 3.12s
```

エラーなくビルドが完了した。

## 動作確認

念のため、まっさらなディレクトリに`--recurse-submodules`を付けて再クローンし、初回からsubmoduleが実体として取得されることを確認した。

```bash
git clone --recurse-submodules git@github.com:example-org/internal-dashboard.git internal-dashboard-check
cd internal-dashboard-check
ls packages/ui-kit
```

```text
dist  package.json  src  tsconfig.json
```

`clone`の時点で`packages/ui-kit`の中身が展開されていることを確認できた。

## まとめ

- `git clone`はsubmoduleの定義（`.gitmodules`）と参照コミットだけを取得し、実際のファイル内容は取得しない。ディレクトリ自体は作られるため、`ls`で気づくまで見落としやすい。
- `git status`はデフォルトでsubmodule未初期化を警告しないため、「リポジトリはcleanなのにビルドだけ失敗する」という分かりにくい症状になる。`git submodule status`を実行し、行頭に`-`が付いていないか確認するのが確実な切り分け方法。
- 恒久対策として、新規cloneは`git clone --recurse-submodules`を使う。既存の作業ディレクトリで気づいた場合は`git submodule update --init --recursive`で取得できる。`git config --global submodule.recurse true`を設定しておくと、以降の`git pull`や`checkout`でもsubmoduleが自動更新されるようになる。

## よくある質問

**Q: `git pull`しただけでもsubmoduleの中身は最新になりますか？**
なりません。`git pull`は親リポジトリが記録しているsubmoduleの参照コミットを更新するだけで、実際のsubmoduleの作業ディレクトリには反映されません。誰かがsubmodule側で新しいコミットを指すように更新した場合、こちら側でも`git submodule update`（または`git submodule update --remote`）を実行する必要があります。

**Q: 毎回`--recurse-submodules`を付け忘れそうです。忘れないようにする方法はありますか？**
`git config --global submodule.recurse true`を設定しておくと、`clone`以外にも`pull`や`checkout`のタイミングでsubmoduleが自動的に追従するようになります。ただしチーム全員の環境で有効になるわけではないので、READMEにclone手順として明記しておくのも有効です。

**Q: `git submodule status`の記号（`-` `+`のあり/なし）の意味を毎回忘れます。**
`-`は未初期化、`+`は初期化済みだが記録コミットとローカルの内容が食い違っている、記号なしは初期化済みかつ最新、と覚えておくと切り分けが早くなります。今回のように`git status`がcleanと出るのに動作がおかしいときは、まずこのコマンドを疑うとよいです。

## 関連記事

- [git cloneしたファイルがLFSポインタ文字列のままになる原因と解決手順](/posts/git-clone-lfs-pointer-file)
- [git worktree addで「is already used by worktree」の原因と解決手順](/posts/git-worktree-already-checked-out)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
