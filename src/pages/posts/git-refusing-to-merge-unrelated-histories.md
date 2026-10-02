---
title: 'git pullで「fatal: refusing to merge unrelated histories」の原因と解決手順【Git 2.43】'
date: '2026-10-02'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullで「fatal: refusing to merge unrelated histories」が出て止まる症状を、再現環境で検証して解説。ローカルとリモートで共通の祖先コミットがない原因と、--allow-unrelated-historiesでの解決手順、使ってはいけない場面まで紹介します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（または「症状」）

手元で`git init`して作り始めたプロジェクトを、あとから用意したリモートリポジトリ（README付きで作成したもの）につなぎ、まずリモート側の内容を取り込もうとして`git pull`を実行した。リモートを先にREADME付きで作ってしまい、ローカルはローカルで別々にコミットを積んでいた、という典型的なパターンである。

```bash
git pull --no-rebase origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

マージコンフリクトのようにファイルの衝突箇所が示されるわけでもなく、`unrelated histories`（無関係な履歴）という聞き慣れない言葉だけで止まってしまう。

なお、この記事の出力は、私がサンドボックス上に実際にリモート用の空リポジトリとローカルリポジトリを作って再現したものを、そのまま貼っている。本番リポジトリで起きた事故ログではない点は先に断っておく。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- ローカル: `git init -b main`で作成。`app.py`を1ファイルだけコミット済み
- リモート: 別のリポジトリで`README.md`を1ファイルだけコミットし、bareリポジトリに`push`したもの
- ブランチ名: ローカル・リモートとも`main`

## 試したこと

### 1. そのまま`git pull`する

最初は何も考えずに`git pull origin main`を実行した。この場合、Git 2.33以降で`pull.rebase`が未設定だと、`unrelated histories`のエラーより前に別のメッセージで止まる。

```bash
git pull origin main
```

```text
From ../origin
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
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

これは「統合の方法を決めてください」という別の話なので、ここでは`--no-rebase`（マージ）を明示して再実行した。それが冒頭の`fatal: refusing to merge unrelated histories`である。

### 2. `git fetch`だけは通ることを確認する

取得自体は成功するのか確認した。`git fetch origin`はエラーなく終わり、`origin/main`は手元に取り込まれていた。つまり通信や認証の問題ではなく、取り込んだ後の「統合」だけが拒否されている。

### 3. 履歴をグラフで見る

```bash
git log --oneline --all --graph
```

```text
* dbdc507 Add app.py
* 10b54b6 Initial commit on remote
```

2本の線がつながっておらず、縦に並んで見えるだけで合流点がない。続けて共通の祖先を探した。

```bash
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

何も出力されず終了コードが1だった。`git merge-base`は共通の祖先コミットを返すコマンドなので、「共通の祖先が存在しない」ことがここで確定した。

### 4. `git pull --rebase`も試した

ついでに`--rebase`も試した。この条件では、リベースは問題なく成功した。

```bash
git pull --rebase origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
Rebasing (1/1)
Successfully rebased and updated refs/heads/main.
```

結果は、リモートの`Initial commit on remote`の上にローカルの`Add app.py`が1本の線で載る形になった。共通の祖先がなくても、リベースは「自分のコミットを相手の先端に付け替える」操作なので成立する。履歴を一直線にしたいだけならこの選択肢もある。ただし、ローカルの履歴が長い場合は全コミットのハッシュが書き換わる点に注意が必要である。

## 原因

`git pull`（merge）は、2つのブランチの共通の祖先を起点に3-wayマージを行う。ローカルとリモートが別々の`git init`から始まっていると、どのコミットをたどっても共通の祖先に行き着かない。`git merge-base`が何も返さなかったのはそのためである。

Gitはバージョン2.9以降、この状態でのマージをデフォルトで拒否する。理由は、無関係なプロジェクトの履歴を気づかないまま合体させる事故を防ぐためだと説明されている。つまりGitの故障ではなく、安全装置が正しく働いている状態である。

## 解決手順

2つの履歴を意図して統合したいと確認できた場合のみ、次のオプションを付ける。

### 1. 取り込む内容を事前に確認する

```bash
git fetch origin
git log --oneline origin/main
```

リモートに何が入っているかを見て、本当に自分のプロジェクトと合体させてよいかを判断する。ここを飛ばすと、別プロジェクトのファイルが混ざる恐れがある。

### 2. `--allow-unrelated-histories`を付けてマージする

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

```text
From ../origin
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit`はマージコミットのメッセージ編集画面を開かないための指定で、ここでは自動メッセージのまま進めている。

同じファイル名（たとえば両方に`README.md`がある）で内容が違う場合は、通常のコンフリクトとして止まる。その場合は[git pullでマージコンフリクトが起きた時の対処法](/posts/git-pull-merge-conflict)と同じ手順で解消する。

### 3. 結果を確認してからpushする

```bash
git log --oneline --graph
git push origin main
```

## 動作確認

マージ後の履歴は次のようになった。

```text
*   95596db Merge branch 'main' of ../origin
|\
| * 10b54b6 Initial commit on remote
* dbdc507 Add app.py
```

2本の線がマージコミットで合流した。ファイルも両方そろっている。

```bash
ls
```

```text
README.md
app.py
```

共通の祖先も、これで見つかるようになった。

```bash
git merge-base main origin/main
```

```text
10b54b6c530467ce81f2441e60f0c2e1d2467358
```

この状態になれば、以降の`git pull`と`git push`は通常どおり通る。

## ハマったポイント

- 最初に出るのは`unrelated histories`ではなく、`pull.rebase`未設定時の`divergent branches`のメッセージだった。Git 2.43で確認した範囲では、こちらを先に解決しないと目的のエラーにたどり着かない
- `--allow-unrelated-histories`は「エラーを黙らせるオプション」ではなく、「履歴を新規に合体させる」宣言である。リモートが別プロジェクトだと分かっているのに付けると、ファイルが混ざった履歴が`push`されてしまう
- そもそもの予防は、リモートを先に作るなら`git clone`から始める、ローカルを先に作るなら**READMEなしの空リポジトリ**をリモートに作る、のどちらかに揃えること。初回pushの手順は[GitHubへ初めてpushする手順](/posts/github-first-push)にまとめてある

## まとめ

- `refusing to merge unrelated histories`は、ローカルとリモートに共通の祖先コミットがない時に出る安全装置で、`git merge-base`が何も返さなければ該当する
- 内容を確認して合体させてよいと判断した場合のみ、`--allow-unrelated-histories`を付けてpullする。履歴を一直線にしたいなら`git pull --rebase`も選べる
- 同じ型のエラーは、リモートを付け替えた直後や、`git init`し直したリポジトリをつなぎ直した時にも出る。まず`git log --oneline --all --graph`で履歴がつながっているかを見る習慣をつけておくとよい

## よくある質問

**Q: `--allow-unrelated-histories`を付けるとデータが消えますか？**
消えない。2つの履歴を残したままマージコミットで合流させるだけである。ただし同名ファイルがあれば、通常どおりコンフリクトの解消が必要になる。

**Q: ローカルの履歴を捨ててリモートに合わせたい場合は？**
ローカルに大事なコミットがないと確認できた場合に限り、`git reset --hard origin/main`で揃えられる。ローカルの変更は失われるので、実行前に`git log`で内容を確認すること。

**Q: `git push`が拒否される場合も同じ原因ですか？**
別の問題で、`non-fast-forward`が原因のことが多い。[git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)を参照。

## 関連記事

- [git pullでマージコンフリクトが起きた時の対処法](/posts/git-pull-merge-conflict)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [GitHubへ初めてpushする手順](/posts/github-first-push)
- [git remoteの操作まとめ](/posts/git-remote-operations)
- [fatal: not a git repositoryエラーの対処法](/posts/git-fatal-not-a-git-repository)
