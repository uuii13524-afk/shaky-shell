---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順'
date: '2026-09-07'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHubで先に作成したリポジトリと、ローカルで別々に育てたリポジトリを結びつけてpullすると「fatal: refusing to merge unrelated histories」が出て失敗する症状を解説。原因の分岐点になったコミットの共通祖先の有無と、--allow-unrelated-historiesを使った安全な解決手順を紹介します。'
ja_tags: ['Git', 'unrelated histories', 'git pull']
en_tags: ['Git', 'unrelated histories', 'git pull']
---

## やりたかったこと（または「症状」）

すでにローカルで作り始めていた`myapp`というプロジェクトを、あとからGitHub上に作成したリモートリポジトリに接続してpushしたかった。GitHub側では「READMEを追加」にチェックを入れてリポジトリを作成済みで、ローカル側にはすでに`src/index.js`を含む初回コミットがあった。

```bash
git remote add origin /path/to/remote-repo
git pull origin main --no-rebase
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git pull`は`fatal`で即座に止まり、リモート側の`README.md`もローカル側の`src/index.js`も統合されなかった。`git status`を確認しても、作業ツリーには変化がなく、ローカルの初回コミットのままだった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- ローカルリポジトリ: `main`ブランチに初回コミット1つ（`src/index.js`を含む）
- リモートリポジトリ: GitHub上で「READMEを追加」して作成した`main`ブランチに初回コミット1つ（`README.md`を含む）
- 両者の間に共通のコミット履歴は存在しない（`git remote add`で後から接続しただけ）

## 試したこと

最初は単に`git pull origin main`を実行すれば、リモートの変更がローカルに取り込まれるはずだと考えていた。

```bash
git pull origin main
```

```text
From /path/to/remote-repo
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

Git 2.43では`pull.rebase`が未設定だとまずこのヒントで止まる。今回はマージで統合したかったので、案内どおり`--no-rebase`を付けて再実行した。

```bash
git pull origin main --no-rebase
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

今度は明確に「unrelated histories（無関係な履歴）」という理由で拒否された。`git log --oneline --all`で両ブランチのコミットを見比べても、共通のコミットは1つもなく、完全に別系統のグラフだと分かった。

## 原因

Gitはデフォルトで、マージしようとしている2つのブランチが**共通の祖先コミットを持たない**場合、それを意図的な統合ではなく「たまたま無関係なリポジトリを混ぜようとしている事故」とみなして`merge`を拒否する。

今回のケースはまさにこのパターンだった。

- ローカル: `4a0ec66 Initial local commit`から始まる履歴
- リモート: `1922d36 Initial commit (created on GitHub)`から始まる履歴

どちらも「最初のコミット」を持つが、片方がもう片方の祖先になっているわけではない。GitHub上でリポジトリ作成時に「READMEを追加」を選ぶと、ローカルの初回コミットとは無関係な初回コミットがリモート側に生成されるため、あとから`git remote add`で結びつけると必ずこの状態になる。これはGitのバグではなく、意図しない履歴の混在を防ぐための安全側のガードだった。

## 解決方法

### 1. 本当に無関係な履歴を統合してよいか確認する

両方のリポジトリの内容を`git log --oneline --all`や実際のファイル内容で見比べ、「別プロジェクトを間違って混ぜようとしていないか」を確認する。今回は「GitHub側のREADMEだけを取り込み、ローカルの実装はそのまま残したい」という意図が明確だったため、次に進んだ。

### 2. `--allow-unrelated-histories`を付けて再実行する

```bash
git pull origin main --no-rebase --allow-unrelated-histories
```

```text
From /path/to/remote-repo
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

今回はファイルパスが競合しなかったため、コンフリクトなしでマージコミットが自動生成された。

### 3. ファイルパスが競合する場合はコンフリクトを解消する

同名ファイルが両方に存在する場合は通常のマージコンフリクトと同様に表示されるので、該当ファイルを開いて手動で解消し、`git add`してから`git commit`する。

```bash
git status
git add <competing-file>
git commit
```

## 動作確認

```bash
git log --oneline --graph --all
```

```text
*   db77580 Merge branch 'main' of /path/to/remote-repo
|\  
| * 1922d36 Initial commit (created on GitHub)
* 4a0ec66 Initial local commit
```

`git status`も`nothing to commit, working tree clean`になり、`ls`でリモート側の`README.md`とローカル側の`src/index.js`が両方とも作業ツリーに存在することを確認できた。

## ハマったポイント

- `git pull`を素朴に実行しただけでは、まず`pull.rebase`未設定に関するヒントで止まり、`--allow-unrelated-histories`の話にすらたどり着かない。エラーメッセージを最後まで読まずに`--allow-unrelated-histories`だけをネットで調べて足しても、`--no-rebase`（または`pull.rebase false`の設定）を併用しないと同じ場所で止まり続けた。
- `--allow-unrelated-histories`は「無関係な履歴でも強制的に統合してよい」という指示であり、内容の衝突を自動で解決してくれるわけではない。同名ファイルがあれば普通にコンフリクトになるため、事前に両リポジトリの中身を見比べる一手間を省くべきではなかった。
- GitHubでリポジトリ作成時に「READMEを追加」にチェックを入れると、ローカルとは無関係な初回コミットが生まれる。ローカルにすでに実装がある状態でリポジトリを作るときは、チェックを外して空のリポジトリとして作成しておけば、そもそもこの問題自体を回避できた。

## よくある質問

**Q: `--allow-unrelated-histories`を付けるのは安全ですか？**
統合しようとしている2つの履歴が「本当に同じプロジェクトの一部」であることを確認できているなら安全。逆に、無関係な別プロジェクトを誤って混ぜようとしている場合にこのオプションで無理やり通すと、意図しないファイルが混在するリポジトリになってしまう。

**Q: `pull.rebase`のヒントと`unrelated histories`のエラーはどちらが先に出ますか？**
Git 2.9以降、`pull.rebase`が未設定の状態で`git pull`を実行すると、まず「divergent branches」のヒントで止まる。`--no-rebase`や`--rebase`など統合方法を明示して初めて、その先で共通祖先の有無がチェックされ`unrelated histories`のエラーに到達する。

**Q: この問題を根本的に避ける方法はありますか？**
GitHubなどでリモートリポジトリを作成する際、ローカルにすでにコミットがある場合は「READMEやライセンスを追加」のオプションを外して空のリポジトリとして作成し、最初のpushをローカル側から行うようにすれば、無関係な履歴が生まれること自体を避けられる。

## 関連記事

- [git pushがrejectedになる原因と解決方法](/posts/git-push-rejected-fix)
- [fatal: not a git repositoryの原因と解決方法](/posts/git-fatal-not-a-git-repository)
- [gitのリモート操作（remote add/remove/rename）まとめ](/posts/git-remote-operations)
- [git pull時のマージコンフリクトを解決する手順](/posts/git-pull-merge-conflict)
- [gitブランチの基本操作まとめ](/posts/git-branch-basics)
