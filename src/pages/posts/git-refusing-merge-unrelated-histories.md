---
title: 'git pullで「fatal: refusing to merge unrelated histories」の原因と解決手順'
date: '2026-10-05'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'ローカルで先にgit initしてコミットした後、リモートのmainをgit pullすると「refusing to merge unrelated histories」で止まる症状を解説。共通の祖先コミットが無い原因の確認方法と、--allow-unrelated-historiesやrebaseでの解決手順を紹介します。'
ja_tags: ['Git', 'git pull', 'unrelated histories']
en_tags: ['Git', 'git pull', 'unrelated histories']
---

## やりたかったこと（または「症状」）

手元で先に`git init`してコミットを作っていたプロジェクトを、別途作成済みのリモートリポジトリ（LICENSEファイルだけが入った`main`ブランチ）につなぎ、pullして内容を揃えようとした。GitHubで「Add a LICENSE」付きでリポジトリを作ったあとに、ローカルで作業を始めていた状況と同じである。

```bash
git pull origin main
```

最初はマージ方法を指定していなかったため、次のヒントが出て止まった。

```text
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
fatal: Need to specify how to reconcile divergent branches.
```

そこで`--no-rebase`を付けて通常のマージとして実行し直すと、今度は本題のエラーになった。

```bash
git pull --no-rebase origin main
```

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

履歴が分岐していること自体は想定していたが、「無関係な履歴」と言われる理由がすぐには分からなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- 構成: ローカルリポジトリ（`main`に「local first」コミットが1つ）とベアのリモートリポジトリ（`main`に「license」コミットが1つ）
- 再現方法: 検証用のディレクトリ内に、ベアリポジトリとローカルリポジトリを別々に作成して再現した。実運用のリポジトリでは試していない

## 試したこと

最初に疑ったのは、リモート名やブランチ名の指定ミスだった。`git remote -v`でURLを確認し、`git branch -a`でブランチ名が`main`であることも確認したが、どちらも正しかった。

次に`git fetch`だけを実行してみた。取得自体は成功し、`origin/main`が作られる。つまり通信や認証の問題ではなく、取得した履歴をマージする段階で拒否されていると分かった。

```bash
git fetch origin
git log --oneline origin/main
```

```text
2bf58e3 license
```

ローカル側のログは次のとおり。

```bash
git log --oneline
```

```text
2424710 local first
```

どちらも1コミットずつで、お互いのコミットを含んでいない。ここで「共通の祖先が無い」ことを疑い、`git merge-base`で確かめた。

```bash
git merge-base HEAD origin/main
echo "rc=$?"
```

```text
rc=1
```

出力は空で、終了コードは1だった。共通の祖先コミットが存在しないということである。さらに、それぞれの履歴の最初のコミット（親を持たないコミット）を並べて確かめた。

```bash
git rev-list --max-parents=0 HEAD origin/main
```

```text
2424710fe4cde8737592c4f44c4c8bc08096480e
2bf58e398abe768a44485b7af3d2fa203abf998d
```

親を持たないルートコミットが2つ出た。通常は1つのリポジトリから派生した履歴なら、ルートコミットは同じ1つになる。ここが2つあるのは、別々に`git init`された2つの履歴が存在するという意味である。

## 原因

原因は、ローカルとリモートが「それぞれ独立してルートコミットを作った別々の履歴」だったことである。ローカルは`git init`後の最初のコミットが、リモートはLICENSE付きで作成した際の最初のコミットが、それぞれルートになっている。

Gitはマージの際、2つのブランチの共通の祖先（merge base）から3-wayマージを行う。共通の祖先が無い場合、どこを基準に差分を取るべきか決まらない。Git 2.9以降は、こうした場合にデフォルトでマージを拒否し、`refusing to merge unrelated histories`を出す。誤って無関係なプロジェクト同士を混ぜてしまう事故を防ぐための仕様である。

今回のように意図して2つの履歴を1つにしたいのであれば、拒否を解除する明示的な操作が必要になる。

## 解決方法

履歴を1つにまとめる方法は主に2つある。今回は両方を検証用リポジトリで実行した。

### 方法1: --allow-unrelated-historiesでマージする

```bash
git pull --no-rebase --allow-unrelated-histories --no-edit origin main
```

`--allow-unrelated-histories`で拒否を解除し、`--no-edit`でマージコミットのメッセージ編集画面を省略した。

```text
From /path/to/remote
 * branch            main       -> FETCH_HEAD
Merge made by the 'ort' strategy.
 LICENSE | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 LICENSE
```

両方に同名のファイルがある場合はコンフリクトになる。今回はREADME.mdとLICENSEで重複しなかったため、そのままマージできた。

### 方法2: リモートの上にローカルのコミットをrebaseする

マージコミットを作りたくない場合は、先にfetchしてからrebaseする。なお、この検証では方法1の前の状態に戻したうえで実行した（`git reset --hard`で「local first」だけの状態へ戻した）。

```bash
git fetch origin
git rebase origin/main
```

```text
Successfully rebased and updated refs/heads/main.
```

`rebase`は共通の祖先が無い場合でも、ローカルのコミットを`origin/main`の先頭に載せ替える。結果は一直線の履歴になる。

## 動作確認

方法1の後のログは次のようになった。

```bash
git log --oneline --graph
```

```text
*   059c014 Merge branch 'main' of /path/to/remote
|\  
| * 2bf58e3 license
* 2424710 local first
```

2つの履歴が1つのマージコミットで結ばれている。方法2の場合は次のとおりで、一本の履歴になる。

```text
* 2116477 local first
* 2bf58e3 license
```

どちらも`ls`でREADME.mdとLICENSEの両方が存在することを確認できた。

## ハマったポイント

- 最初の`git pull`は、`pull.rebase`が未設定だと「divergent branches」のヒントで止まる。この時点では本題のエラーはまだ出ていない。`--no-rebase`または`--rebase`を付けて初めて`unrelated histories`が出る。
- 共通の祖先が無い状態のrebaseは、`--allow-unrelated-histories`の指定が要らない。マージとrebaseで挙動が違う点が分かりにくい。
- すでにリモートに他人のコミットがある場合、rebaseは自分のコミットのハッシュを書き換える。pushするときに困らないよう、共有ブランチで行う場合は事前にチームへ共有する。

## まとめ

- `refusing to merge unrelated histories`は「共通の祖先コミットが無い」というGitの安全装置で、`git merge-base HEAD origin/main`が空を返し終了コード1になれば原因はこれである。
- `git rev-list --max-parents=0 HEAD origin/main`でルートコミットが2つ出ていれば、別々に`git init`された履歴だと断定できる。
- 意図して統合するなら`git pull --allow-unrelated-histories`でマージ、または`git rebase origin/main`で一本化する。意図せず発生した場合は、リモートURLの取り違えを疑う。

## よくある質問

**Q: `--allow-unrelated-histories`を付けるのは危険ですか？**
無関係なリポジトリを誤って混ぜる場合は危険です。その場合はURLの取り違えを疑い、リモートのURLを確認してください。意図して統合する場合は問題ありません。

**Q: 次回から同じ状況を避けるには？**
リモートを先に作る場合は、GitHub上でREADMEやLICENSEを追加せず空のリポジトリで作成してから、ローカルの履歴をpushします。逆にリモートが先にあるなら、`git clone`してから作業を始めるのが確実です。

**Q: マージとrebaseのどちらを選ぶべきですか？**
個人の新規リポジトリなら、履歴が一直線になるrebaseが読みやすいです。すでに他の人がpullしているブランチでは、ハッシュが変わらないマージの方が安全です。

## 関連記事

- [git pushが「rejected」になる原因と解決手順](/posts/git-push-rejected-fix)
- [git pullでマージコンフリクトが起きたときの対処法](/posts/git-pull-merge-conflict)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [git rebaseの基本](/posts/git-rebase-basics)
