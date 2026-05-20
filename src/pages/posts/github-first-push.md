---
title: 'GitHubで初めてリポジトリを作ってpushする手順'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

ローカルで作ったプロジェクトをGitHubにpushしたかった。
初めてやる場合、手順が複数あって詰まりやすい。

## 環境

- Windows 10 / 11
- Git
- GitHub

## 手順

### 1. GitHubでリポジトリを作成

1. https://github.com にログイン
2. 右上の「+」→「New repository」をクリック
3. Repository nameを入力
4. Public / Privateを選択
5. 「Create repository」を押す

### 2. ローカルでGitを初期化

```
git init
git add .
git commit -m "first commit"
```

### 3. GitHubと接続してpush

GitHubのリポジトリ作成後に表示されるコマンドをそのまま実行する。

```
git remote add origin https://github.com/ユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

## ハマったポイント

- GitHubのリポジトリ作成時にREADMEを追加するとpushで競合が起きる。最初は空のリポジトリで作成する
- `git push -u origin main` の `-u` は次回から `git push` だけで済むようにする設定
- パスワード認証は廃止されている。GitHubのPersonal Access Token（PAT）またはSSH鍵が必要

## Personal Access Tokenの取得方法

1. GitHubの右上アイコン→「Settings」
2. 左メニュー最下部「Developer settings」
3. 「Personal access tokens」→「Tokens (classic)」
4. 「Generate new token」
5. 必要な権限（repo）にチェックを入れて生成
6. 生成されたトークンをパスワードの代わりに使う

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
