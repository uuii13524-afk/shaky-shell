---
title: 'Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）'
date: '2026-05-14'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## リモートリポジトリの確認

```bash
git remote -v
```

## リモートリポジトリの追加・変更

```bash
git remote add origin URL
git remote set-url origin URL
git remote remove origin
```

## fetch・pull・pushの違い

```bash
git fetch origin       # リモートの変更を取得（マージしない）
git pull origin main   # fetch + merge
git push               # ローカルの変更をリモートに送る
git push -u origin main  # 上流ブランチを設定してpush
```

## ハマったポイント

- `git push --force` は共有リポジトリでは使わない
- `-u` フラグで上流ブランチを設定すると次回から `git push` だけで済む

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
