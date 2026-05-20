---
title: 'git pullでコンフリクトが発生した時の解決方法'
date: '2026-05-13'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## 症状

```
CONFLICT (content): Merge conflict in ファイル名
Automatic merge failed; fix conflicts and then commit the result.
```

## 解決手順

### 1. コンフリクトしているファイルを確認

```bash
git status
```

### 2. ファイルを開いて修正

```
<<<<<<< HEAD
自分の変更内容
=======
相手の変更内容
>>>>>>> ブランチ名
```

`<<<<<<<`、`=======`、`>>>>>>>` を削除して正しい内容に書き直す。

### 3. コミット

```bash
git add .
git commit -m "resolve conflict"
```

## マージを中止する場合

```bash
git merge --abort
```

## ハマったポイント

- 記号を残したままコミットしないように注意
- こまめにpullしてコンフリクトを小さくする

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
