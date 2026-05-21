---
title: 'Gitのタグとリリースを管理する方法'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

Gitのタグを使ってリリースのバージョンを管理したかった。

## タグとは

特定のコミットに名前を付ける機能。バージョン管理によく使われる。

## タグの作成

### 軽量タグ（簡単）

```bash
git tag v1.0.0
```

### 注釈付きタグ（推奨）

```bash
git tag -a v1.0.0 -m "バージョン1.0.0リリース"
```

### 過去のコミットにタグを付ける

```bash
git log --oneline
git tag -a v1.0.0 コミットID -m "バージョン1.0.0"
```

## タグの確認

```bash
git tag              # タグ一覧
git tag -l "v1.*"    # パターンでフィルタ
git show v1.0.0      # タグの詳細
```

## タグをリモートにpush

```bash
git push origin v1.0.0        # 特定のタグをpush
git push origin --tags        # 全タグをpush
```

## タグの削除

```bash
git tag -d v1.0.0              # ローカルのタグを削除
git push origin --delete v1.0.0  # リモートのタグを削除
```

## GitHubでリリースを作成する

1. GitHubのリポジトリページを開く
2. 「Releases」→「Create a new release」
3. タグを選択またはタグ名を入力
4. リリースノートを記入して「Publish release」

## ハマったポイント

- タグはpushしないとリモートに反映されない
- 注釈付きタグは作者・日時・メッセージが記録される
- セマンティックバージョニング（v1.0.0）が一般的

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
