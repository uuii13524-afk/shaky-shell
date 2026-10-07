---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順【Git 2.43】'
date: '2026-10-07'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullで「fatal: refusing to merge unrelated histories」が出て止まる症状を再現しました。ローカルとリモートの履歴が無関係な原因と、--allow-unrelated-historiesやrebaseで安全に統合する手順を解説します。'
ja_tags: ['Git', 'unrelated histories', 'git pull', 'git merge']
en_tags: ['Git', 'unrelated histories', 'git pull', 'git merge']
---

## 症状

ローカルで作り始めたプロジェクトを、あとから作ったリモートリポジトリにつなげて `git pull` したところ、次のエラーで止まりました。

```text
From ../bare
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

やりたかったのは、リモート側にだけ存在するファイル（`LICENSE`）をローカルに取り込んでから `push` することです。fetch 自体は成功していて `origin/main` もできているのに、マージだけが拒否されます。終了コードは `128` でした。

## 環境

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- 構成: ローカルリポジトリ + ローカルの bare リポジトリ（`../bare`）をリモートとして使用

GitHub 上のリポジトリでも起きる現象ですが、今回の再現は bare リポジトリで行いました。bare リポジトリを GitHub の代わりに見立て、別のクローンから「Initial commit」を push してリモート側に独立した履歴を作っています。

## 試したこと

まず、再現手順を整理します。ポイントは「ローカルとリモートで、最初のコミットがそれぞれ別に作られている」ことです。

```bash
# ローカル側: 先にリポジトリを作って最初のコミットを作る
git init -b main
echo "# my-app" > README.md
git add README.md
git commit -m "first commit"
git remote add origin ../bare
```

リモート側には、別の場所から `LICENSE` だけを含む「Initial commit」を push 済みの状態にしておきます。この状態でそのまま `git push -u origin main` を実行すると、次のように拒否されます。

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../bare'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
```

ヒントに従って `git pull origin main` を実行すると、今度は「divergent branches」のヒントが出ます。Git 2.43.0 では `pull.rebase` が未設定だと、マージするのか rebase するのかを指定しない限り先に進めません。

```text
hint: You have divergent branches and need to specify how to reconcile them.
fatal: Need to specify how to reconcile divergent branches.
```

そこで `--no-rebase`（マージ）を明示して実行したところ、冒頭のエラーになりました。

```bash
git pull --no-rebase origin main
```

```text
fatal: refusing to merge unrelated histories
```

## 原因

2つのブランチに共通の祖先コミットがないためです。`git log` でそれぞれの履歴を見ると、ローカルの `first commit` とリモートの `Initial commit` は別々のルートコミットで、どちらも親を持ちません。

```bash
git log --oneline --all --graph
```

```text
* c397f9e first commit
* ec06513 Initial commit
```

2本の線が一度も交わっていないのが見て取れます。`git merge-base HEAD FETCH_HEAD` を実行すると何も出力されず、終了コードが `1` になりました。共通祖先が存在しない証拠です。

Git 2.9 以降、共通祖先のない履歴同士のマージはデフォルトで拒否されるようになっています。リポジトリの取り違えで無関係な履歴を混ぜてしまう事故を防ぐための安全装置です。私のケースでは、ローカルで `git init` したあとに、README や LICENSE 付きでリモートを新規作成してしまったことが原因の可能性が高いです。

## 解決手順

リモートとローカルが本当に同じプロジェクトの一部で、統合してよいと確認できた場合の手順です。方法は2つあります。

### 方法1: --allow-unrelated-histories でマージする

```bash
git pull --no-rebase origin main --allow-unrelated-histories --no-edit
```

`--allow-unrelated-histories` が安全装置を外すオプションで、`--no-edit` はマージコミットのメッセージ編集を省略します。今回の出力は次のとおりです。

```text
From ../bare
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 LICENSE | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 LICENSE
```

同じ名前のファイルが両側にある場合はコンフリクトが起きます。その場合は通常のマージと同じように解決して `git commit` します。

### 方法2: rebase でローカルのコミットを載せ替える

履歴をマージコミットなしの一直線にしたい場合は rebase が使えます。こちらは `--allow-unrelated-histories` が不要でした。

```bash
git pull --rebase origin main
```

```text
Rebasing (1/1)Successfully rebased and updated refs/heads/main.
```

ローカルの `first commit` がリモートの `Initial commit` の上に載り、履歴が一直線になります。コミットのハッシュは変わる点に注意してください。まだ push していないローカルのコミットだけを載せ替える使い方なら問題ありません。

## 動作確認

方法1を実行したあとの履歴です。

```bash
git log --oneline --graph
```

```text
*   2643bed Merge branch 'main' of ../bare
|\  
| * ec06513 Initial commit
* c397f9e first commit
```

2本の線が1つのマージコミットで合流しています。`ls` で `LICENSE` と `README.md` の両方が手元にあることも確認できました。あとは通常どおり `git push -u origin main` で反映できます。方法2の場合は、`git log --oneline --graph` で線が1本になっていれば成功です。

## まとめ

- `refusing to merge unrelated histories` は、2つのブランチに共通祖先がないときに出る安全装置のエラーです。
- 統合してよいと確認できたら、`--allow-unrelated-histories` を付けてマージするか、`git pull --rebase` で載せ替えます。
- 再発を防ぐには、リモートを先に作って `git clone` するか、リモートを空（README・LICENSE なし）で作ってから `git remote add` します。

同じ種類の問題として、`git push` が rejected になる場合や、`git pull` でコンフリクトが起きる場合も、まず `git log --oneline --graph --all` で履歴の形を確認すると原因を切り分けやすくなります。どのリポジトリとつないでいるのかは `git remote -v` で必ず確認してから、無関係な履歴を統合してください。別のプロジェクトのリモートを指しているのに `--allow-unrelated-histories` を付けてしまうと、関係のないファイルが大量に混ざってしまいます。

## 関連記事

- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git rebaseの基本と使い方](/posts/git-rebase-basics)
