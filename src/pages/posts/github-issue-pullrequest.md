---
title: 'GitHubのIssueとPull Requestの基本的な使い方'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

GitHubのIssueとPull Requestを使ってチーム開発の流れを理解したかった。

## 環境

- GitHub

## Issueとは

バグ報告・機能要望・タスク管理に使う。

### Issueを作成する

1. GitHubのリポジトリページを開く
2. 「Issues」タブ→「New issue」
3. タイトルと説明を入力して「Submit new issue」

### よく使うIssueのテンプレート

```markdown
## 症状
どんな問題が起きているか

## 再現手順
1. 
2. 
3. 

## 期待する動作
どうなるべきか

## 環境
- OS：
- バージョン：
```

## Pull Requestとは

コードの変更をレビューしてもらってからマージする仕組み。

### Pull Requestの流れ

```bash
# 1. ブランチを作成
git switch -c feature/fix-bug

# 2. 変更してコミット
git add .
git commit -m "fix: バグを修正"

# 3. GitHubにpush
git push -u origin feature/fix-bug
```

4. GitHubでPull Requestを作成
5. レビューしてもらう
6. 承認されたらマージ

### Pull RequestとIssueを紐付ける

コミットメッセージやPRの説明に以下を書くと自動でIssueが閉じる。

```
fix #123
closes #123
resolves #123
```

## ハマったポイント

- Issueの番号はPRと自動紐付けできる
- レビューなしでmainに直接pushするのは避ける
- ブランチ名はわかりやすく付ける

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
