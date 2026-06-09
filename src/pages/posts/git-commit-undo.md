---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitで間違えてcommitした時の取り消し方を解説。git reset --softやgit revertを使ったコミットの取り消し・修正方法をまとめて紹介します。'
---

## やりたかったこと

間違えた状態でgit commitしてしまった。`.env`ファイルを誤ってコミットしていた、commitメッセージを盛大に誤字ったなど、よくある状況でどのコマンドを使えばいいのか毎回混乱する。`reset`と`revert`の違いもよくわからなかった。

## 環境

- Git 2.44.0
- Windows 11 / Ubuntu 22.04
- GitHub（リモートリポジトリあり）

## 試したこと・うまくいかなかったこと

最初、「commitを取り消す」方法を調べたら`git reset`と`git revert`の2種類が出てきて、どちらを使えばいいか迷った。「revertの方が安全」という情報を見て`git revert HEAD`を使ったら、取り消し用の新しいコミットが作られた。これだと「取り消したコミット」が履歴に残るので、まだpushしていない段階では使い方が間違っていた。

次に`git reset --hard HEAD~1`を使ったら確かにコミットは消えたが、ファイルの変更内容ごと消えてしまった。せっかく書いたコードが全部消えて、やり直しになってしまった。`--hard`と`--soft`の違いをちゃんと理解しないで使った失敗だった。

`git commit --amend`でメッセージだけ修正しようとしたら、すでにpushした後だったのでリモートとの差分が生まれてしまい、`git push --force`が必要になってしまった。チームリポジトリだったのでforce pushは危険だった。

## 解決策

状況に合わせてコマンドを使い分ける。

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

pushする前の場合はこれが最も安全。コミットは消えるが、変更したファイルはそのままstaged状態で残る。

```bash
git reset --soft HEAD~1
```

commitし直せる状態になるので、ファイルを修正してから改めてcommitする。

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も消す）

ファイルの変更ごと全部なかったことにする。元に戻せないので使う前に`git diff HEAD~1`でどんな変更が消えるか確認しておく。

```bash
git reset --hard HEAD~1
```

### 3. commitメッセージだけ変更したい

まだpushしていない場合のみ使う。pushした後に使うとリモートとの差分が生まれてforce pushが必要になる。

```bash
git commit --amend -m "新しいメッセージ"
```

### 4. pushした後に取り消したい場合

pushした後は`reset`で履歴を書き換えるとチームに迷惑がかかる。`revert`で「取り消しコミット」を新しく作る方法が安全。

```bash
git revert HEAD
```

エディタが開いてコミットメッセージを書く画面になる。保存して閉じると取り消し用のコミットが作られる。その後`git push`すれば完了。

### 5. 2つ以上前のcommitを取り消したい

`HEAD~1`の数字を変えれば何個でも指定できる。

```bash
git reset --soft HEAD~3  # 3つ前まで取り消す
```

現在の履歴を確認してから判断する。

```bash
git log --oneline
```

コミット履歴の確認方法は[git logでコミット履歴を確認する方法](/posts/git-log-history)に詳しくまとめた。

## ハマったポイント

- `--soft`と`--hard`の違いをちゃんと理解してから使うべきだった。`--hard`は「ファイルの変更ごと消える」という意味で、気軽に使ったら書いたコードが全部消えて焦った
- `reset`と`revert`は使いどころが全然違う。「まだpushしていない」なら`reset`で履歴を書き換えていい。「すでにpushした」なら`revert`で取り消しコミットを追加する方が安全
- `git commit --amend`をpush後に使うと`git push --force`が必要になる。force pushはチームリポジトリでは原則禁止なので、メッセージミスに気づいたタイミングが重要だった
- `.gitignore`に書いていない`.env`ファイルをコミットしてしまった場合、`git reset --soft HEAD~1`でコミットを取り消してから`.gitignore`に追加する。`.gitignore`の設定ミスが原因なら[Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)も確認する
- `git reflog`を使うとresetで消したコミットも一定期間は復元できると後から知った。`--hard`で消してしまっても諦めずにまず`git reflog`を確認するのが正解

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
