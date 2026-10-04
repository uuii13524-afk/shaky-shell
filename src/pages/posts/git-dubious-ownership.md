---
title: 'git statusで「fatal: detected dubious ownership in repository」が出る原因と解決手順（Git 2.43 / Ubuntu 24.04）'
date: '2026-10-04'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git statusやgit logが「fatal: detected dubious ownership in repository」で止まる症状を再現して解説。所有者の違いが原因で、safe.directoryの設定かchownで解決できる手順と、*指定のリスクまで紹介します。'
ja_tags: ['Git', 'safe.directory', 'dubious ownership']
en_tags: ['Git', 'safe.directory', 'dubious ownership']
---

## やりたかったこと（症状）

別ユーザーが作成したディレクトリにあるGitリポジトリで、いつものように状態を確認したかった。

```bash
cd repo
git status
```

ところが、通常のステータス表示ではなく、次のエラーで止まった。

```text
fatal: detected dubious ownership in repository at '/path/to/repo'
To add an exception for this directory, call:

	git config --global --add safe.directory /path/to/repo
```

`git log`も同じエラーで失敗し、終了コードは128だった。リポジトリが壊れたのかと一瞬疑ったが、`.git`の中身は無事で、原因は別のところにあった。なお`/path/to/repo`は実際のパスを伏せた表記で、メッセージの構造は出力そのままである。

## 環境

この記事の出力は、すべて次の環境で実際にコマンドを実行して得たものである。

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- 実行ユーザー: root（uid=0）
- リポジトリの所有者: uid=1000, gid=1000（`chown`で意図的に変更）

実際の現場では、「Dockerのボリュームマウントで所有者がずれた」「WSL2のWindows側ドライブにあるリポジトリを開いた」「共有サーバで別ユーザーが作ったリポジトリを触った」といった場面で遭遇しやすい。ここでは原因を確実に切り分けるため、`git init`したリポジトリの所有者だけを`chown`で別のuidに変えて再現した。

## 試したこと

まず「リポジトリ自体が壊れた」と考え、`.git`ディレクトリを疑った。しかしエラーメッセージを読み直すと、`corrupt`や`not a git repository`ではなく`dubious ownership`（疑わしい所有権）と書かれている。これは破損ではなく、Gitが意図的にコマンドを拒否している状態だと分かった。

次に、再現のためにリポジトリの所有者を変えて状況を確認した。

```bash
git init -q repo
chown -R 1000:1000 repo
id
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

実行しているのはrootで、リポジトリの所有者はuid 1000になっている。この状態で`git status`を実行すると、冒頭のエラーが再現した。

つまり「今のユーザーと、リポジトリ（のディレクトリ）の所有者が一致しない」ことが引き金になっている。ファイルの読み取り権限は十分にあるのに拒否されるのが、この問題の分かりにくいところである。

## 原因

Gitは、リポジトリのディレクトリの所有者が現在のユーザーと異なる場合、そのリポジトリでのコマンド実行を拒否する。これはGit 2.35.2以降で追加された安全対策（CVE-2022-24765への対応）で、他人が置いたリポジトリ内の設定ファイルや`core.fsmonitor`などのフック的な設定を通じて、意図しないコマンドが実行されるのを防ぐ目的がある。

エラーメッセージが案内している`safe.directory`は、「このディレクトリは信頼してよい」とGitに教えるための設定項目である。この設定が登録されたパスについては、所有者が違っても通常どおり動作する。

注意点として、`safe.directory`は**グローバル設定（`--global`）やシステム設定からのみ読み込まれる**。リポジトリ内の`.git/config`に書いても効果がない。リポジトリ側で自分を信頼させる設定を書けてしまうと、安全対策の意味がなくなるためである。

## 解決手順

### 1. 状況を確認する

まず、エラーが「所有者の不一致」によるものかを確認する。ディレクトリの所有者と自分のuidを比べる。

```bash
id -u
stat -c '%u %U' .
```

2つの値が異なっていれば、今回のエラーに該当する。

### 2. 方法A：safe.directoryに登録する（所有者を変えたくない場合）

エラーメッセージが表示したコマンドをそのまま実行する。`$(pwd)`で現在のパスを渡している。

```bash
git config --global --add safe.directory "$(pwd)"
```

これでリポジトリが信頼済みとして扱われる。

### 3. 方法B：所有者を自分に変える（自分のものとして使う場合）

そのリポジトリを自分専用として使うなら、所有者を現在のユーザーにそろえるほうが根本的な解決になる。

```bash
sudo chown -R "$(id -u):$(id -g)" .
```

`-R`で配下のファイルも含めて変更する。他のユーザーが同じディレクトリを使い続ける環境では、この方法は他のユーザーの作業を壊すので避ける。

### 4. 方法C：`*`で全部許可する（推奨しない）

```bash
git config --global --add safe.directory '*'
```

この設定でも解消はするが、すべてのディレクトリを信頼することになり、Git 2.35.2で入った安全対策を無効化するのと同じである。個人のCI用コンテナなど、使い捨てで他人が書き込めない環境に限定して使うべきだと考えている。

## 動作確認

隔離した`HOME`で、方法Aを実行して結果を確かめた（普段のグローバル設定を汚さないため）。

```bash
git config --global --add safe.directory "$(pwd)"
git status
```

```text
On branch master

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

エラーが消え、終了コードも0になった。登録した内容は次のコマンドで確認できる。

```bash
git config --global --get-all safe.directory
```

```text
/path/to/repo
```

`~/.gitconfig`には次のように記録される。

```text
[safe]
	directory = /path/to/repo
```

また、いったん設定を消して`'*'`を登録した場合も、同じく`git status`は正常に動作した。ただし、前述のとおりこれは安全対策を外す設定である。

## まとめ

- `dubious ownership`は、リポジトリの破損ではなく、ディレクトリの所有者と実行ユーザーが違うためにGitが実行を拒否している状態である。
- 信頼できるリポジトリなら`git config --global --add safe.directory <パス>`、自分で使うなら`chown`で所有者をそろえる。
- `safe.directory '*'`は手軽だが、安全対策を丸ごと外すため、使い捨ての環境以外では避ける。`.git/config`に書いても無効な点にも注意する。

Dockerのボリュームやrootで`sudo git`を実行した後など、所有者がずれる状況が原因のことが多い。同種のエラーに出会ったら、まず`stat`で所有者を確認する癖をつけておくと切り分けが早い。

## よくある質問

**Q: `sudo git pull`をしたら次から通常ユーザーでエラーになりました。**
`sudo`で作成・更新されたファイルの所有者がrootになったことが原因の可能性が高いです。`sudo chown -R "$(id -u):$(id -g)" .`で自分の所有に戻すと解消します。以後は`sudo`を付けずに実行するほうが安全です。

**Q: `.git/config`に`safe.directory`を書けば、リポジトリごとに共有できますか？**
できません。`safe.directory`はリポジトリ内のローカル設定からは読み込まれない仕様です。グローバル設定かシステム設定に登録する必要があります。

**Q: 登録した`safe.directory`を取り消すには？**
`git config --global --unset-all safe.directory`で全て削除できます。特定のパスだけ消す場合は`~/.gitconfig`の該当行を直接編集してください。

## 関連記事

- [git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順](/posts/git-submodule-not-initialized)
- [fatal: not a git repositoryが出る原因と解決手順](/posts/git-fatal-not-a-git-repository)
- [git worktree addで「is already used by worktree」の原因と解決手順](/posts/git-worktree-already-checked-out)
- [Linuxのファイル権限（chmod/chown）の基本](/posts/linux-file-permissions)
- [Linuxのユーザー管理（useradd/usermod）の基本](/posts/linux-user-management)
