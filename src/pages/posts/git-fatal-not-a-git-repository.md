---
title: 'git status で fatal: not a git repository が出た時の対処法'
date: '2026-07-23'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git status や git add で fatal: not a git repository (or any of the parent directories): .git が出る原因と直し方を解説。ZIPダウンロードで.gitが失われるケースやサブディレクトリでの実行ミスも紹介します。'
ja_tags: ['Git', 'GitHub', 'fatal', 'not a git repository', '.git']
en_tags: ['Git', 'GitHub', 'fatal', 'not a git repository', '.git']
---

## やりたかったこと（または「症状」）

社内の別チームが作った小さなツールをGitHubから取ってきて、少し手を加えてpushし直そうとしていた。ブラウザでリポジトリページを開き、「Code」ボタンから「Download ZIP」を選んで手元に展開し、いつも通り作業ディレクトリで `git status` を打った。ところが見慣れないエラーで即座に弾かれた。

```text
$ git status
fatal: not a git repository (or any of the parent directories): .git
```

`git add .` や `git log` を試しても同じエラーで止まり、リポジトリの中で作業しているはずなのに、Gitがそのディレクトリをリポジトリとして認識してくれなかった。

## 環境

- OS: macOS Sonoma 14.5
- Git: 2.45.1（Homebrew経由でインストール）
- ターミナル: iTerm2
- 取得方法: GitHubの「Download ZIP」機能でリポジトリを取得

## 試したこと

最初はGitそのものが壊れているのではないかと疑い、別の既存プロジェクトのディレクトリに移動して `git status` を実行した。

```bash
cd ~/projects/other-repo
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

こちらは問題なく動作したため、Git自体は壊れておらず、今回展開したディレクトリ側に何か問題があると分かった。次に、隠しファイルまで含めてディレクトリの中身を確認した。

```bash
cd ~/Downloads/mytool-main
ls -la
```

```text
total 32
drwxr-xr-x   8 acia  staff   256  7 23 10:12 .
drwx------@ 20 acia  staff   640  7 23 10:11 ..
-rw-r--r--   1 acia  staff  1071  7 23 10:12 README.md
-rw-r--r--   1 acia  staff   215  7 23 10:12 package.json
drwxr-xr-x   4 acia  staff   128  7 23 10:12 src
```

`.git` ディレクトリがどこにも存在していなかった。ここでようやく、ZIPでダウンロードしたことが原因だと気づいた。

## 原因

GitHubの「Download ZIP」ボタンは、その時点のブランチのスナップショット（ファイルの中身）だけをZIPとして固めて配布するもので、コミット履歴やブランチ情報を保持する `.git` ディレクトリは一切含まれていない。`git clone` はリモートリポジトリの `.git` の中身（履歴・ブランチ・リモート設定などのメタデータ一式）ごと丸ごと複製するのに対し、ZIPダウンロードは「今のファイルの見た目」だけを取ってくる仕組みのため、展開したフォルダはGitの管理下にないただのファイル群になる。`git status` はカレントディレクトリから親方向へ `.git` を探しに行き、見つからなければ「ここはGitリポジトリではない」という意味でこの `fatal` エラーを出す。

なお同じエラーは、実際に `git clone` したはずのプロジェクトでも、`cd` で間違えて `.git` の外側の親ディレクトリに出てしまっていたり、うっかり `rm -rf .git` してしまっていたりする場合にも発生する。

## 解決方法

### 1. そもそも `.git` があるべき場所を確認する

```bash
find ~/Downloads/mytool-main -maxdepth 1 -name ".git"
```

```text
(何も表示されない = .git が存在しない)
```

`.git` が見つからない時点で、そのディレクトリはGitリポジトリではないと確定する。

### 2. ZIPで取得したものは削除し、改めて `git clone` する

```bash
rm -rf ~/Downloads/mytool-main
git clone git@github.com:example/mytool.git
cd mytool
```

```text
Cloning into 'mytool'...
remote: Enumerating objects: 214, done.
remote: Counting objects: 100% (214/214), done.
remote: Compressing objects: 100% (150/150), done.
Receiving objects: 100% (214/214), 58.02 KiB | 2.90 MiB/s, done.
Resolving deltas: 100% (78/78), done.
```

`git clone` を使うことで、ファイルの中身に加えてコミット履歴・ブランチ・`origin` のリモート設定まで含んだ `.git` 一式が作られる。

### 3. 再度 `git status` で確認する

```bash
git status
```

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

`.git` が存在するディレクトリで実行しているため、正しくリポジトリとして認識され、以降 `git add` や `git push` も問題なく通るようになった。

### 4. 「間違って親ディレクトリで実行していた」だけの場合

`.git` を消してしまったわけではなく、単に `cd` の階層を間違えているだけのケースもある。その場合は `pwd` で現在地を確認し、リポジトリのルート（`.git` が存在するディレクトリ）まで移動すればよい。

```bash
pwd
cd mytool
git status
```

## ハマったポイント

- ZIPを展開したフォルダ名にリポジトリ名と関係のない `-main` というサフィックスが付いていたため、一見それらしいディレクトリに見えて、`.git` が無いことにすぐ気づけなかった
- `git init` を実行すればエラーは消えるが、それは新しい空のリポジトリを作るだけで、GitHub側のコミット履歴とは無関係になってしまう。表面上エラーが消えても、リモートと紐付いていないので `git push` すると別物として扱われる。焦って `git init` で誤魔化さず、素直に `git clone` し直すべきだった
- 同じエラーが、階層の深いモノレポで `cd packages/foo` のように潜った先で発生することもあった。こちらは `.git` を消したわけではなく、リポジトリのルートより浅い場所に `.git` があること自体は正しいので、`cd` で一段上に戻れば解決した

## よくある質問

**Q: `git init` すれば直るのでは？**
エラー自体は消えますが、それは「今いる場所を新しい空のGitリポジトリにする」操作であり、GitHub上の元のコミット履歴やブランチとは別物になります。既存リポジトリの続きとして作業したいなら `git init` ではなく `git clone` を使うべきです。

**Q: モノレポのサブディレクトリで作業していて急にこのエラーが出た場合は？**
`.git` はリポジトリのルートに1つだけ存在するのが基本なので、サブディレクトリ自体が原因であることは通常ありません。多くの場合はターミナルのカレントディレクトリがリポジトリの外（親ディレクトリのさらに上など）にずれています。`pwd` で現在地を確認し、`.git` があるディレクトリまで `cd` で戻ってください。

**Q: 展開したZIPの中身をそのままGit管理下に戻す方法はある？**
ファイルを一切失いたくない場合は、`git clone` で新しくリポジトリを作った後、ZIP側で編集した差分ファイルだけを上書きコピーする方法があります。ただし基本的には最初からZIPではなく `git clone` で取得しておくのが安全です。

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHubに初めてpushする手順](/posts/github-first-push)
- [git commitを取り消す方法](/posts/git-commit-undo)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [Windowsに Git をインストールする手順](/posts/windows-git-install)
