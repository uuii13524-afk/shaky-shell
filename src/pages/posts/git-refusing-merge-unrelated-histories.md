---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順【Git 2.43】'
date: '2026-09-29'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullで「fatal: refusing to merge unrelated histories」と表示されて止まる症状を解説。ローカルとリモートで最初のコミットが別物になる原因と、rebaseまたは--allow-unrelated-historiesで安全に統合してpushするまでの手順を紹介します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（または「症状」）

手元で作り始めたプロジェクトを、あとから空のリモートリポジトリに上げようとしました。ところが、リモート側にはすでにREADMEだけのコミットが入っていました。リポジトリ作成時に「READMEを追加する」を選んでいたのが原因です。

まず `git push` を試すと、次のように拒否されました。

```bash
git push -u origin main
```

```text
To ../remote.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '../remote.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

ヒントに従って `git pull` すると、今度は次のエラーで止まります。

```bash
git pull --no-rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

pushもpullもできない状態になり、どちらから手を付ければよいのか分からなくなりました。この記事では、この状況を手元で再現して確認した手順をまとめます。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- ブランチ名: `main`（ローカル・リモートとも）
- リモート: 検証用にローカルへ作ったベアリポジトリ（`../remote.git`）。GitHubでも同じ挙動になります。
- ローカル: `git init` したばかりで、`index.js` を1コミットだけ持つリポジトリ
- リモート: `README.md` を1コミットだけ持つリポジトリ

## 試したこと

### 1. pushし直す

`git push` が「fetch first」で拒否されたので、まず強制pushを疑いました。ただ、リモートのコミットを消してしまうことになるので、この時点では実行しませんでした。リモートにあるのはREADMEだけとはいえ、他人が触っているリポジトリなら取り返しがつきません。

### 2. 素直にpullする

次に `git pull origin main` をそのまま実行しました。ここでは統合方法の指定を求められるだけで、unrelated historiesのエラーにはなりませんでした。

```text
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

`pull.rebase` の設定が未指定のままだと、Git 2.43ではこのメッセージが出ます。そこで `--no-rebase` を付けてmergeを指定したところ、冒頭の `refusing to merge unrelated histories` に行き当たりました。

### 3. 履歴の中身を確認する

エラー名の意味を確かめるため、履歴を見ました。

```bash
git log --oneline --all --graph
```

ローカルの `first local commit` と、リモートの `Initial commit` は、どちらも親を持たないルートコミットです。共通の祖先がありません。

## 原因

`git init` で作ったローカルリポジトリと、リモート側で別途作られたリポジトリは、それぞれ独立した履歴の起点（ルートコミット）を持ちます。両者に共通の祖先コミットがないため、mergeの基準にできる点が存在しません。

Gitは2.9以降、このような「共通祖先のない履歴同士のmerge」をデフォルトで拒否します。誤って無関係なリポジトリをmergeし、履歴を混ぜてしまう事故を防ぐための仕様です。今回のように、意図して両者を統合したい場合は、明示的に許可する必要があると考えられます。

## 解決手順

統合の方法は2通りあります。履歴を一直線にしたいならrebase、統合したことを履歴に残したいならmergeです。どちらもリモートの履歴は書き換えません。

### 方法A: rebaseで一直線にする

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

rebaseでは、ローカルのコミットをリモートの `Initial commit` の上に付け替えます。このためmergeのように共通祖先を求められず、エラーは出ませんでした。履歴は次のとおり一直線になります。

```text
* a023d71 first local commit
* c083ee9 Initial commit
```

コミットのハッシュは付け替えで変わります。まだpushしていないコミットなので問題ありません。

### 方法B: `--allow-unrelated-histories` でmergeする

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--allow-unrelated-histories` で共通祖先のないmergeを許可しています。`--no-edit` はmergeコミットのメッセージ編集画面を省略するオプションです。履歴は次のようにmergeコミットで2本が合流します。

```text
*   f4c77b3 Merge branch 'main' of ../remote
|\  
| * 28dafe8 Initial commit
* 1ddf576 first local commit
```

同じファイルが両側にあると、この段階でコンフリクトが起きます。たとえばリモートにも `.gitignore` があり、ローカルにも別内容の `.gitignore` がある場合です。その場合は通常のコンフリクトと同様に、ファイルを手で直してから `git add` と `git commit` を行います。今回は `README.md` と `index.js` で名前が重ならなかったので、コンフリクトは発生しませんでした。

### 最後にpushする

統合が済んだら、あらためてpushします。

```bash
git push -u origin main
```

```text
To ../remote.git
   c083ee9..a023d71  main -> main
branch 'main' set up to track 'origin/main'.
```

`c083ee9..a023d71` のように範囲が表示されているので、リモートの履歴を上書きせず、続きとして追加できています。

## 動作確認

pushのあと、状態を確認します。

```bash
git status -sb
```

```text
## main...origin/main
```

ローカルの `main` とリモートの `origin/main` が同じ位置にあり、差分もありません。`git log --oneline --graph` で、自分のコミットとリモートのコミットの両方が並んでいることも確認できました。

## ハマったポイント

- エラーの原因はpullの設定ではなく、履歴の起点が別々なことです。`pull.rebase` を設定し直しても、`git pull --no-rebase` のmergeでは同じエラーが出ます。
- `--allow-unrelated-histories` は、本当に統合したいときだけ付けます。別プロジェクトのリポジトリのURLを間違えてpullしたときにも、このオプションを付けると通ってしまい、無関係なファイルがまとめて入ってきます。付ける前に `git remote -v` でURLを確認しておくと安全です。
- 強制push（`git push --force`）でも先に進めますが、リモートの履歴を消します。一人で使う空のリポジトリ以外では避けたほうがよい手段です。
- 今回のログは、ローカルに作った検証用リポジトリで実行した結果です。GitHubのリモートで試す場合、URLの表示などは異なります。

## よくある質問

**Q: `refusing to merge unrelated histories` が出るのはどんなときですか？**
ローカルで `git init` したリポジトリと、GitHubなどで別に作成されたリポジトリをつなげたときが典型です。リモート作成時にREADMEやLICENSEを自動追加した場合に起きやすくなります。

**Q: rebaseとmergeのどちらを選べばよいですか？**
履歴をきれいに一直線にしたいならrebaseです。二つの履歴を統合した事実を残したいならmergeです。どちらを選んでもファイルの内容は同じになります。

**Q: 最初からこのエラーを避けるには？**
GitHubで新規リポジトリを作るとき、READMEなどの初期ファイルを追加せず空のまま作成します。そうすれば、ローカルの履歴をそのままpushできます。もう一つの方法は、先に `git clone` してからその中でファイルを追加していく流れです。

## まとめ

- `refusing to merge unrelated histories` は、ローカルとリモートに共通祖先がないときに出るエラーです。
- `git pull --rebase` か `git pull --allow-unrelated-histories` で統合し、その後に通常どおりpushします。
- 別のリポジトリを誤って指定していないか、`git remote -v` で確認してから許可オプションを使います。

同じように「pullやpushが拒否される」系のエラーは、原因を履歴の形から読み解くと切り分けやすくなります。

## 関連記事

- [git pushが rejected されたときの直し方](/posts/git-push-rejected-fix)
- [git pullでコンフリクトが起きたときの対処法](/posts/git-pull-merge-conflict)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [git remoteの基本操作](/posts/git-remote-operations)
- [GitHubへの初めてのpush手順](/posts/github-first-push)
