---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順（Git 2.43 / Ubuntu 24.04）'
date: '2026-10-10'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pull origin mainが「fatal: refusing to merge unrelated histories」で止まる症状を、再現環境で検証しました。共通の祖先がない2つの履歴が原因で、--allow-unrelated-historiesまたは--rebaseで取り込む手順を解説します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（症状）

手元で`git init`して数コミット作ったリポジトリに、あとからリモートを追加した。リモート側には、GitHubで新規作成したときに自動生成されたREADMEだけのコミットが入っている。この状態でリモートの内容を取り込もうとして`git pull`を実行したところ、次のエラーで止まった。

```bash
git pull origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

コンフリクトでもネットワークエラーでもなく、マージそのものをGitが拒否している。`git pull`の前に`git fetch`は成功しているので、通信や認証の問題ではない。

なお、この記事のログは本番リポジトリではなく、ローカルに作った検証用のベアリポジトリで実際に再現して取得したものです。自分のリポジトリで起きたときも、同じ手順で原因を切り分けられます。

## 環境

- OS: Ubuntu 24.04.5 LTS
- Git: 2.43.0
- 構成: ローカルリポジトリ（`main`、コミット1つ）と、別に作ったベアリポジトリ（`main`、README.mdだけのコミット1つ）
- `pull.rebase`は`false`（merge方式）に設定

## 試したこと

最初に、`git pull`をそのまま再実行したが、当然同じエラーになる。次にコミット履歴の状態を確認した。

```bash
git log --oneline --all
```

```text
76ddee3 local first commit
94d4adb Initial commit
```

2つのコミットが並んでいるだけで、どちらかがどちらかの親になっているわけではない。そこで、2つのブランチの共通祖先を探した。

```bash
git merge-base main origin/main
echo "rc=$?"
```

```text
rc=1
```

何も出力されず、終了コードは1だった。共通祖先が存在しないということになる。

## 原因

`git merge-base`が何も返さなかったことが決定的な証拠で、ローカルの`main`とリモートの`main`は**共通の祖先コミットを持たない、別々に生まれた履歴**になっている。ローカルで`git init`したときの最初のコミットと、リモート側で別途作られた最初のコミットは、お互いを知らない。

Gitは2.9以降、このように共通祖先のない履歴同士のマージを、デフォルトでは拒否する。別プロジェクトのリポジトリを誤って取り込む事故を防ぐための安全装置で、今回のエラーはその仕様どおりの動作だった。リポジトリが壊れているわけではない。

なお、pullの挙動はGitの設定にも左右される。`pull.rebase`を設定していない状態で、履歴が分岐している場合の`git pull`は、別のエラー`fatal: Need to specify how to reconcile divergent branches.`で先に止まることがある。今回の検証では、手元のリポジトリにまず`pull.rebase false`を指定して、`unrelated histories`のエラーに絞って確認した。

## 解決手順

### 1. 本当に取り込んでよいリモートか確認する

```bash
git remote -v
git log --oneline origin/main
```

リモートのURLが意図したものか、リモートのコミットが想定どおりか（READMEだけの初期コミットなど）を確認する。別プロジェクトのURLを登録していた場合は、取り込まずに`git remote set-url`で直す。

### 2. 履歴を意図的につなぐ場合は`--allow-unrelated-histories`を付ける

```bash
git pull --allow-unrelated-histories --no-edit origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--no-edit`は、マージコミットのメッセージ編集画面を開かないための指定。

### 3. マージコミットを残したくない場合は`--rebase`

別の方法として、履歴を一直線にしたい場合は`--rebase`が使える。別の検証用リポジトリで試したところ、`--allow-unrelated-histories`なしでも次のように成功した。

```bash
git pull --rebase origin main
```

```text
From ../remote
 * branch            main       -> FETCH_HEAD
Successfully rebased and updated refs/heads/main.
```

rebaseはローカルのコミットをリモートの先頭の上に付け替えるだけなので、共通祖先がなくても動く。ただしコミットのハッシュが変わるため、すでにpush済みのコミットがある場合は使わないほうがよい。

## 動作確認

`--allow-unrelated-histories`でマージした後の状態を確認した。

```bash
git log --oneline --graph
git status -sb
```

```text
*   2f2ca02 Merge branch 'main' of ../remote
|\  
| * 94d4adb Initial commit
* 76ddee3 local first commit
## main
```

リモートの`Initial commit`とローカルの`local first commit`が、マージコミット`2f2ca02`でつながった。以降は共通祖先ができたので、通常の`git pull`と`git push`が使える。

## まとめ

- `refusing to merge unrelated histories`は、ローカルとリモートに共通の祖先コミットがないときの安全装置。`git merge-base`が何も返さなければそれが原因
- 意図して統合するなら`git pull --allow-unrelated-histories`、履歴を一直線にしたいなら`git pull --rebase`
- 先にリモートのURLと中身を確認する。別プロジェクトを取り込んでいないかを見るのが最優先
- 今後は、GitHubで空のリポジトリを作る際にREADMEを自動生成しない、または`git clone`から始めると、この状況自体を避けられる

## よくある質問

**Q: `--allow-unrelated-histories`を付けるとファイルが上書きされますか？**
同じパスのファイルが両方にある場合は通常のマージと同様にコンフリクトとして扱われる。今回のようにファイルが重ならなければ、そのまま両方が残る。

**Q: エラーメッセージの`refusing`は壊れているという意味ですか？**
壊れていない。Gitが安全のために意図的に止めているだけで、履歴の事実を確認してからオプションで許可すればよい。

## 関連記事

- [git pushがrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [git pullで起きるマージコンフリクトの解消](/posts/git-pull-merge-conflict)
- [git remoteの基本操作](/posts/git-remote-operations)
- [GitHubへ最初のpushをする手順](/posts/github-first-push)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
