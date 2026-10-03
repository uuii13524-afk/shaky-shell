---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順'
date: '2026-10-03'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'ローカルで先にgit initしてコミットした後、リモートのmainをpullすると fatal: refusing to merge unrelated histories で止まる症状を解説。共通の祖先がない原因の確認方法と、--allow-unrelated-historiesで統合する手順を紹介します。'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## 症状

ローカルで先に`git init`してコミットを重ね、あとから空ではないリモートリポジトリ（READMEが1つだけ入ったもの）を`origin`として登録した。`git push`は拒否されたので、案内に従って`git pull`したところ、マージに入る前に次のエラーで止まった。

```text
fatal: refusing to merge unrelated histories
```

コンフリクトのエラーなら見慣れているが、これはファイルの競合ではなく、マージそのものを拒否されている。最初は何を直せばいいのか分からなかった。

## 環境

- OS: Linux
- Git: 2.43.0
- ローカルリポジトリ: `git init -b main`で作成、コミット1件（`app.py`のみ）
- リモート: README.mdだけをコミットした別履歴のmainブランチ（検証ではベアリポジトリをローカルに用意）
- Git設定: `pull.rebase`などは未設定のデフォルト

この記事のコマンドと出力は、上記の環境で作った検証用リポジトリで実際に実行した結果をそのまま載せている。

## 試したこと

まず、ローカルのmainをそのままpushした。

```bash
git push origin main
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
```

ヒントに従って`git pull origin main`を実行したが、設定が未指定のGit 2.43.0では、まず別のエラーで止まった。

```text
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

これは「mergeかrebaseかを選べ」という要求なので、`--no-rebase`を付けてmergeを選び直した。

```bash
git pull origin main --no-rebase
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

ここで初めて、冒頭のエラーに到達した。`git pull`は内部で`git fetch`と`git merge`を順に実行しており、fetchは成功しているので、拒否しているのは後半のmerge側だと分かる。

## 原因

`git merge`は、2つのブランチの共通の祖先コミット（merge base）を見つけて、そこからの差分を3-wayで統合する。ローカルとリモートで別々に`git init`していると、どちらのコミットもルートが異なり、共通の祖先が存在しない。Gitはこの状態を「無関係な履歴」と見なし、デフォルトでは誤操作の可能性が高いとして統合を拒否する。この動作は2.9以降のデフォルトで、`--allow-unrelated-histories`を付けたときだけ許可される。

共通の祖先がないことは、次のコマンドで確認できる。

```bash
git fetch origin
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

`merge-base`が何も出力せず終了コード1で終わるのが、共通の祖先がないことの証拠になる。履歴が関連していれば、ここにコミットのハッシュが1つ表示される。

## 解決手順

### 1. 状態を確認する

統合前に、両者のコミットを見比べる。

```bash
git log --oneline --all --graph
```

```text
* fd5d0d8 first local commit
* fd4f79a first local commit
* 275e74c Initial commit
```

縦に1本ずつ別々のルートが並んでいる。つながっておらず、2本のルートが独立して存在していることが分かる。同名のコミットメッセージが並んでいるが、ハッシュが違うので別物である。

### 2. 意図して統合する

両方の履歴を残したい場合は、フラグを付けてmergeする。

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit`はマージコミットメッセージのエディタ起動を省くためのもの。両側で同名のファイルがあればこの段階でコンフリクトが出るので、通常のコンフリクト解消と同じ手順で対処する。今回は`README.md`と`app.py`で名前が重ならなかったため、自動で統合された。

### 3. 結果を確認してpushする

```bash
git log --oneline --graph
ls
git push origin main
```

## 動作確認

統合後のログは次のようになった。

```text
*   8591421 Merge branch 'main' of ../remote
|\  
| * fd4f79a first local commit
| * 275e74c Initial commit
* fd5d0d8 first local commit
```

`ls`の結果は`README.md`と`app.py`の両方が存在する状態で、`git push origin main`は`fd4f79a..8591421  main -> main`と成功した。マージコミットを境に2本の履歴が1つにつながり、以降は通常の`git pull`が通る。

## 補足: マージコミットを作りたくない場合

履歴を一直線にしたいなら、ローカルのコミットをリモートの上に載せ直す方法もある。

```bash
git pull origin main --rebase
```

この方法は、今回の検証では`Successfully rebased and updated refs/heads/main.`と表示されて成功し、履歴は1本になった。ただしローカルのコミットのハッシュは書き換わる。すでに他の人がそのコミットを取得している場合は、rebaseは避けてmergeを選ぶ。

また、リモート側のREADMEが不要で、ローカルの履歴だけを正としたい場合は、`--allow-unrelated-histories`で統合するのではなく、リモートの内容を意図的に上書きする運用（`git push --force-with-lease`）もある。ただしこれはリモートの履歴を失う操作なので、本当に捨てて問題ないリポジトリかを確認してから行う。

## まとめ

- `fatal: refusing to merge unrelated histories`は、ローカルとリモートに共通の祖先コミットがないときにmergeが拒否されるエラー。`git merge-base`が終了コード1で何も返さなければ原因は確定する。
- 両方の履歴を残すなら`git pull origin main --allow-unrelated-histories --no-rebase`、履歴を一本化したいなら`--rebase`を使う。
- 同種の症状は、GitHubで「README付きで新規作成」したリポジトリに、ローカルの既存プロジェクトを初めてpushするときによく起きる。次回からは、リモートを空で作るか、先に`git clone`してからファイルを追加するとこのエラーを避けられる。

## よくある質問

**Q: `--allow-unrelated-histories`を付けるとデータが消えませんか？**
消えません。両方のコミットを残したまま、新しいマージコミットを作って統合します。同名ファイルが両側にあれば通常のコンフリクトとして止まるので、勝手に上書きされることもありません。

**Q: `git pull`に`--allow-unrelated-histories`を付けたのに「Need to specify how to reconcile divergent branches」と出ます。**
別のエラーです。`pull.rebase`が未設定のため、mergeかrebaseかの指定が求められています。`--no-rebase`か`--rebase`を併せて付けるか、`git config pull.rebase false`で既定値を決めてください。

**Q: 本当に無関係な2つのリポジトリを1つにまとめたいときも同じ手順ですか？**
基本は同じですが、ディレクトリ構成がぶつかりやすいので、サブディレクトリに移してからコミットしておくと、統合後に整理しやすくなります。

## 関連記事

- [git pushがrejectedされる原因と解決手順](/posts/git-push-rejected-fix)
- [git pullでコンフリクトが出たときの解決方法](/posts/git-pull-merge-conflict)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [fatal: not a git repositoryの原因と解決手順](/posts/git-fatal-not-a-git-repository)
