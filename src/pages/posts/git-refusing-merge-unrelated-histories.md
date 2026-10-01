---
title: 'git pullで「fatal: refusing to merge unrelated histories」の原因と解決手順【Git 2.43】'
date: '2026-10-01'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullやgit mergeで「fatal: refusing to merge unrelated histories」が出て止まる症状を解説。ローカルとリモートで共通の祖先コミットがないのが原因です。--allow-unrelated-historiesとgit pull --rebaseの使い分けと、実際に再現した出力を紹介します。'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## やりたかったこと（または「症状」）

手元で先に`git init`してコミットを作っておき、あとからリモートリポジトリを`git remote add`でつないで、リモート側の内容を取り込もうとしました。リモートには別のところで作った`README.md`の初回コミットだけが入っています。

```bash
git pull origin main
```

すると、次のエラーで止まりました。

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

`git merge origin/main`でも結果は同じです。コンフリクトのメッセージではなく「履歴が無関係なので拒否する」という内容なので、`git pull-merge-conflict`系の対処とは別物だと気づくまで少し時間がかかりました。

## 環境

- OS: Linux（カーネル6.18系）
- Git: 2.43.0
- 構成: ローカルの作業リポジトリ`work`、リモート役のベアリポジトリ`remote.git`、リモートに最初のコミットを置くための別クローン`other`
- ブランチ名: `main`（両方とも`git init -b main`で作成）
- `pull.rebase`: `false`（merge方式）に設定

この記事の出力は、上の構成をローカルで作って実際に実行したものです。GitHubなど外部サービスは使っていません。

## 試したこと

### 1. まず`git pull`だけを実行した

`pull.rebase`を設定していない状態で`git pull origin main`を実行すると、`unrelated histories`のエラーではなく、別のメッセージが先に出ました。

```text
hint: You have divergent branches and need to specify how to reconcile them.
（中略）
fatal: Need to specify how to reconcile divergent branches.
```

これはGit 2.27以降の仕様で、merge・rebase・fast-forwardのどれで統合するかを決めていないと出る警告です。`git config pull.rebase false`でmerge方式を指定したところ、ようやく本題のエラーに到達しました。つまり「divergent branches」の警告と「unrelated histories」のエラーは別の問題で、前者を解消すると後者が見えてくるケースがあります。

### 2. 共通の祖先があるか確認した

履歴が本当に無関係なのか、`git merge-base`で確認しました。

```bash
git fetch origin
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

何も表示されず、終了コードが1でした。`git merge-base`は共通の祖先コミットが見つかれば、そのハッシュを出力します。見つからなければ何も出力せず1を返します。これで、ローカルの`main`とリモートの`main`には共通の祖先がない、と確認できました。

### 3. pushも試したが拒否された

ついでに、先にpushしてしまえば解決するのではと考えて試しました。

```bash
git push origin main
```

```text
To ../remote.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. If you want to integrate the remote changes,
hint: use 'git pull' before pushing again.
```

当然ですが、リモートの履歴を上書きできないので拒否されます。`--force`で押し切ると、リモート側の初回コミットが消えるので、ここでは選びませんでした。

## 原因

Gitは`git merge`のとき、2つのブランチの共通の祖先を探して三方向マージ（3-way merge）を行います。ところが今回は、ローカルの`main`とリモートの`main`が、それぞれ別々の最初のコミット（root commit）から始まっていて、共通の祖先がありません。

Git 2.9以降、この状態でのmergeはデフォルトで拒否されます。別々の用途で作ったリポジトリを誤って結合する事故を防ぐための安全装置です。ここから、エラーの原因は「ローカルで`git init`した履歴と、リモートで作られた履歴が、そもそも別系統だった」ことだと考えられます。`git merge-base`が何も返さなかった事実とも一致します。

典型的に起きやすい場面は次のとおりです。

- ローカルで`git init`して作業を始めたあとで、GitHub上に`README`付きの空でないリポジトリを作ってしまった
- 別のリポジトリのコピーを、同名の新規リポジトリにつなぎ直した
- `git filter-repo`などで履歴を書き換えたあと、古いリモートと再接続した

## 解決手順

状況に応じて、方法は2つあります。どちらも実際に試して成功しました。

### 方法A: `--allow-unrelated-histories`でmergeする

両方の履歴をそのまま残して統合したいときの方法です。

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

`--allow-unrelated-histories`で共通の祖先なしのmergeを許可し、`--no-edit`でマージコミットメッセージの編集をスキップします。

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

ファイル名が衝突していなかったので、コンフリクトなしでmergeできました。同名のファイルが両方にある場合は、通常のmergeと同じくコンフリクトが出るので、手動で解消してからコミットします。

### 方法B: `git pull --rebase`で履歴を一本化する

マージコミットを作らず、ローカルのコミットをリモートの先頭の上に積み直したいときの方法です。

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

意外だったのは、こちらは`--allow-unrelated-histories`が不要だった点です。rebaseは共通の祖先を前提としないため、ローカルの1コミットがリモートの`Initial commit`の上に載り直されました。

## 動作確認

方法Bのあとの履歴は、次のように一直線になりました。

```bash
git log --oneline --graph
```

```text
* 9e36887 local first commit
* afd93a6 Initial commit
```

`ls`でも、リモート由来の`README.md`とローカルの`local.txt`が両方そろっていました。

方法Aを選んだ場合は、次のようにマージコミットが入ります。

```text
*   8d47f79 Merge branch 'main' of ../remote
|\  
| * 8a6cd5e Initial commit
* 07a76a6 local first commit
```

そのあと`git push origin main`が通ることも確認しました。

```text
To ../remote.git
   8a6cd5e..8d47f79  main -> main
```

## まとめ

- `refusing to merge unrelated histories`は、ローカルとリモートに共通の祖先コミットがないときに出る。`git merge-base`が何も返さなければ確定
- 履歴を両方残すなら`--allow-unrelated-histories`、一直線にしたいなら`git pull --rebase`
- `git push --force`で上書きすると、リモート側の履歴が消えるので、中身を確認せずには使わない

同種の問題として、GitHubで空でないリポジトリを作ってしまった場合は、新規プロジェクトでは最初から`git clone`してから作業を始めるのが確実です。すでにローカルで作業してしまったときは、今回の2つの方法で対処できます。

なお、ここで確認した動作はGit 2.43.0でのものです。デフォルトの挙動はバージョンによって異なる場合があります。

## よくある質問

**Q: `--allow-unrelated-histories`を付けても安全ですか？**
片方のリポジトリを意図せず別のものとつなぎ直した場合は、無関係な履歴が混ざってしまいます。実行前に`git log origin/main`で、中身が想定どおりか確認してください。

**Q: `git pull --rebase`と`--allow-unrelated-histories`のどちらを使うべきですか？**
ローカルのコミットが少なく、履歴をきれいに保ちたいなら`--rebase`が向いています。両方の歴史をそのまま残したい、または共有済みのコミットがあって書き換えたくない場合はmergeを選びます。

**Q: エラーを避けるにはどうすればいいですか？**
リモートに先にリポジトリを作り、`git clone`してから作業を始めると、最初から共通の祖先を持つ状態になります。

## 関連記事

- [git pushが拒否されたときの対処法](/posts/git-push-rejected-fix)
- [git pullでマージコンフリクトが起きたときの解決方法](/posts/git-pull-merge-conflict)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [git remoteの基本操作まとめ](/posts/git-remote-operations)
- [GitHubへ初めてpushする手順](/posts/github-first-push)
