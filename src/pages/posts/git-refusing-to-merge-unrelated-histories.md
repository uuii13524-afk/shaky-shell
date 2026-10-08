---
title: 'git pullで「refusing to merge unrelated histories」が出る原因と解決手順（Git 2.43）'
date: '2026-10-08'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pull origin mainが「fatal: refusing to merge unrelated histories」で止まる症状を再現して解説。共通の祖先がない原因と、--allow-unrelated-historiesで統合しREADMEの競合を解消する手順を紹介します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（症状）

ローカルで先に`git init`して作業を始めたプロジェクトを、あとから用意したリモートリポジトリと同期したかった。リモート側には、Web画面から作成したときに自動で付く初期コミット（READMEのみ）が入っている状態だった。

```bash
git remote add origin ../remote.git
git pull origin main
```

最初の`git pull`は、次のようなヒントを出して止まった。

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint: 
fatal: Need to specify how to reconcile divergent branches.
```

これは`pull`の統合方法を指定していないだけなので、マージ方式を明示して再実行した。すると今度は別のエラーになった。

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

## 環境

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- ローカル: `git init -b main`で作成、READMEを1つコミット済み
- リモート: ベアリポジトリ。別の場所で作られた初期コミット（READMEのみ）がある
- 検証はすべてローカルのベアリポジトリ（`../remote.git`）で再現した

## 試したこと

最初に疑ったのはブランチ名の食い違いだった。ローカルもリモートも`main`なので、これは違った。

次に`git fetch`してから、両方のコミットを並べて見た。

```bash
git fetch origin
git log --oneline --all --graph
```

```text
* 2aec163 first local commit
* 42aee34 initial commit on remote
```

2つのコミットが縦に並んでいるだけで、枝がつながっていない。親子関係のない独立した2本の履歴があることが見て取れた。

さらに、共通の祖先があるかを`merge-base`で確かめた。

```bash
git merge-base HEAD origin/main
echo "exit=$?"
```

```text
exit=1
```

何も表示されず、終了コードは1だった。共通の祖先コミットが1つも存在しないということになる。

## 原因

`git merge`と`git pull`は、2つのブランチの共通の祖先（merge base）を起点に、双方の差分を3方向マージする。ところが今回は、ローカルとリモートの履歴がそれぞれ別のルートコミットから始まっていて、共通の祖先がない。この状態でマージすると、意図しない別プロジェクトを混ぜてしまう恐れがあるため、Gitはデフォルトで統合を拒否する。これが`refusing to merge unrelated histories`の正体である。

Gitのバージョンについては、この拒否は2.9以降のデフォルト動作として知られている。それ以前のバージョンは黙ってマージしていたため、古い記事の手順がそのまま動かないことがある。

発生しやすいのは次のような場面だと考えられる。

- ローカルで`git init`して作業したあと、初期コミット入り（READMEやLICENSE付き）のリモートを作って同期しようとした
- 履歴を`git filter-repo`などで書き換えたり、リポジトリを作り直したりして、ルートコミットが変わった
- 別々に作った2つのリポジトリを1つにまとめたい

## 解決手順

### 1. 本当に統合してよい履歴か確認する

```bash
git log --oneline origin/main
```

別プロジェクトの履歴を取り込もうとしていないか、ここで確認する。今回はリモートがREADMEだけの初期コミットだと分かっているので、統合して問題なかった。

### 2. `--allow-unrelated-histories`を付けて統合する

```bash
git pull --no-rebase origin main --allow-unrelated-histories
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

「unrelated histories」のエラーは消えて、マージ自体は走った。ただし、両方に`README.md`が存在してどちらも新規追加扱い（add/add）のため、競合が起きた。

### 3. 競合を解消する

```bash
git status --short
cat README.md
```

```text
AA README.md
<<<<<<< HEAD
# local
=======
# remote
>>>>>>> 42aee348ee440d6e8b918e39cd3e62e00de6a5a5
```

`AA`は「両側で追加された」を表す。ファイルを開いて、残したい内容に手で書き換えた。今回は次の1行にした。

```bash
echo "# project" > README.md
git add README.md
git commit
```

コミットメッセージのエディタが開くので、デフォルトのマージメッセージのまま保存する。

## 動作確認

マージ後の履歴と、共通の祖先を確認した。

```bash
git log --oneline --graph
git merge-base HEAD origin/main
```

```text
*   2888d83 Merge branch 'main' of ../remote
|\  
| * 42aee34 initial commit on remote
* 2aec163 first local commit
42aee348ee440d6e8b918e39cd3e62e00de6a5a5
```

2本の履歴がマージコミットでつながり、`merge-base`もリモート側の初期コミットを返すようになった。以降の`git pull`は通常どおり動く。

## まとめ

- `refusing to merge unrelated histories`は、2つのブランチに共通の祖先がないときにGitが統合を拒否するエラー。ブランチ名の食い違いではなく、ルートコミットが別であることが原因。
- `git merge-base HEAD origin/main`が何も出さず終了コード1なら、このケースだと切り分けられる。
- 統合してよいと確認できたら`--allow-unrelated-histories`を付ける。READMEやLICENSEが両側にあるとadd/add競合になるので、そのつもりで解消する。
- 次回以降は、既存リモートを`git clone`してから作業を始めるか、空のリモート（READMEなし）を作ると避けられる。

## よくある質問

**Q: `--allow-unrelated-histories`を付けるとデータが消えませんか？**
今回の検証では、競合を手で解消するまで両方の内容が作業ツリーに残りました。ただし競合解消で片方を捨てれば、その内容は最新のファイルからは消えます（履歴にはコミットとして残ります）。実行前に`git log origin/main`で中身を確認するのが安全です。

**Q: `git pull`のたびに`--no-rebase`を付けるのが面倒です。**
`git config pull.rebase false`でマージ方式を既定にできます。このエラー自体とは別問題ですが、今回のように最初の`pull`が止まる場面では、先にこの設定をしておくと原因の切り分けが一段楽になります。

**Q: リモートの履歴は不要で、ローカルで上書きしたい場合は？**
`git push --force`で上書きする方法もありますが、リモートの履歴が失われます。共有リポジトリでは他の人の作業を壊す恐れがあるため、チームで合意してから実行してください。

## 関連記事

- [git pushが「rejected」になる原因と解決手順](/posts/git-push-rejected-fix)
- [git pullでマージ競合が出たときの解決手順](/posts/git-pull-merge-conflict)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
