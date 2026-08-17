---
title: 'git commitで「Unable to create .git/index.lock: File exists」が出る原因と解決手順'
date: '2026-08-17'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git commitやgit addを実行すると「Unable to create .git/index.lock: File exists」で失敗する症状を解説。原因となる.git/index.lockの役割と、安全に削除して復旧する手順、git statusは通っても書き込み系コマンドだけ失敗する理由を紹介します。'
ja_tags: ['Git', 'index.lock', 'commit']
en_tags: ['Git', 'index.lock', 'commit']
---

## やりたかったこと（または「症状」）

作業中のリポジトリで、いつも通り変更をコミットしようとした。

```bash
git commit -m "first commit"
```

```text
fatal: Unable to create '/path/to/repo/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

`fatal`で止まり、コミットは作成されなかった。直前にエディタや他のgitコマンドを開いた覚えはなく、ターミナルも1つしか開いていなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- 症状発生リポジトリ: ローカルの通常のgitリポジトリ（`.git`はワーキングディレクトリ内、外部ストレージやネットワークドライブではない）

## 試したこと

まず`git status`を実行して、リポジトリ自体が壊れていないか確認した。

```bash
git status
```

```text
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   file.txt
```

意外なことに`git status`は普通に成功し、ステージ済みの変更も正しく表示された。「リポジトリが壊れている」わけではなく、書き込みを伴う操作だけが失敗している可能性が高いと判断した。実際に`git add`でも同じエラーが再現した。

```bash
git add file2.txt
```

```text
fatal: Unable to create '/path/to/repo/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

`git status`（読み取り主体の操作）は通るのに、`git add`や`git commit`（インデックスへの書き込みを伴う操作）だけ失敗する、という切り分けができた。エラーメッセージにも「`.git/index.lock`というファイルが既に存在している」と明記されていたので、まずそのファイルの実在を確認した。

```bash
ls -la .git/index.lock
```

```text
-rw-r--r-- 1 root root 0 Aug 17 00:10 .git/index.lock
```

サイズ0バイトの`index.lock`が実際に残っていた。中身が空という点も、正常な処理中に一時的に作られるロックファイルの特徴と一致していた。

## 原因

Gitは`.git/index`（ステージング内容を保持するファイル）を安全に書き換えるため、書き込み系の操作を行う前に`.git/index.lock`という一時ファイルを作成し、処理が終わったら削除する、という仕組みを使っている。他のgitプロセスが同時に同じインデックスを書き換えて壊してしまうことを防ぐための排他制御で、`index.lock`が存在する間は「今このリポジトリのインデックスを別プロセスが編集中」とみなされ、新たに書き込み系コマンドを実行しようとすると今回のエラーで止まる。

正常な流れでは、コマンドの完了と同時に`index.lock`は自動的に削除される。今回`index.lock`が残っていたのは、直前に実行していたgitコマンドが完了前に強制終了した（ターミナルの強制クローズやプロセスのkill、エディタのフリーズなど）ためと考えられる。ロックを持っていたプロセス自体は既に存在しないのに、ロックファイルという“痕跡”だけが消えずに残ってしまい、以降のgitコマンドが「まだ誰かが使用中」と誤認し続ける状態になっていた。

`git status`が通っていたのは、`status`が基本的にインデックスを読み取るだけで書き換えを行わないため、ロックの有無に関係なく実行できたからだった。書き込みを伴う`add`・`commit`・`merge`などのコマンドだけが影響を受ける、という切り分け結果とも一致する。

## 解決方法

### 1. 本当に他のgitプロセスが動いていないか確認する

ロックファイルを消す前に、同じリポジトリに対して別のgitコマンドやIDEのGit連携機能が実際に動作中でないかを確認する。動作中のプロセスがある状態でロックファイルを削除すると、そのプロセスとインデックスの内容が競合して壊れる可能性があるため、必ず先に確認する。

```bash
ps aux | grep -i git
```

該当するプロセスが見当たらない、かつエディタやIDEも閉じている状態であることを確認できたら次に進む。

### 2. `.git/index.lock`を手動で削除する

プロセスが残っていないと確認できたら、エラーメッセージの指示通りロックファイルを削除する。

```bash
rm .git/index.lock
```

### 3. 削除後に書き込み系コマンドを再実行する

```bash
git add file2.txt
git commit -m "second commit"
```

```text
[master 2e8c229] second commit
 1 file changed, 1 insertion(+)
```

エラーが出ずにコミットが完了した。

## 動作確認

```bash
git log --oneline
git status
```

```text
2e8c229 second commit
35f7321 first commit
On branch master
nothing to commit, working tree clean
```

`index.lock`削除後は`add`・`commit`とも正常に完了し、`git status`も「nothing to commit」まで進むことを確認できた。

## ハマったポイント

- `git status`が成功していたせいで、最初は「リポジトリは正常」と早合点しかけた。実際には読み取り系と書き込み系で挙動が分かれているだけで、根本原因の切り分けにはならなかった
- `index.lock`はサイズが0バイトで、中身から手がかりを得ることはできない。存在そのものが「直前の処理が異常終了した痕跡」であって、内容を調べても意味がない
- 他のgitプロセスが本当に動いている状態でロックファイルを消すと競合の原因になるため、削除前に`ps aux`などでプロセスの有無を確認する手順を省略しないようにした

## よくある質問

**Q: `index.lock`は削除しても安全ですか？**
同じリポジトリに対して動作中のgitプロセスが存在しないことを確認できていれば、基本的に安全に削除できる。動作中のプロセスがある状態で削除すると、そのプロセスの書き込みと競合してインデックスが壊れる可能性があるため、必ず先にプロセスの有無を確認する。

**Q: なぜ`git status`は失敗しなかったのですか？**
`status`はインデックスの内容を読み取って表示するだけで、書き換えを行わないため。`.git/index.lock`は書き込み系コマンドの排他制御に使われるファイルなので、読み取りのみの操作は影響を受けない。

**Q: 今後同じ状況を防ぐ方法はありますか？**
git実行中にターミナルを強制終了したりプロセスをkillしたりしないことが基本だが、完全には避けられない。同じ症状が起きたら、まずプロセスの有無を確認したうえで`.git/index.lock`を削除する、という今回の手順を覚えておくと復旧が早い。

## 関連記事

- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [git stashの使い方](/posts/git-stash-usage)
- [fatal: not a git repositoryの原因と対処法](/posts/git-fatal-not-a-git-repository)
- [git reflogでコミットを復元する方法](/posts/git-reflog)
