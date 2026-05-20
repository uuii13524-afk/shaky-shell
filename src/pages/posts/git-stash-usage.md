---
title: 'git stashで作業を一時退避する方法'
date: '2026-05-20'
category: 'Git'
---

## 基本的な使い方

```bash
git stash              # 変更を退避
git stash list         # 退避一覧を確認
git stash pop          # 最新の退避を復元して削除
git stash apply        # 最新の退避を復元（削除しない）
git stash drop         # 最新の退避を削除
git stash clear        # 全ての退避を削除
```

## よくある使い方

```bash
# 作業中に緊急対応が必要になった場合
git stash
git switch hotfix
# 緊急対応してコミット
git switch main
git stash pop
```

## ハマったポイント

- `git stash pop` はコンフリクトが起きることがある
- 新規ファイルは `-u` オプションが必要
- `git stash clear` は元に戻せないので注意

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
