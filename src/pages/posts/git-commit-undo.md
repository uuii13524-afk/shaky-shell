---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-20'
category: 'Git'
---

## 症状

間違えたファイルをcommitしてしまった。
commitメッセージを間違えた。
pushする前に取り消したい。

## 環境

- Git
- Windows / Mac / Linux

## 状況別の対処法

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

```
git reset --soft HEAD~1
```

commitだけ取り消される。ファイルの変更はそのまま残る。
commitメッセージを間違えた時に使う。

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も戻す）

```
git reset --hard HEAD~1
```

commitもファイルの変更も全部取り消される。
注意：この操作は元に戻せない。

### 3. commitはそのままでファイルだけ変更したい

```
git reset HEAD~1
```

commitを取り消してファイルをステージング前の状態に戻す。
修正してから再度commitできる。

### 4. commitメッセージだけ変更したい

```
git commit --amend -m "新しいメッセージ"
```

直前のcommitメッセージだけ変更できる。

### 5. 特定のファイルだけステージングから外したい

```
git reset HEAD ファイル名
```

git addしたファイルをステージングから外す。commitには含まれなくなる。

## pushした後に取り消したい場合

pushした後の取り消しは危険なので基本的にやらない。
チームで使っている場合は特に注意が必要。

どうしても必要な場合は以下を使う。

```
git revert HEAD
```

取り消し用の新しいcommitを作る方法。履歴が残るので安全。

## ハマったポイント

- `--hard` と `--soft` の違いを間違えるとファイルの変更が消える
- pushした後の取り消しは `git revert` を使う
- `HEAD~1` は「1つ前のcommit」という意味。2つ前は `HEAD~2`

## 確認コマンド

操作前後にcommit履歴を確認する習慣をつける。

```
git log --oneline
```

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
