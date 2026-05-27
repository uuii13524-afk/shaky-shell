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

コミット履歴をもっと詳しく確認したい場合は[git logでコミット履歴を確認する方法](/posts/git-log-history)を参照。`.gitignore` の設定ミスでコミットしてしまった場合は[Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)も合わせて確認してほしい。

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
