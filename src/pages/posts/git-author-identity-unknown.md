---
title: 'git commitで「Please tell me who you are」エラーが出る原因と解決手順'
date: '2026-08-30'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Git', 'git commit', 'user.name', 'user.email']
description: '新しい環境でgit commitを実行すると「Please tell me who you are」と表示されコミットできない現象を解説。user.name/user.emailの設定方法と、グローバル設定とリポジトリ単位設定の使い分けまで紹介します。'
---

## ひとことで言うと

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

これを実行してから `git commit` をやり直せばコミットできるようになります。

---

## やりたかったこと / 現象

新しく用意したコンテナ環境で、リポジトリを `git init` した直後に最初のコミットを作ろうとしたところ、コミットが成立せずに以下のエラーで止まりました。

```bash
git add README.md
git commit -m "init"
```

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: empty ident name (for <>) not allowed
```

`git add` は成功しているのに、`git commit` の段階でだけ失敗します。ファイルの中身やステージングには何も問題がありません。

---

## 環境

- Git: 2.43.0
- OS: Linux（コンテナ環境、`$HOME` が空のプロファイルでまだ何も `git config` していない状態）

---

## 試したこと

最初は「ステージングし忘れているファイルがあるのでは」と疑い、`git status` や `git diff --cached` で差分を確認しましたが、`README.md` は正しくステージされていました。次に、コミットメッセージの引用符が悪いのかと `-m` の書き方を変えて再実行しましたが、エラー内容は変わらず `Author identity unknown` のままでした。

エラーメッセージ本文をよく読むと、`git config --global user.email` / `user.name` を設定するよう案内が出ています。ここでようやく、ファイルやコマンドの書式ではなく「そもそも著者情報が未設定」であることが原因だと気づきました。

---

## 原因

`git commit` はコミットオブジェクトの `author` / `committer` 欄に、名前とメールアドレスを埋め込む必要があります。この値は `user.name` と `user.email` という設定から取得されますが、今回の環境は新規に用意したもので、`~/.gitconfig`（グローバル設定）にもリポジトリの `.git/config`（ローカル設定）にもこの2つが一度も設定されていませんでした。

実際に確認すると、両方とも空でした。

```bash
git config --global user.name || echo "(unset)"
git config --global user.email || echo "(unset)"
```

```
(unset)
(unset)
```

値が空のまま無理にコミットしようとすると、名前もメールアドレスも空の識別子（`<>`）でコミットオブジェクトを作ろうとするため、Gitが `fatal: empty ident name (for <>) not allowed` として処理を止めます。これは壊れたコミット履歴が残るのを防ぐための正常な安全装置で、バグではありません。

---

## 解決手順

### 1. グローバルに名前とメールアドレスを設定する

このマシン・このユーザーで作業するすべてのリポジトリに適用したい場合は `--global` を付けます。

```bash
git config --global user.name "Test User"
git config --global user.email "test@example.com"
```

各行の意図は次のとおりです。

- `user.name`: コミットの author/committer に表示される表示名を設定する
- `user.email`: 同じくコミットに埋め込まれるメールアドレスを設定する

### 2. コミットをやり直す

```bash
git add README.md
git commit -m "init"
```

```
[master (root-commit) b482ab7] init
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

先ほどと同じ操作なのに、今度は正常にコミットが成立しました。

### 3. リポジトリ単位で別の名前・メールを使いたい場合

会社用と個人用でGitHubアカウントを使い分けているなど、リポジトリごとに著者情報を変えたいときは `--global` を外してそのリポジトリ内だけに設定します。

```bash
git config user.name "Repo Local User"
git config user.email "repo-local@example.com"
```

`--global` を付けない設定は `.git/config` に書き込まれ、グローバル設定より優先されます。複数のGitHubアカウントを使い分けているプロジェクトではこちらを使うと安全です。

---

## 動作確認

設定が反映され、コミット履歴に author 情報が正しく記録されていることを確認します。

```bash
git log --oneline
```

```
b482ab7 init
```

さらにリポジトリ単位の設定を確認したい場合は次のコマンドで現在有効な値を表示できます。

```bash
git config user.name
git config user.email
```

```
Repo Local User
repo-local@example.com
```

これで、グローバル設定・ローカル設定のどちらが効いているかも切り分けて確認できます。

---

## よくあるエラーと対処

### `--global` を付けたのに反映されない

複数のリポジトリで作業していて「グローバルに設定したはずなのに毎回聞かれる」場合は、そのリポジトリの `.git/config` に古いローカル設定が残っていないか確認します。ローカル設定はグローバル設定より優先されるため、空文字や間違ったアドレスが残っていると上書きされません。

```bash
git config --local --list | grep user
```

### CI環境で毎回このエラーが出る

GitHub Actionsなど使い捨てのCI環境では `~/.gitconfig` が毎回空の状態からスタートするため、ワークフロー内で明示的に `user.name` / `user.email` を設定する必要があります。多くの場合、コミットを行うジョブの先頭で一度だけ設定しておけば十分です。

```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
```

---

## よくある質問

**Q: 本名やプライベートなメールアドレスを使いたくありません。どうすればいいですか？**
GitHubの場合、GitHub側が提供する `noreply` 形式のメールアドレス（例: `ユーザー名@users.noreply.github.com`）を `user.email` に設定すれば、本物のメールアドレスを公開せずにコミットできます。

**Q: `--global` と付けない設定はどちらが優先されますか？**
リポジトリ内の設定（`--global` なし）が優先されます。グローバル設定は「どのリポジトリでも設定がない場合のデフォルト値」という位置づけです。

**Q: 一度設定すれば、他のリポジトリでも使い回せますか？**
`--global` で設定した場合はそのユーザーのすべてのリポジトリに適用されます。リポジトリごとに変えたい場合だけ、そのリポジトリ内で個別に設定してください。

**Q: このエラーは初回コミット以外でも出ますか？**
出ます。`user.name` / `user.email` が空である限り、2回目以降のコミットでも同じように `Author identity unknown` で止まります。設定が完了すれば以降は毎回聞かれません。

---

## まとめ

- `git commit` は author/committer 情報として `user.name` と `user.email` を必須で使う。これが未設定だと `Please tell me who you are` で止まる。
- 解決は `git config --global user.name` / `user.email` の2行を設定するだけ。既存のファイルやコミットメッセージの書き方には問題がない。
- 複数アカウントを使い分ける場合や、CIのような使い捨て環境では `--global` を付けないリポジトリ単位の設定が有効。
- 同じ「設定が空のまま実行して安全装置で止まる」系のエラーは、SSHの `known_hosts` 未登録や、GPG署名鍵未設定でのコミット拒否などでも起きる。エラーメッセージが案内している設定コマンドをそのまま実行する、という対処の型は共通して使える。

## 関連記事

- [git commitを取り消す方法まとめ](/posts/git-commit-undo)
- [fatal: not a git repositoryの原因と対処法](/posts/git-fatal-not-a-git-repository)
- [.gitignoreの書き方と設定手順](/posts/git-gitignore-setup)
