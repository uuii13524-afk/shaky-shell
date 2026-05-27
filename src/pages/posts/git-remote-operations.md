---
title: 'Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）'
date: '2026-05-14'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitのremote・fetch・pull・pushコマンドでリモートリポジトリを操作する方法を解説。originの確認・追加・変更手順もまとめて紹介します。'
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

GitHubにSSH接続している場合は[SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)でリモートURLをSSH形式にしておくと認証が楽になる。

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
