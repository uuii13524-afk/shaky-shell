---
title: 'git logでコミット履歴を確認する方法'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

Gitのコミット履歴を確認したかった。
`git log` は様々なオプションで表示をカスタマイズできる。

## 環境

- Git

## 基本的な使い方

```bash
git log                  # 全コミット履歴を表示
git log --oneline        # 1行で表示（よく使う）
git log --oneline -10    # 最新10件だけ表示
git log --graph          # ブランチの分岐をグラフで表示
git log --oneline --graph --all  # 全ブランチをグラフ表示
```

## 特定のファイルの履歴を確認

```bash
git log ファイル名           # 特定ファイルの変更履歴
git log --follow ファイル名  # ファイル名変更を追う
```

## 変更内容も一緒に確認

```bash
git log -p               # 各コミットの差分も表示
git log -p ファイル名    # 特定ファイルの差分
git show コミットID      # 特定コミットの詳細
```

## 検索・フィルタリング

```bash
git log --author="名前"          # 作者でフィルタ
git log --since="2026-01-01"     # 日付以降
git log --until="2026-12-31"     # 日付以前
git log --grep="キーワード"      # コミットメッセージで検索
```

## 差分を確認

```bash
git diff                         # 変更差分を表示
git diff HEAD~1                  # 1つ前のコミットとの差分
git diff コミットID1 コミットID2  # 2つのコミット間の差分
```

## ハマったポイント

- `git log` は `q` キーで終了する
- `--oneline` は短いハッシュとメッセージだけ表示されて見やすい
- `git log --graph --all` でブランチの状態を視覚的に確認できる

## 関連記事

- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
