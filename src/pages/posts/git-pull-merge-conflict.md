---
title: 'git pullでコンフリクトが発生した時の解決方法'
date: '2026-05-20'
category: 'Git'
---

## 症状

git pullしたらコンフリクトが発生してマージできない。

```
CONFLICT (content): Merge conflict in ファイル名
Automatic merge failed; fix conflicts and then commit the result.
```

## 環境

- Git

## コンフリクトとは

同じファイルの同じ箇所を複数人（または複数のブランチ）が変更した時に発生する。
Gitが自動でマージできないため手動で解決が必要。

## 解決手順

### 1. コンフリクトしているファイルを確認

```bash
git status
```

`both modified:` と表示されているファイルがコンフリクトしている。

### 2. ファイルを開いて確認

コンフリクトしているファイルを開くと以下のような記号が追加されている。

```
<<<<<<< HEAD
自分の変更内容
=======
相手の変更内容
>>>>>>> ブランチ名
```

### 3. 手動で修正

`<<<<<<<`、`=======`、`>>>>>>>` の記号を削除して、正しい内容に書き直す。

例：両方の変更を残す場合。

```
自分の変更内容
相手の変更内容
```

### 4. コミット

```bash
git add .
git commit -m "resolve conflict"
```

## コンフリクトを中止して元に戻す

解決が難しい場合はマージを中止できる。

```bash
git merge --abort
```

## ハマったポイント

- `<<<<<<<`、`=======`、`>>>>>>>` の記号を残したままコミットしないように注意
- VS Codeなどのエディタはコンフリクトを視覚的に解決する機能がある
- こまめにpullしてコンフリクトを小さくするのが予防策

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
