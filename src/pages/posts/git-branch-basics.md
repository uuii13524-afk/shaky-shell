---
title: 'GitのブランチをCLIで作成・切り替える基本コマンド'
date: '2026-05-08'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitのブランチをCLIで作成・切り替え・削除する基本コマンドを解説。git branch・git checkout・git switchの使い方をまとめて紹介します。'
---

## やりたかったこと

mainブランチで直接コードを書いていたら、途中で「これは別ブランチで作業すべきだった」と気づいた。チームのリポジトリにpushしたら怒られて、ブランチの切り方をちゃんと覚えることにした。

---

## 環境

- OS: macOS 13.5 / Ubuntu 22.04
- Git: 2.42.0

---

## 試したこと・うまくいかなかったこと

最初は `git checkout -b ブランチ名` でブランチを作っていた。これ自体は動くが、「`checkout` って何でも使えすぎて意味がわかりにくい」と感じていた。ブランチの切り替えもファイルの復元も同じコマンドで、間違えてファイルを消したことが1回あった。

次に、作業中のファイルを残したままブランチを切ろうとしたら、こんなエラーが出た。

```
error: Your local changes to the following files would be overwritten by checkout:
  src/index.js
Please commit your changes or stash them before you switch branches.
```

コミットもスタッシュも知らなかったので、一時的に変更を `git stash` で退避する方法を調べることになった。

---

## 基本コマンド

Git 2.23以降では `git switch` が推奨。`git checkout` より用途が明確で覚えやすい。

```bash
git branch                    # ブランチ一覧（現在のブランチに * が付く）
git branch -a                 # リモートブランチも含めて表示
git switch -c ブランチ名       # 作成して切り替え（checkout -b と同じ）
git switch ブランチ名          # 切り替え
git branch -d ブランチ名       # マージ済みブランチを削除
git branch -D ブランチ名       # 強制削除（マージ未済みでも削除）
```

---

## 実際の開発でよく使う流れ

```bash
# mainを最新にしてからブランチを作る
git switch main
git pull origin main
git switch -c feature/add-login

# 作業してコミット
git add src/login.js
git commit -m "add login form"

# mainにマージ
git switch main
git merge feature/add-login

# 不要になったブランチを削除
git branch -d feature/add-login
```

---

## 変更が残っているときのブランチ切り替え

未コミットの変更があると `git switch` はエラーになる。2つの方法で対処できる。

```bash
# 変更を一時退避してからブランチを切り替え
git stash
git switch other-branch

# 元のブランチに戻ってスタッシュを復元
git switch feature/add-login
git stash pop
```

または変更をコミットしてしまう（WIPコミット）:

```bash
git add -A
git commit -m "WIP: 作業途中"
git switch other-branch
```

---

## ハマったポイント

- `git switch` は Git 2.23以降。古いバージョンでは `git checkout` を使う。バージョンは `git --version` で確認できる
- `git checkout` はブランチの切り替えとファイルの復元を両方やる。`git checkout ファイル名` でコミット前の変更を捨てられるが、間違えてやると変更が消える。`git switch` はブランチ操作に特化していてこの事故が起きない
- `git pull origin main` より前に `git switch main` をしないと、別ブランチにmainの変更が引き込まれる。順番を間違えて余計なマージコミットが入った
- ブランチ名に空白は使えない。`feature/add login` はエラーになるのでハイフンかアンダースコアを使う
- `-d` で削除しようとしたらマージ未済みのブランチだと警告が出て削除できなかった。捨てて構わないなら `-D` で強制削除できる

---

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
