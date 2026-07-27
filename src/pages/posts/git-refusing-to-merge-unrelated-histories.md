---
title: 'git pull で fatal: refusing to merge unrelated histories が出た時の対処法'
date: '2026-07-27'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pull や git merge で fatal: refusing to merge unrelated histories が出る原因と直し方を解説。GitHubで先にREADMEを作成してからローカルでgit initした場合など、よくある発生パターンも紹介します。'
en_tags: ['Git', 'GitHub', 'fatal', 'unrelated histories', 'merge']
---

## やりたかったこと（または「症状」）

新しいプロジェクトをローカルで `git init` して数コミット積んだ後、GitHub側に対応するリポジトリを作成した。GitHub上では「READMEファイルを追加する」にチェックを入れて作成していたため、リモート側にも1コミットある状態だった。ローカルにリモートを追加し、`git pull` で取り込もうとしたところ、見慣れないエラーで止まった。

```text
$ git remote add origin git@github.com:example/myproject.git
$ git pull origin main
warning: no common commits
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 799 bytes | 799.00 KiB/s, done.
From github.com:example/myproject
 * branch            main       -> FETCH_HEAD
 * [new branch]      main       -> origin/main
fatal: refusing to merge unrelated histories
```

`git push` ではなく `git pull` の段階で弾かれており、ローカルのコミットもリモートのコミットも消えていないのに、マージだけができない状態だった。

## 環境

- OS: Ubuntu 24.04 LTS
- Git: 2.43.0（apt経由でインストール）
- ターミナル: GNOME Terminal
- リポジトリの作り方: ローカルで `git init` → GitHub側で「Add a README file」にチェックして新規リポジトリ作成 → 後からリモート追加

## 試したこと

まず単純に再実行すれば直るかと思い、もう一度 `git pull origin main` を叩いたが、結果は同じだった。

```bash
git pull origin main
```

```text
fatal: refusing to merge unrelated histories
```

次に `git log` でローカルとリモートのコミットを見比べてみた。

```bash
git log --oneline
git log --oneline origin/main
```

```text
$ git log --oneline
a1b2c3d Initial commit (local scaffold)
$ git log --oneline origin/main
9f8e7d6 Initial commit (README from GitHub)
```

2つのログの先頭コミットが完全に別物で、共通の祖先コミットが1つも存在しないことが分かった。これが `unrelated histories` という言葉の意味だと理解した。

## 原因

Gitは通常、マージしようとしている2つのブランチが同じ初期コミットから枝分かれしていることを前提にしている。しかし今回のように「ローカルで `git init` して独自にコミットを作る」のと「GitHub側でREADME付きのリポジトリを新規作成する」を両方行うと、それぞれのブランチが完全に別の初期コミットから始まってしまい、共通の祖先が存在しない2本の履歴になる。

Git 2.9以降、`git merge`（および内部的にマージを呼び出す `git pull`）はこの「共通祖先のない履歴」を安全のためデフォルトで拒否するようになっており、それが `fatal: refusing to merge unrelated histories` というエラーになって表れる。意図せず全く無関係な2つのプロジェクトを1つのリポジトリにマージしてしまう事故を防ぐための挙動であり、バグではない。

## 解決方法

### 1. 履歴が本当に無関係で問題ないか確認する

先に `git log --oneline` と `git log --oneline origin/main` を見比べ、単純に「ローカルとリモートを両方初期化してしまっただけ」であることを確認する。もし片方に消したくない大量のコミットがある場合は、マージ前にバックアップブランチを切っておくと安全。

```bash
git branch backup-local
```

### 2. `--allow-unrelated-histories` を付けて再度pullする

無関係な履歴同士でも意図的にマージしたい場合は、明示的にオプションを付ける。

```bash
git pull origin main --allow-unrelated-histories
```

```text
Merge made by the 'ort' strategy.
 README.md | 3 +++
 1 file changed, 3 insertions(+)
 create mode 100644 README.md
```

ローカルの初期コミットとGitHub側のREADMEコミットの両方が1つの履歴に統合され、以降は通常通り `git push` できるようになった。

### 3. コンフリクトが出た場合は通常のマージと同じ手順で解決する

ファイルが重複していた場合（例えば両方に `README.md` がある場合）は、通常のマージコンフリクトと同じ手順で解決すればよい。

```bash
git status
```

```text
both added:      README.md
```

```bash
# README.md の中身を確認し、必要な部分を残して編集
git add README.md
git commit
```

### 4. そもそもこの状況を避けたい場合

次回以降は、GitHubでリポジトリを新規作成する際に「Add a README file」のチェックを外し、空のリポジトリとして作成してからローカルの `git init` プロジェクトを push する順序にすれば、最初から共通の祖先を持つ1本の履歴になり、このエラー自体が発生しない。

```bash
git remote add origin git@github.com:example/myproject.git
git push -u origin main
```

## ハマったポイント

- `--allow-unrelated-histories` という名前を知らないと、エラーメッセージだけを見て「リモートの設定が間違っているのでは」と勘違いしやすい。実際にはリモートのURLもブランチ名も正しく、履歴の系譜だけが問題だった
- 焦って `git pull` を何度も再実行しても、オプションを付けない限り同じエラーが繰り返されるだけだった
- `--allow-unrelated-histories` でマージした後、GitHub側のREADMEとローカルにも別途README.mdを作っていたため、内容が重複してマージコンフリクトになった。無関係履歴のマージ自体は成功しても、ファイルの中身がぶつかるケースがある点に注意が必要だった

## よくある質問

**Q: `--allow-unrelated-histories` を付けるのは危険ではないですか？**
本当に無関係な2つの別プロジェクトを誤ってマージしようとしている場合は危険です。まず `git log` でお互いの履歴を確認し、「単にローカルとリモートを両方初期化してしまっただけ」と分かった上でオプションを付けるようにしてください。

**Q: `git pull` ではなく `git fetch` + `git merge` でも同じですか？**
はい、内部的には同じマージ処理が走るため、`git merge origin/main --allow-unrelated-histories` のようにオプションを付ける必要があるのも同様です。

**Q: 今後同じ事故を防ぐには？**
GitHubで新規リポジトリを作る際は「Add a README file」やライセンス・.gitignoreの自動生成にチェックを入れず、空のリポジトリとして作成し、ローカル側から最初のpushを行う運用にすると、この問題自体が発生しなくなります。

## 関連記事

- [GitHubに初めてpushする手順](/posts/github-first-push)
- [git pullでマージコンフリクトが起きた時の対処法](/posts/git-pull-merge-conflict)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
