---
title: 'git logでコミット履歴を確認する方法'
date: '2026-05-17'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## 基本的な使い方

```bash
git log --oneline              # 1行で表示（よく使う）
git log --oneline -10          # 最新10件
git log --oneline --graph --all  # 全ブランチをグラフ表示
git log -p                     # 差分も表示
git show コミットID             # 特定コミットの詳細
```

## 検索・フィルタリング

```bash
git log --author="名前"
git log --since="2026-01-01"
git log --grep="キーワード"
```

## 差分を確認

```bash
git diff
git diff HEAD~1
```

## ハマったポイント

- `git log` は `q` キーで終了する
- `--oneline` が一番見やすい

## 関連記事

- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
