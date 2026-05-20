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
# 新機能の開発を始める
git switch -c feature/new-function

# 作業してcommit
git add .
git commit -m "add new function"

# mainに戻ってマージ
git switch main
git merge feature/new-function

# ブランチを削除
git branch -d feature/new-function
```

## リモートブランチの操作

### リモートブランチを確認

```
git branch -r
```

### リモートブランチをローカルに取得

```
git switch -c ブランチ名 origin/ブランチ名
```

### ローカルブランチをリモートにpush

```
git push origin ブランチ名
```

## ハマったポイント

- 古いGitでは `git checkout` を使う。新しいGitでは `git switch` が推奨
- マージ前に必ずmainブランチに切り替える
- ブランチ名にスペースは使えない。`/` や `-` を使う
- `-d` で削除できない場合は `-D` で強制削除できる（マージ前でも削除される）
