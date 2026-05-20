---
title: 'git stashで作業を一時退避する方法'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

作業中に別のブランチに緊急で切り替える必要が出た。
コミットせずに変更を一時退避したかった。

## 環境

- Git

## git stashとは

現在の変更を一時的に退避してクリーンな状態に戻す機能。
退避した変更は後で復元できる。

## 基本的な使い方

### 変更を退避する

```bash
git stash              # 変更を退避
git stash save "メッセージ"  # メッセージ付きで退避
git stash -u           # 追跡されていないファイルも退避
```

### 退避した変更を確認

```bash
git stash list
# stash@{0}: On main: 作業中の変更
# stash@{1}: On main: 別の変更
```

### 退避した変更を復元する

```bash
git stash pop          # 最新の退避を復元して削除
git stash apply        # 最新の退避を復元（削除しない）
git stash apply stash@{1}  # 特定の退避を復元
```

### 退避した変更を削除する

```bash
git stash drop         # 最新の退避を削除
git stash drop stash@{1}  # 特定の退避を削除
git stash clear        # 全ての退避を削除
```

## よくある使い方

```bash
# 作業中に緊急対応が必要になった場合
git stash              # 変更を退避
git switch hotfix      # 別のブランチに切り替え
# 緊急対応を行ってコミット
git switch main        # 元のブランチに戻る
git stash pop          # 退避した変更を復元
```

## ハマったポイント

- `git stash pop` は競合が起きることがある。その場合は手動で解決する
- `git stash` はコミットされていない変更を退避する。新規ファイルは `-u` オプションが必要
- スタッシュはブランチをまたいで使える
- `git stash clear` は元に戻せないので注意

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
