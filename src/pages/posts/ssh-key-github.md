---
title: 'SSHキーを生成してGitHubに登録する方法'
date: '2026-05-20'
category: 'Git'
---

## やりたかったこと

GitHubにpushするたびにパスワード（トークン）を入力するのが面倒なのでSSH接続に変えたかった。
SSHキーを使うと認証が自動化される。

## 環境

- Windows（Git Bash）/ Mac / Linux

## 手順

### 1. SSHキーを生成

```bash
ssh-keygen -t ed25519 -C "GitHubのメールアドレス"
```

以下が表示されたらEnterを押す（保存場所はデフォルトでOK）。

```
Enter file in which to save the key (/home/user/.ssh/id_ed25519):
```

パスフレーズは任意。設定しなくてもOK。

### 2. 公開鍵を確認

```bash
cat ~/.ssh/id_ed25519.pub
```

`ssh-ed25519 AAAA...` から始まる文字列が表示される。これをコピーする。

### 3. GitHubに公開鍵を登録

1. GitHubにログイン
2. 右上アイコン→「Settings」
3. 左メニュー「SSH and GPG keys」
4. 「New SSH key」をクリック
5. Titleに任意の名前を入力
6. Keyにコピーした公開鍵を貼り付け
7. 「Add SSH key」をクリック

### 4. 接続確認

```bash
ssh -T git@github.com
```

以下のように表示されれば成功。

```
Hi ユーザー名! You've successfully authenticated.
```

### 5. リポジトリのURLをSSHに変更

既存のリポジトリをHTTPSからSSHに変更する。

```bash
git remote set-url origin git@github.com:ユーザー名/リポジトリ名.git
```

確認。

```bash
git remote -v
```

## ハマったポイント

- Windowsの場合はGit Bashで操作する
- 公開鍵（.pub）をGitHubに登録する。秘密鍵は絶対に共有しない
- `ssh-keygen` を実行すると2つのファイルが生成される
  - `id_ed25519`：秘密鍵（共有しない）
  - `id_ed25519.pub`：公開鍵（GitHubに登録する）
- 既存リポジトリのURLをSSHに変えないとHTTPSのままになる

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
