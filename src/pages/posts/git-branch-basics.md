---
title: 'GitのブランチをCLIで作成・切り替える基本コマンド'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

Gitのブランチを使って機能ごとに開発を分けたかった。
CLIでブランチを操作する基本コマンドをまとめる。

## 環境

- Git

## 基本コマンド

### ブランチ一覧を確認

```
git branch
```

現在いるブランチに `*` が付く。

### 新しいブランチを作成

```
git branch ブランチ名
```

### ブランチを切り替える

```
git switch ブランチ名
```

### ブランチを作成して同時に切り替える

```
git switch -c ブランチ名
```

これが一番よく使う。

### ブランチをmainにマージ

```
git switch main
git merge ブランチ名
```

### ブランチを削除

```
git branch -d ブランチ名
```

## よくある使い方

```
git switch -c feature/new-function
git add .
git commit -m "add new function"
git switch main
git merge feature/new-function
git branch -d feature/new-function
```

## リモートブランチの操作

```
git branch -r
git switch -c ブランチ名 origin/ブランチ名
git push origin ブランチ名
```

## ハマったポイント

- 古いGitでは `git checkout` を使う。新しいGitでは `git switch` が推奨
- マージ前に必ずmainブランチに切り替える
- ブランチ名にスペースは使えない
- `-d` で削除できない場合は `-D` で強制削除できる

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
