---
title: 'git cherry-pickで特定のコミットだけ別ブランチに適用する'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Git', 'cherry-pick', 'バージョン管理']
en_tags: ['Git', 'cherry-pick', 'version control']
---

## やりたかったこと

featureブランチで直したバグを、mainブランチにも適用したかった。
ブランチ全体をmergeするほどではなく、特定のコミットだけ持ってきたかった。

## cherry-pickの基本

```bash
# コミットハッシュを確認する
git log --oneline

# 特定のコミットを現在のブランチに適用する
git cherry-pick abc1234
```

`git log` で持ってきたいコミットのハッシュを確認してから実行する。

## 複数コミットをcherry-pickする

```bash
# 複数のコミットを個別に指定
git cherry-pick abc1234 def5678

# 連続したコミットをまとめて（abc1234の次から ghi9012 まで）
git cherry-pick abc1234..ghi9012
```

範囲指定 `A..B` はAを含まずBを含む。

## コンフリクトが起きたとき

```bash
# コンフリクト発生
git cherry-pick abc1234
# CONFLICT (content): Merge conflict in app.js

# ファイルを手動で修正してから
git add app.js
git cherry-pick --continue

# やっぱりやめる場合
git cherry-pick --abort
```

rebaseと同じく、修正 → `git add` → `--continue` の流れ。

## cherry-pickを取り消す

```bash
# cherry-pickしたコミットを打ち消すコミットを作る（push済みの場合）
git revert abc1234

# cherry-pickしたコミット自体を削除（未pushのとき）
git reset --hard HEAD~1
```

すでにpushしている場合は `git revert` で取り消しコミットを作るほうが安全。

## ハマったポイント

- コミットハッシュは `git log --oneline` で確認するのが一番早い
- cherry-pickするとコミットハッシュが変わる（別のコミットとして記録される）
- 範囲指定 `A..B` はAを含まずBを含む（rebaseと同じ挙動）
- 同じ変更を複数回cherry-pickするとコンフリクトが起きやすい
- push済みのコミットを取り消すときは `reset` ではなく `revert` を使う

## 関連記事

- [Gitのブランチ操作まとめ](/posts/git-branch-basics)
- [git commitを取り消す方法](/posts/git-commit-undo)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
- [git pullでコンフリクトが起きたときの解決方法](/posts/git-pull-merge-conflict)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
