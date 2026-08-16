---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順'
date: '2026-08-16'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubで新規作成したリポジトリにローカルの既存プロジェクトからgit pullすると、fatal: refusing to merge unrelated historiesで止まる症状を解説します。原因を切り分け、履歴を安全に統合する手順を紹介します。'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## やりたかったこと（または「症状」）

すでに`git init`してコミットも何度か積んであるローカルのプロジェクトを、GitHub上に「READMEにチェックを入れて」新規作成したリモートリポジトリと紐付けようとした。`git remote add origin`でリモートを登録し、既存のREADMEを取り込むつもりで`git pull origin main`を実行したところ、ファイルは一切取り込まれず、以下のように止まった。

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

指示通り`git config pull.rebase false`を設定してから再度`git pull origin main`を実行すると、今度は別のエラーに変わった。

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git log`で確認しても、ローカル側にはリモートのコミットはまだ1つも存在しておらず、「pullしただけなのに、なぜ拒否されるのか」が最初は分からなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS
- Git: 2.43.0
- ローカル側: `git init`済み、`package.json`をコミット済みの独立リポジトリ
- リモート側: GitHubで「Add a README file」にチェックを入れて新規作成したリポジトリ（`README.md`と`.gitignore`のみをコミット済み）

## 試したこと

最初は`pull.rebase`の設定が足りないだけだと思い、`git config pull.rebase false`（マージ方式）を明示的に設定した。

```bash
git config pull.rebase false
git pull origin main
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

エラーメッセージは変わったが、依然として取り込みは拒否された。次に、リモート側のコミットだけを確認しようと`git fetch origin`を実行してみたところ、こちらはエラーなく完了し、`origin/main`としてリモートのコミットがローカルに認識されていることが分かった。

```bash
git fetch origin
git log --oneline --graph --all
```

```text
* 989fccd (origin/main) Initial commit on GitHub
* ea52b33 (HEAD -> main) Initial local commit
```

2つのコミットに親子関係がなく、枝分かれではなく完全に独立した2本の履歴として存在していることがグラフから読み取れた。ここでようやく、単純な設定不足ではなく「そもそも共通の祖先コミットを持たない2つのリポジトリを1つにマージしようとしている」ことが原因だと理解できた。

## 原因

`git pull`は内部的に`git fetch` + `git merge`（または`rebase`）を実行する。通常の`merge`は、2つのブランチの共通の祖先コミットを起点に差分を計算して統合する。しかし今回のケースでは、ローカルのリポジトリもリモートのリポジトリも、それぞれ`git init`（またはGitHub上の初回コミット）から始まった独立した履歴であり、共通の祖先コミットが存在しない。Gitはこの状態を「無関係な履歴（unrelated histories）」と判断し、意図しない誤マージを防ぐために標準では拒否する。CI環境などでは共通祖先がないマージを許可すると事故につながりやすいため、Git 2.9以降はこの挙動がデフォルトで有効になっている。

## 解決方法

### 1. 無関係な履歴を明示的に許可してマージする

原因が「共通祖先がないこと」だと分かれば、対処は単純で、Gitに「それを承知の上でマージしてよい」と明示的に伝えるだけでよい。

```bash
git pull origin main --allow-unrelated-histories
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 .gitignore | 1 +
 README.md  | 1 +
 2 files changed, 2 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 README.md
```

今回はファイル名が衝突していなかったため、コンフリクトなくマージコミットが自動生成された。もし両方のリポジトリに同名の`README.md`など内容が異なるファイルがあれば、この時点で通常のマージコンフリクトとして表示されるので、該当ファイルを開いて手動で解消し、`git add`してからマージコミットを完了させる。

### 2. マージ結果を確認する

```bash
git log --oneline --graph --all
```

```text
*   5b1c0b3 Merge branch 'main' of /path/to/remote
|\
| * 989fccd Initial commit on GitHub
* ea52b33 Initial local commit
```

2本の独立した履歴が1つのマージコミットで結合され、ローカルの`package.json`とリモートの`README.md`・`.gitignore`が両方とも作業ツリーに存在していれば成功している。

### 3. push前にリモートの最新状態を確認する

マージが完了したら、通常通り`git push origin main`でリモートに反映する。マージコミットにはローカル・リモート双方の履歴が含まれているため、`push`自体は特別な操作を必要としない。

```bash
git push origin main
```

## ハマったポイント

- 最初のエラー（`Need to specify how to reconcile divergent branches`）だけを見て`pull.rebase`の設定不足だと判断し、実際の原因である「共通祖先の不在」に気づくまで少し時間がかかった。エラーメッセージは2段階に分かれて出るため、両方読む必要がある
- `--allow-unrelated-histories`は一見危険なオプションに見えるが、実際にはコンフリクトが起きればマージコンフリクトとして通常通り検知されるため、意図せず片方の変更を消してしまうわけではない
- `rebase`方式（`pull.rebase true`）を選んでいた場合は挙動が異なり、こちらは`git rebase --root`など別の対応が必要になる。今回は`merge`方式を前提とした手順であることに注意

## よくある質問

**Q: `--allow-unrelated-histories`を使うと、片方のリポジトリの内容が消えることはありますか？**
基本的にはありません。このオプションは「共通祖先がなくてもマージ計算を試みる」ことを許可するだけで、ファイル単位の差分計算やコンフリクト検出は通常のマージと同様に行われる。同名ファイルの内容が異なる場合は、通常のマージコンフリクトとして検出されるため、内容を確認せずに片方が上書きされることはない。

**Q: 毎回`--allow-unrelated-histories`を付けるのが面倒です。設定で省略できますか？**
このオプションを恒久的にデフォルト化する設定項目は用意されていない。無関係な履歴のマージは通常のワークフローでは頻繁に発生する操作ではなく、意図しない誤マージを防ぐための安全装置として意図的にオプトインが必要な設計になっている。

**Q: GitHub上で新規リポジトリを作る際、最初から「Add a README file」のチェックを外しておけば防げますか？**
防げる。チェックを外して空のリポジトリとして作成し、そこに最初の`git push`を行えば、リモート側に独立したコミットが存在しないため、今回のような「無関係な履歴」の衝突自体が発生しない。すでにREADME付きで作成してしまった後にこのエラーに遭遇した場合は、本記事の手順で解決するのが手早い。

## 関連記事

- [git pushがrejectedになる時の原因と解決方法](/posts/git-push-rejected-fix)
- [git pull時のmerge conflictを解決する方法](/posts/git-pull-merge-conflict)
- [初めてのgit push手順まとめ](/posts/github-first-push)
- [git remoteの追加・変更・削除コマンドまとめ](/posts/git-remote-operations)
- [fatal: not a git repositoryが出た時の対処法](/posts/git-fatal-not-a-git-repository)
