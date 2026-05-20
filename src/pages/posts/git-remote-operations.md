---
title: 'Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

Gitのリモートリポジトリの操作コマンドを整理したかった。

## 環境

- Git
- GitHub

## リモートリポジトリの確認

```bash
git remote -v          # リモートリポジトリの一覧と URL を確認
```

## リモートリポジトリの追加・変更・削除

```bash
git remote add origin URL          # リモートを追加
git remote set-url origin URL      # URLを変更
git remote remove origin           # リモートを削除
git remote rename origin upstream  # リモートの名前を変更
```

## fetch・pull・pushの違い

### git fetch：リモートの変更を取得するだけ

```bash
git fetch origin       # リモートの変更を取得（マージしない）
```

ローカルのファイルは変更されない。リモートの状態を確認したい時に使う。

### git pull：取得してマージまで行う

```bash
git pull               # fetch + merge
git pull origin main   # mainブランチをpull
```

### git push：ローカルの変更をリモートに送る

```bash
git push               # 現在のブランチをpush
git push origin main   # mainブランチをpush
git push -u origin main  # 上流ブランチを設定してpush
git push --force       # 強制push（注意）
```

## よくある操作

### リモートの最新状態に追従する

```bash
git fetch origin
git merge origin/main
# または
git pull origin main
```

### ローカルブランチをリモートに追加する

```bash
git push -u origin ブランチ名
```

## ハマったポイント

- `git pull` はコンフリクトが起きることがある。`git fetch` で確認してから `git merge` が安全
- `git push --force` は履歴を書き換えるので共有リポジトリでは使わない
- `-u` フラグで上流ブランチを設定すると次回から `git push` だけで済む

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
