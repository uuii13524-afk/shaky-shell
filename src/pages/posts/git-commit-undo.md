---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## 症状

間違えたファイルをcommitしてしまった。commitメッセージを間違えた。

## 状況別の対処法

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

```
git reset --soft HEAD~1
```

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も戻す）

```
git reset --hard HEAD~1
```

注意：この操作は元に戻せない。

### 3. commitメッセージだけ変更したい

```
git commit --amend -m "新しいメッセージ"
```

### 4. pushした後に取り消したい場合

```
git revert HEAD
```

取り消し用の新しいcommitを作る。履歴が残るので安全。

## 確認コマンド

```
git log --oneline
```

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
