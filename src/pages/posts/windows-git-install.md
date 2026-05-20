---
title: 'WindowsにGitをインストールして初期設定する方法'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

WindowsにGitをインストールして使えるようにしたかった。
インストール時の設定項目が多くて迷いやすい。

## 環境

- Windows 10 / 11

## 手順

### 1. Gitをダウンロード

https://git-scm.com にアクセスして「Download for Windows」をクリック。

### 2. インストール

インストーラーを実行する。設定項目が多いが以下の点だけ注意する。

**「Choosing the default editor used by Git」**
→ 「Use Visual Studio Code as Git's default editor」を選ぶ（VS Codeがある場合）
→ なければ「Use Notepad as Git's default editor」でOK

**「Adjusting the name of the initial branch in new repositories」**
→ 「Override the default branch name for new repositories」を選んで `main` と入力

**「Adjusting your PATH environment」**
→ 「Git from the command line and also from 3rd-party software」を選ぶ

それ以外はデフォルトのままでOK。

### 3. インストール確認

ターミナルを再起動して以下を実行。

```
git --version
```

バージョンが表示されれば成功。

### 4. 初期設定

```
git config --global user.name "自分の名前"
git config --global user.email "メールアドレス"
```

GitHubのアカウントと同じメールアドレスを設定する。

### 5. 設定確認

```
git config --list
```

## ハマったポイント

- インストール後にターミナルを再起動しないとgitコマンドが認識されない
- user.nameとuser.emailを設定しないとcommit時にエラーになる
- デフォルトブランチ名を `main` にしないとGitHubと名前が合わずにpushで詰まる

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
