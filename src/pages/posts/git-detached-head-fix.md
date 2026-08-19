---
title: 'Gitでdetached HEAD stateになった時の対処法'
date: '2026-07-16'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git checkoutで古いコミットに移動しdetached HEAD状態で作業し、ブランチ切替後にコミットがgit logから消えた症状を解説します。git reflogで見つけてgit branchで復元する手順を紹介します。'
ja_tags: ['Git', 'detached HEAD', 'ブランチ', 'checkout']
en_tags: ['Git', 'detached-head', 'branch', 'checkout']
---

## やりたかったこと

過去のコミットの状態を確認しようと `git checkout` で古いコミットハッシュに直接移動した。そのまま作業を続けて何回かコミットしてしまい、`git switch main` でmainブランチに戻ったところ、さっき積んだはずのコミットが `git log` からきれいに消えていた。ターミナルを遡ると、コミットハッシュへ移動した時点で次のようなメッセージが表示されていたことに気づいた。

```text
Note: switching to '3f2a1b9'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

HEAD is now at 3f2a1b9 fix: update config parser
```

このとき警告文の意味をちゃんと読んでいなかったのが、後で困る原因になった。

---

## 環境

- OS: Ubuntu 22.04 / macOS 14 (Sonoma)
- Git: 2.42.0
- エディタ: VS Code 1.89
- シェル: bash 5.1

---

## 試したこと

最初に、detached HEAD状態のまま気づかずコミットを2つ積んでしまい、`git switch main` でmainブランチに戻ろうとした。ブランチの切り替え自体は成功したが、ターミナルには次のような警告が流れていた。

```text
Warning: you are leaving 1 commit behind, not connected to
any of your branches:

  3f2a1b9 fix: update config parser

If you want to keep it by creating a new branch, this may be a good time
to do so with:

 git branch <new-branch-name> 3f2a1b9

Switched to branch 'main'
```

この時点では「mainに戻れたから大丈夫だろう」と警告を読み飛ばしてしまった → その後 `git log` を確認したら、さっき作ったコミットがどこにも表示されなくなっていた → mainブランチを含め、どのブランチのrefからも参照されていないコミットは `git log` の通常表示には出てこないため、実際には残っているのに消えたように見えていたのが原因だった。

---

## 原因

Gitのブランチは特定のコミットを指す「名前付きの矢印」のようなものだが、detached HEAD状態ではHEADがブランチ名を経由せず、コミットハッシュを直接指している。この状態で新しくコミットを作ると、そのコミットはどのブランチからも参照されない「宙に浮いた」コミットになる。ブランチを切り替えると、参照されていないコミットは通常のGitコマンド（`git log` など）の表示対象から外れるため、パッと見は消えたように見える。実際にはすぐに削除されるわけではなく、`git gc` によるガベージコレクションが実行されるまでの間はreflogを通じて追跡可能な状態で残っている。

---

## 解決方法

### まだdetached HEAD状態にいる場合はブランチを作って保存する

```bash
git switch -c recovered-work
```

```text
Switched to a new branch 'recovered-work'
```

新しいブランチ名を割り当てることで、detached HEAD状態で作ったコミットに正式な参照(ref)ができる。refが付いたコミットはブランチを切り替えても消えず、通常のコミットと同じように扱える。

### すでにブランチを離れてしまった場合はreflogで探す

```bash
git reflog
```

```text
3f2a1b9 HEAD@{0}: commit: fix: update config parser
a1b2c3d HEAD@{1}: checkout: moving from main to 3f2a1b9
7e6d5c4 HEAD@{2}: checkout: moving from feature/parser to main
```

`git reflog` はHEADが移動した履歴を記録しているため、detached HEAD状態で作ったコミットのハッシュも一覧に残っている。目的のコミット（ここでは `3f2a1b9`）を見つけたら、そのハッシュを指定してブランチを作り直す。

```bash
git branch recovered-work 3f2a1b9
git branch
```

```text
  main
* recovered-work
```

これで消えたように見えていたコミットに、再びブランチ経由でアクセスできるようになる。

---

## ハマったポイント

- detached HEAD状態でコミットを2つ積んでしまい、`git log` では普通に自分のコミットが見えていたので、その場では何も異常に気づかなかった。`git status` を実行して初めて `HEAD detached at 3f2a1b9` という表示に気づいた
- `git switch main` を実行した際に流れた警告メッセージを読み飛ばしてしまい、後から `git log` でコミットが消えていることに気づいて焦った。警告はスクロールで流れて一瞬しか表示されないので、実行直後に必ず読むようにした
- `git reflog` の一覧は長くなりがちで、目的のコミットがどれかすぐに分からなかった。コミットメッセージを手がかりに `git reflog | grep "fix: update config parser"` のように絞り込むと見つけやすかった
- 同僚が使っていたブランチ名と同じ名前で `git branch recovered-work 3f2a1b9` を実行しようとしたら `fatal: A branch named 'recovered-work' already exists` となり失敗した。既存ブランチと重複しない名前を付け直す必要があった
- reflogのエントリはずっと残るわけではなく、デフォルトでは到達不能なコミットは30日ほどで `git gc` の対象になる。放置している間に消えてしまう可能性があるため、気づいたらすぐに復元するべきだった

---

## よくある質問

**Q: git detached HEAD state から抜け出すには？**
`git switch main` や `git switch ブランチ名` のように、既存のブランチ名を指定して切り替えると解除できます。ただし切り替え前に作業中のコミットを保存していないと、警告の通り宙に浮いた状態になるので、`git switch -c 新しいブランチ名` で先に保存しておくのが安全です。

**Q: git checkout でdetached HEADにならないようにするには？**
コミットハッシュやタグを直接指定する `git checkout <hash>` は仕様上必ずdetached HEAD状態になります。ブランチを作りながら移動したい場合は `git checkout -b 新しいブランチ名 <hash>` または `git switch -c 新しいブランチ名 <hash>` を使うと、その場で参照付きのブランチが作られるため回避できます。

**Q: git reflogの保存期間はどれくらい？**
デフォルトでは、他のrefから到達可能なコミットのreflogエントリは90日、到達不能なコミットのエントリは30日で `git gc` の対象になります。設定は `git config gc.reflogExpire` と `git config gc.reflogExpireUnreachable` で確認・変更できます。

---

## 関連記事

- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [git reflogで消えたコミットを復元する方法](/posts/git-reflog)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
