---
title: 'git pullで"refusing to merge unrelated histories"が出た時の原因と解決手順'
date: '2026-08-09'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubでREADME付きのリポジトリを作った直後にgit pullすると発生するfatal: refusing to merge unrelated historiesの原因と、履歴を安全に統合する解決手順を解説します。'
ja_tags: ['Git', 'GitHub', 'unrelated histories', 'git pull', 'マージ']
en_tags: ['Git', 'GitHub', 'unrelated histories', 'git pull', 'merge']
---

## やりたかったこと（症状）

ローカルで`git init`してから`README.md`なしでコミットを積んでいた既存プロジェクトを、後からGitHub上で「README・.gitignore・LICENSE付き」で新規作成したリモートリポジトリに接続しようとした。`git remote add origin`でリモートを登録し、いつも通り`git pull origin main`を叩いたところ、まず以下のヒントが表示されて止まった。

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

`pull.rebase`の設定がないという指摘だと理解し、`git config pull.rebase false`でマージ方式に固定してから再度`git pull`を実行した。ところが今度は別のエラーで完全に弾かれた。

```text
fatal: refusing to merge unrelated histories
```

`git config`の指示通りに設定したのに、なぜまだpullできないのか最初は理解できなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- リモート: GitHub（Webの「Create repository」画面でREADME・.gitignoreを追加して作成）
- ローカル: `git init`済みで、リモートとは無関係にコミットを1つ以上積んでいた既存プロジェクト

## 試したこと

最初に疑ったのは`pull.rebase`の設定不足だった。上記のヒント通り`git config pull.rebase false`を実行してから`git pull origin main`をやり直したが、`fatal: refusing to merge unrelated histories`で再び止まった。この時点で「rebaseかmergeかの選択」と「unrelated histories」は別問題だと気づいた。

次に、リモートのURLを間違えているのではないかと疑い、`git remote -v`で登録内容を確認した。

```bash
git remote -v
```

```text
origin  /tmp/.../repoA (fetch)
origin  /tmp/.../repoA (push)
```

URLは正しく、リモート自体は問題なくfetchできていた。実際`git fetch origin`は正常に完了し、`FETCH_HEAD`にリモートのブランチも取得できていた。つまり通信やリモート設定の問題ではなく、pull（=fetch＋merge）の「merge」の段階だけが拒否されていることになる。

ここで、ローカルのコミット履歴とリモートのコミット履歴を`git log`で見比べた。

```bash
git log --oneline
```

ローカル側は`local: initial scaffold`から始まる履歴、リモート側（`git fetch`後の`origin/main`）は`Initial commit from GitHub web UI`から始まる履歴で、共通の祖先コミットが1つも存在しないことが分かった。GitHub上でリポジトリを作る際にREADMEを追加すると、ローカルの`git init`とは完全に無関係な最初のコミットがリモート側に作られる。この2つの履歴には共有ルートがないため「unrelated histories」と判定されていた。

## 原因

Gitはデフォルトで、共通の祖先コミットを持たない2つの履歴同士のマージを安全側に倒して拒否する。これは意図しない無関係なリポジトリ同士を誤ってマージしてしまう事故を防ぐための仕様で、Git 2.9以降で導入された挙動になる。

今回のケースでは、ローカルで先に`git init`して作業を始めたプロジェクトと、GitHub側で「README付きで新規作成」したリポジトリが、それぞれ別々のルートコミットを持っていた。`git config pull.rebase false`を設定しても、これは「fast-forwardできない場合にmerge方式を使う」という設定にすぎず、「共通の祖先がない履歴同士を強制的につなげてよいか」という別の確認をスキップするものではない。そのため`pull.rebase`の設定だけでは解決せず、明示的に許可するオプションが必要になる。

## 解決手順

### 1. 履歴が本当に無関係かをfetchで確認する

いきなりマージする前に、まず`fetch`だけ行いリモートの履歴を確認する。

```bash
git fetch origin
git log --oneline --graph --all
```

ローカルとリモート（`origin/main`）の履歴に共通のコミットが1つもなく、ツリーが完全に分岐している（グラフが1点で交わっていない）ことを確認した。

### 2. --allow-unrelated-historiesを付けてpullする

無関係な履歴同士のマージを許可した上で、あらためて`git pull`を実行する。

```bash
git pull origin main --allow-unrelated-histories
```

```text
From /tmp/.../repoA
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`Merge made by the 'ort' strategy.`と表示され、今度はマージが成功した。GitHub側で追加されていた`README.md`が、ローカルの既存ファイルと衝突することなくマージコミットとして取り込まれた。

### 3. マージコミットができたことを確認する

```bash
git log --oneline --graph --all
```

```text
*   bd1bbdd Merge branch 'main' of /tmp/.../repoA
|\
| * 4adee1c Initial commit from GitHub web UI
* 2e85e09 local: initial scaffold
```

ローカルの初期コミットとGitHub側の初期コミットが、それぞれ別の祖先を持ったまま1つのマージコミットに合流していることが分かる。ファイルが衝突した場合はここで通常のコンフリクト解消（該当ファイルを編集して`git add`→`git commit`）が必要になるが、今回はファイルが重複していなかったため自動でマージが完了した。

## 動作確認

マージ後、作業ディレクトリにローカルとリモート両方のファイルが揃っていることを確認する。

```bash
ls -la
```

```text
README.md
index.js
```

GitHub側の`README.md`と、ローカルで先に作っていた`index.js`の両方が同じディレクトリに存在している。この状態で`git push origin main`すれば、リモートにもマージ後の履歴がそのまま反映される。

## まとめ

- `fatal: refusing to merge unrelated histories`は、共通の祖先コミットを持たない履歴同士をGitが安全のためにマージ拒否しているだけで、リモート設定や通信の問題ではない。
- `git config pull.rebase false/true`は「fast-forwardできない時の統合方式」の設定であり、「無関係な履歴を許可するか」とは別軸の設定なので、これだけでは解決しない。
- `git pull origin <branch> --allow-unrelated-histories`で明示的に許可すれば、無関係な履歴同士でもマージコミットとして統合できる。ファイルが衝突する場合は通常のコンフリクト解消フローに進めばよい。
- 同じ現象は「ローカルで先に作業してからGitHubでREADME付きリポジトリを作った」「別々に管理していた2つのリポジトリを1つに統合したい」といった場面でも起きるため、原因の切り分け方は共通して使える。

## 関連記事

- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git reflogで消えたコミットを復元する方法](/posts/git-reflog)
- [GitのリモートリポジトリをCLIで操作する基本コマンド](/posts/git-remote-operations)
