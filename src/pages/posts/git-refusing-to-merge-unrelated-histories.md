---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順【Git 2.43】'
date: '2026-10-09'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullで「fatal: refusing to merge unrelated histories」が出てマージできない症状を再現して解説。ローカルとリモートに共通の祖先コミットがないことが原因です。--allow-unrelated-historiesの使いどころとaddの競合の解消手順まで紹介します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（または「症状」）

ローカルで`git init`して数コミット書いたあと、GitHub側に先に作っておいた空でないリポジトリ（READMEだけが入っている状態）と合流させようとした。`git remote add origin`でリモートを登録して、そのまま`git pull`を実行した。

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

fetch自体は成功していて`origin/main`も作られているのに、マージの段階で`fatal: refusing to merge unrelated histories`と言われて止まる。終了コードは128だった。`git push`も当然通らないので、ローカルの作業をリモートに載せられない。

なお、この記事のログはすべてサンドボックス上で実際にコマンドを実行して得た出力である（ローカル用とリモート用のリポジトリを別々に`git init`して再現した）。ハッシュ値や作業ディレクトリ名は検証環境のものなので、読む人の環境では異なる。

## 環境

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- ローカル: `git init -b main`で作成。`app.txt`だけをコミットした1コミットのリポジトリ
- リモート: ベアリポジトリ。別のクローンから`README.md`だけをコミットしてpush済み
- 設定: グローバルのgit設定なし（`pull.rebase`未設定）

## 試したこと

### 1. 最初の`git pull`は別のエラーで止まった

最初は`--no-rebase`を付けずに`git pull origin main`と打った。Git 2.43.0でグローバル設定が空の場合、`pull.rebase`が未設定なので次のように言われる。

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
（中略）
fatal: Need to specify how to reconcile divergent branches.
```

これは「mergeするのかrebaseするのかを決めてください」という別の話で、今回の本題ではない。`--no-rebase`でmergeを指定すると、冒頭の`refusing to merge unrelated histories`に変わる。

### 2. 履歴の形を確認した

ローカルの履歴と、fetchしてきた`origin/main`の履歴をそれぞれ見た。

```bash
git log --oneline
git log --oneline origin/main
```

```text
50b54e2 Initial local commit
48b9326 Initial commit (README)
```

1行目がローカル、2行目がリモートである。どちらも「最初のコミット」から始まっていて、親が存在しない。つまり別々の場所から生えた2本の木になっている。

### 3. 共通の祖先があるかを`merge-base`で確かめた

```bash
git merge-base HEAD origin/main
echo $?
```

```text
1
```

何も出力されず、終了コード1で終わった。これは共通の祖先コミットが見つからないという意味になる。ここまでで「履歴が無関係だから拒否されている」と確信できた。

## 原因

Gitのマージは、2つのブランチの共通の祖先（merge base）を起点に、それぞれの差分を3-wayで統合する仕組みになっている。`git merge-base HEAD origin/main`が何も返さない、つまり共通の祖先が存在しない2本の履歴は、Git 2.9以降では既定でマージが拒否される。誤って無関係なリポジトリ同士を混ぜる事故を防ぐための安全装置である。

今回の場合、ローカルは`git init`から自分でコミットを積み、リモートは別の場所（GitHubのWeb画面やテンプレートからの作成など）で最初のコミットが作られていた。互いのルートコミットが別物なので、共通の祖先がない。これは壊れているわけではなく、「同じリポジトリから分岐した履歴ではない」ことをGitが正しく検知しているだけの状態だった。

## 解決手順

### 方法A: `--allow-unrelated-histories`で合流させる（今回採用）

ローカルとリモートの両方の履歴を残して1本につなげたい場合は、このオプションを付ける。

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit`はマージコミットのメッセージ編集画面を開かないための指定である。ファイルが重複しなければ、このように競合なしでマージコミットが作られる。

### 方法B: `git pull --rebase`なら拒否されないケースを確認した

同じ状況で`--rebase`を試すと、手元の検証ではエラーにならなかった。

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)Successfully rebased and updated refs/heads/main.
```

ローカルのコミットをリモートの先頭に付け替える形で、履歴が一直線になった。マージコミットを残したくないならこちらでもよい。ただしこの挙動はGitのバージョンによって差がありうるため、自分の環境で確認してからにしてほしい（今回確認したのはGit 2.43.0のみ）。

### 方法C: そもそも合流させない

リモートのREADMEが不要で、ローカルの履歴だけを正としたい場合は、無理に`pull`しない。空のリポジトリに対して`git push -u origin main`するか、リモート側を作り直す方が安全である。リモートの履歴を上書きする`--force`は、他の人の作業を消す可能性があるため、中身を確認せずに使ってはいけない。

## 動作確認

方法Aのあとで履歴とファイルを確認した。

```bash
git log --oneline --graph
ls
```

```text
*   c55bc9d Merge branch 'main' of ../remote
|\  
| * 48b9326 Initial commit (README)
* 50b54e2 Initial local commit
README.md
app.txt
```

2本の履歴がマージコミット`c55bc9d`でひとつにつながり、`README.md`と`app.txt`の両方が手元に揃った。この状態なら通常どおり`git push origin main`できる。

## ハマったポイント

### 同じファイル名が両方にあると競合する

READMEをローカルでも作っていた場合、`--allow-unrelated-histories`を付けてもマージ自体は始まるが、共通の祖先がないため両方が「新規追加」扱いになり、競合する。実際に両側で`README.md`を作って試すと次のようになった。

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

`git status -sb`では`AA README.md`と表示される（両方が追加した状態）。この場合は普通のマージ競合と同じく、`README.md`を開いて内容を整えてから`git add README.md`、続けて`git commit`で完了する。競合の直し方そのものは[git pullでマージ競合が起きたときの対処](/posts/git-pull-merge-conflict)にまとめてある。

### オプションを付ければ何でも安全というわけではない

`--allow-unrelated-histories`は「本当に別物の履歴を意図して混ぜる」ときのためのものである。リモートURLを間違えて別のプロジェクトを登録していた場合でも、このオプションを付けるとマージできてしまう。付ける前に`git remote -v`でURLが正しいか見直したほうがよい。

## まとめ

- `fatal: refusing to merge unrelated histories`は、`git merge-base`が何も返さない（共通の祖先がない）2本の履歴をマージしようとしたときの安全装置である
- 意図して合流させるなら`git pull --no-rebase --allow-unrelated-histories`。履歴を一直線にしたいなら`--rebase`も選択肢になる
- 同名ファイルが両側にあると`add/add`の競合になる。オプションを付ける前に`git remote -v`でリモートの取り違えがないか確認する

同じように「push/pullが拒否される」系のエラーは[git pushがrejectedされたときの直し方](/posts/git-push-rejected-fix)や[git remoteの基本操作](/posts/git-remote-operations)も参照してほしい。

## 関連記事

- [git pullでマージ競合が起きたときの対処](/posts/git-pull-merge-conflict)
- [git pushがrejectedされたときの直し方](/posts/git-push-rejected-fix)
- [git remoteの基本操作](/posts/git-remote-operations)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [GitHubへ初めてpushする手順](/posts/github-first-push)
