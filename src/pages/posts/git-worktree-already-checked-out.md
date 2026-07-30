---
title: 'git worktree addで「is already used by worktree」の原因と解決手順'
date: '2026-07-30'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git worktree addで同じブランチを別ディレクトリに追加しようとすると「is already used by worktree」で失敗する症状を解説。worktreeディレクトリをrmで直接削除した後に発生する原因と、git worktree pruneでの解決手順を紹介します。'
ja_tags: ['Git', 'git worktree', 'ブランチ']
en_tags: ['Git', 'git worktree', 'branch']
---

## やりたかったこと（または「症状」）

複数のfeatureブランチを並行して作業するために`git worktree`を使っていた。ある日、以前作業していた`feature-login`ブランチのworktreeディレクトリが不要になったと判断し、`git worktree remove`ではなく普通に`rm -rf`でディレクトリごと削除した。

後日、同じブランチで別の場所に作業ディレクトリを作り直そうとしたところ、`git worktree add`がエラーで失敗した。

```bash
git worktree add ../feature-login feature-login
```

```text
fatal: 'feature-login' is already used by worktree at '/home/dev/project-feature-login'
```

すでにディレクトリは`rm -rf`で消しているのに、Gitはまだそのworktreeが存在するものとして扱っていた。パスを変えて実行しても同じエラーになった。

```bash
git worktree add ../feature-login-v2 feature-login
```

```text
fatal: 'feature-login' is already used by worktree at '/home/dev/project-feature-login'
```

ブランチ名を変えずに別ディレクトリへworktreeを追加すること自体ができない状態だった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.51.0
- リポジトリ構成: メインの作業ディレクトリ1つ＋featureブランチごとのworktreeを`../`配下に複数作成する運用
- 削除したworktreeディレクトリ: `/home/dev/project-feature-login`（`git worktree remove`を使わず`rm -rf`で削除）

## 試したこと

まず、Gitが認識しているworktreeの一覧を確認した。

```bash
git worktree list
```

```text
/home/dev/project                  a1b2c3d [main]
/home/dev/project-feature-login    e4f5g6h [feature-login]
```

実ディレクトリはすでに存在しないはずなのに、`git worktree list`には`/home/dev/project-feature-login`が現役のworktreeとして表示されていた。試しにそのパスへ移動してみると案の定ディレクトリごと存在しなかった。

```bash
cd /home/dev/project-feature-login
```

```text
bash: cd: /home/dev/project-feature-login: No such file or directory
```

次に、`git branch`で該当ブランチの状態を確認した。

```bash
git branch -v
```

```text
* main            a1b2c3d Latest commit on main
  feature-login   e4f5g6h Add login form validation
```

ブランチ自体は残っており壊れてはいなかった。問題はブランチではなく、Gitの内部メタデータ側に「このブランチは`/home/dev/project-feature-login`でチェックアウト中」という古い記録が残っていることだと分かった。

## 原因

`git worktree`はメインリポジトリの`.git/worktrees/`配下に、各worktreeの管理情報（対応ディレクトリのパスや、どのブランチをチェックアウトしているか）を保持している。`git worktree remove`コマンドを使えば、この管理情報とディレクトリの両方が整合性を保ったまま削除される。

しかし今回のように`rm -rf`でディレクトリだけを直接削除すると、`.git/worktrees/`側の管理情報は消えずに残ってしまう。Gitから見ると「`feature-login`ブランチは今も`/home/dev/project-feature-login`というworktreeでチェックアウト中」という状態のままになるため、同じブランチを別の場所へ`worktree add`しようとすると、二重チェックアウトを防ぐ安全機構が働いて`is already used by worktree`エラーになる。これは壊れているのではなく、Gitが「削除されたことをまだ知らない」だけの状態だった。

## 解決方法

### 1. 現在のworktree一覧を確認する

```bash
git worktree list
```

存在しないパスが残っていないか確認する。

### 2. 存在しなくなったworktreeの管理情報を掃除する

`git worktree prune`を実行すると、実ディレクトリが存在しないworktreeの管理情報を安全に削除できる。

```bash
git worktree prune -v
```

```text
Removing worktrees/project-feature-login: gitdir file points to non-existent location
```

### 3. worktree一覧を再確認する

```bash
git worktree list
```

```text
/home/dev/project    a1b2c3d [main]
```

`feature-login`のworktreeエントリが消え、ブランチが「どこにもチェックアウトされていない」状態に戻った。

### 4. 改めてworktreeを追加する

```bash
git worktree add ../feature-login feature-login
```

```text
Preparing worktree (checking out 'feature-login')
HEAD is now at e4f5g6h Add login form validation
```

エラーなくworktreeが作成できた。

## 動作確認

```bash
git worktree list
```

```text
/home/dev/project                a1b2c3d [main]
/home/dev/project-feature-login  e4f5g6h [feature-login]
```

新しいディレクトリで`feature-login`ブランチが正しくチェックアウトされていることを確認できた。

## ハマったポイント

- `rm -rf`でworktreeディレクトリを消しただけでは、Git側の管理情報（`.git/worktrees/`配下）は自動的にクリーンアップされない。必ず`git worktree remove`を使うか、消した後に`git worktree prune`を実行する必要がある
- エラーメッセージの`is already used by worktree`だけを読むと、あたかも今もどこかで使用中であるかのように見えるが、実際にはディレクトリがすでに存在しない「幽霊worktree」であるケースが多い。慌てて`--force`を付けて回避する前に、まず`git worktree list`で実体の有無を確認するべきだった
- `git worktree add --force`でも同じブランチを別worktreeに強制的にチェックアウトできるが、同一ブランチを複数worktreeで同時に触ってしまうと、コミット漏れや意図しない上書きの原因になるため、根本原因（管理情報の残留）を解消する方が安全

## よくある質問

**Q: `git worktree remove`を使わずに消してしまった場合、他に影響はありますか？**
ディレクトリと管理情報が不整合になるだけで、コミット履歴やブランチ自体が壊れることはない。`git worktree prune`で管理情報を整理すれば元通りに使える。

**Q: `git worktree prune`は他のworktreeにも影響しますか？**
実体が存在するworktree（きちんと`cd`できるディレクトリ）には影響しない。あくまで実ディレクトリが見つからないエントリだけが対象になる。

**Q: 今後同じ問題を避けるにはどうすればいいですか？**
worktreeを不要にする際は必ず`git worktree remove <path>`を使う。手動で`rm -rf`した場合は、忘れずに`git worktree prune`をセットで実行する運用にしておくとよい。

## 関連記事

- [git branchの基本コマンドまとめ](/posts/git-branch-basics)
- [git detached HEADの直し方](/posts/git-detached-head-fix)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [git stashの使い方まとめ](/posts/git-stash-usage)
- [fatal: not a git repositoryエラーの対処法](/posts/git-fatal-not-a-git-repository)
