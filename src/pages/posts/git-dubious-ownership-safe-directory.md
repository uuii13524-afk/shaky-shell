---
title: 'git statusで「fatal: detected dubious ownership in repository」が出る原因と解決手順（safe.directory）'
date: '2026-09-30'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git statusやgit logが「fatal: detected dubious ownership in repository」で止まる症状を解説。リポジトリの所有者と実行ユーザーが違うことが原因で、git config --global --add safe.directoryで解消するまでの手順を紹介します。'
ja_tags: ['Git', 'safe.directory', 'dubious ownership']
en_tags: ['Git', 'safe.directory', 'dubious ownership']
---

## やりたかったこと（症状）

別のユーザー（UID 1001）が作ったGitリポジトリの状態を、rootで確認したかった。ディレクトリに入って`git status`を叩いただけなのに、何も表示されず次のエラーで止まった。

```bash
git status
```

```text
fatal: detected dubious ownership in repository at '/path/to/repo'
To add an exception for this directory, call:

	git config --global --add safe.directory /path/to/repo
```

`git log`でも同じエラーになる。終了コードは`128`だった。リポジトリが壊れたのかと最初は身構えたが、メッセージをよく読むと「所有者が怪しい」と言っているだけで、データ破損の話ではない。

なお、ここに載せた出力は、後述の環境でこの状況を実際に再現して得たものです。パスだけ`/path/to/repo`に置き換えています。

## 環境

- OS: Linux（コンテナ環境）
- Git: 2.43.0
- 実行ユーザー: root（UID 0）
- リポジトリの所有者: UID 1001

## 試したこと

最初に疑ったのは、`.git`ディレクトリの破損だった。ただ、エラー文に`fatal: not a git repository`ではなく`dubious ownership`と書かれている。リポジトリとしては認識されていて、そのうえで「使うのを拒否」されている。

次に、エラー文が案内している通りの対処を確認した。すでに例外登録があるかどうかは、次のコマンドで調べられる。

```bash
git config --global --get-all safe.directory
```

このときは何も出力されなかった。つまり、このディレクトリは信頼済みとして登録されていない。

## 原因

Gitは、リポジトリのディレクトリの所有者が、コマンドを実行しているユーザーと異なる場合、そのリポジトリを既定では扱わない。これは2022年に修正された脆弱性（CVE-2022-24765）への対策として入った仕組みで、他人が書き込めるディレクトリに置かれた悪意ある`.git/config`などを、自分の権限で読み込んでしまう事故を防ぐためのものだ。

今回はリポジトリの所有者がUID 1001、実行ユーザーがrootで、所有者が食い違っていた。これが原因だと考えて間違いない。エラーは「リポジトリが壊れている」という意味ではなく、「所有者が違うので、明示的に許可されるまで触らない」という安全装置の動作だった。

Dockerのボリュームマウント、共有サーバー、`sudo`でのgit実行、CIのコンテナなど、「ファイルを作ったユーザーと、gitを実行するユーザーが違う」状況で起きやすい。

## 解決手順

### 1. 対象ディレクトリを信頼済みとして登録する

エラー文にそのまま書かれているコマンドを使う。

```bash
git config --global --add safe.directory /path/to/repo
```

`--global`を付けているので、実行ユーザーの`~/.gitconfig`に設定が書き込まれる。パスはエラー文に出ていたものをそのまま使う。

### 2. 登録されたことを確認する

```bash
git config --global --get-all safe.directory
```

```text
/path/to/repo
```

### 3. もう一度gitコマンドを実行する

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

エラーが消えて、通常の`git status`の出力が返ってきた。

### 別の解決策：所有者そのものを合わせる

例外登録ではなく、ディレクトリの所有者を実行ユーザーに合わせる方法もある。`chown -R`で所有者を変更すれば、そもそも「所有者の食い違い」が無くなる。ただし、今回は他のユーザーが引き続き使うリポジトリだったので、所有者は変えず`safe.directory`の登録を選んだ。この`chown`の手順は今回は実行していないので、実行するときは対象パスを必ず確認してほしい。

## 所有者を確認する方法

例外を登録する前に、所有者が本当に食い違っているか、そして相手を信頼できるかを確認しておくとよい。`ls -ld`でディレクトリの所有者、`id -un`で現在の実行ユーザーが分かる。

```bash
ls -ld /path/to/repo
id -un
```

2つの名前が違えば、それが原因だ。誰が何のために作ったリポジトリかが分かっている場合だけ、例外を登録する。他のユーザーが書き込めるディレクトリには、自分の権限で実行される設定が仕込まれている可能性がある。このチェックはそれを防ぐためのものなので、パスを登録することは「そこに書き込める全員を信頼する」と宣言することになる。今回、チェック自体を無効にする方法を探さず、特定のパスだけを登録したのはそのためだ。

## 動作確認

登録前後で同じディレクトリに対して`git status`を実行し、次の違いを確認した。

- 登録前: `fatal: detected dubious ownership in repository`で終了コード128
- 登録後: `On branch master` `nothing to commit, working tree clean`

設定を元に戻したいときは、次のコマンドで登録を削除できる。削除後に`git status`を実行すると、再び同じエラーが出ることも確認した。

```bash
git config --global --unset-all safe.directory
```

## まとめ

- `dubious ownership`は、リポジトリの所有者と実行ユーザーが違うときにGitが作動する安全装置で、データ破損ではない。
- 信頼できるリポジトリなら、エラー文に出るパスを`git config --global --add safe.directory <パス>`で登録すれば使える。
- 同種の「Gitが所有者違いで拒否する」問題は、Docker・共有サーバー・`sudo`・CIコンテナで起こりやすい。全ディレクトリを一括で信頼する設定はセキュリティ対策を無効にするので、対象のパスを個別に登録するのが安全。

## よくある質問

**Q: `safe.directory`は`--global`でなく、リポジトリの`.git/config`に書けませんか？**
書けません。この設定は、リポジトリ内の設定ファイルからは読み込まれない仕様です。悪意あるリポジトリが自分自身を信頼済みにしてしまうのを防ぐためで、ユーザー単位（`--global`）またはシステム単位の設定が対象になります。

**Q: 登録しても直らないときは？**
登録したパスとエラー文のパスが一致しているかを確認してください。`git config --global --get-all safe.directory`で登録済みのパスを一覧できます。また、`sudo`で実行している場合は、実行ユーザーがrootになるため、rootの`~/.gitconfig`に登録する必要があります。

**Q: 権限を変えず、自分のリポジトリでだけ確認したいです。**
自分が所有しているリポジトリでこのエラーが出る場合は、所有者が意図せず変わっている可能性があります。`ls -ld`で所有者を確認してください。

## 関連記事

- [git worktree addで「is already used by worktree」の原因と解決手順](/posts/git-worktree-already-checked-out)
- [git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順](/posts/git-submodule-not-initialized)
- [「fatal: not a git repository」の原因と解決手順](/posts/git-fatal-not-a-git-repository)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
