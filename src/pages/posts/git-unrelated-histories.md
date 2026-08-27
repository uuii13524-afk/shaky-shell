---
title: 'git mergeで「fatal: refusing to merge unrelated histories」が出た時の解決方法'
date: '2026-08-27'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '別々に git init した2つのリポジトリを1つに統合しようとすると出るrefusing to merge unrelated historiesの原因と、--allow-unrelated-historiesを使った解決手順を解説します。'
ja_tags: ['Git', 'unrelated histories', 'git merge', 'コンフリクト解決', 'リポジトリ統合']
en_tags: ['Git', 'unrelated histories', 'git merge', 'merge conflict', 'repository merge']
---

## やりたかったこと

個人的に `git init` して育てていた別プロジェクトのコードを、既存のメインリポジトリに1つのブランチとして取り込みたかった。GitHub上でリポジトリを新規作成し直すのではなく、ローカルの2つのリポジトリの履歴をそのまま `git merge` でくっつければいいだろうと軽く考えていた。

ところが、取り込み先のリポジトリで取り込み元をフェッチしてマージしようとした瞬間、以下のエラーで止まった。

```
fatal: refusing to merge unrelated histories
```

`git pull` で試した場合は、先にこちらの警告が出ることもある。

```
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
fatal: Need to specify how to reconcile divergent branches.
```

## 環境

- OS: Ubuntu 24.04（コンテナ環境で検証）
- Git: 2.43.0
- 状況: `git init` で作成した2つの独立したローカルリポジトリ（共通の祖先コミットを持たない）

## 試したこと

まず単純に `git pull` で取り込もうとした。

```bash
git pull /path/to/repo-b master
```

これは「divergent branches」の警告で止まり、`--rebase` や `--no-rebase` を付けても解決の糸口が見えなかった。そもそもrebaseやmergeの戦略以前に、2つのリポジトリのコミット履歴に共通の祖先が1つも存在しないことが問題だと気づいていなかった。

次に、フェッチしてから明示的に `git merge` を試した。

```bash
git fetch /path/to/repo-b master
git merge FETCH_HEAD
```

結果は同じで、次のエラーで止まった。

```
fatal: refusing to merge unrelated histories
```

## 原因

2つのリポジトリはそれぞれ別々に `git init` して作られており、最初のコミット同士に親子関係が一切ない。Gitはバージョン2.9以降、こうした「共通の祖先を持たない履歴」同士のマージをデフォルトで拒否するようになっている。これは、無関係な2つのリポジトリを誤ってマージしてしまう事故を防ぐための安全策で、実際に自分のケースも「本当に無関係な履歴を意図的に1つにまとめたい」という操作だったので、Gitの警告自体は正しく機能していた。

## 解決手順

意図的に無関係な履歴を統合したい場合は、`--allow-unrelated-histories` オプションを付けて明示的に許可する。

```bash
# 取り込み元のリポジトリをフェッチする
git fetch /path/to/repo-b master

# 無関係な履歴同士のマージを明示的に許可してマージする
git merge --allow-unrelated-histories FETCH_HEAD -m "Merge project B into project A"
```

自分の環境では、両方のリポジトリに同名の `README.md` があったため、マージはそのままでは終わらずコンフリクトになった。

```
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

これは `--allow-unrelated-histories` 特有の問題ではなく、通常の `git merge` と同じ「両方の変更を1ファイルに残すコンフリクト」なので、いつも通りの手順で解消する。

```bash
# コンフリクトマーカーが入ったファイルを確認する
cat README.md

# エディタで <<<<<<< / ======= / >>>>>>> を手動で編集して内容を確定させる

# 解決済みとしてステージングする
git add README.md

# マージコミットを完了させる
git commit -m "Merge project B into project A"
```

## 動作確認

コミット後、`git log --oneline --graph --all` で2つの履歴が1本のマージコミットに合流していることを確認した。

```bash
git log --oneline --graph --all
```

```
*   fc79c3d Merge project B into project A
|\
| * f08ba49 Initial commit for project B
* 40e3102 Initial commit for project A
```

`git status` も `nothing to commit, working tree clean` になり、コンフリクトが残っていないことを確認できた。

## よくある質問

**Q: `--allow-unrelated-histories` を付けるとコンフリクトも自動で消えますか？**
消えません。このオプションは「共通の祖先がない履歴同士でもマージ処理自体は許可する」というだけで、実際にファイルの内容が競合していれば通常のマージと同じくコンフリクトになります。マーカーを手で解消して `git add` → `git commit` する必要があります。

**Q: `git pull` と `git fetch` + `git merge` はどちらを使うべきですか？**
今回のように「そもそも履歴がつながっているか怪しい」場面では、`git pull` でいきなり取り込むよりも、`git fetch` で一度履歴だけ取得してから `git log FETCH_HEAD` などで中身を確認し、そのうえで `git merge` するほうが事故が少ない。`git pull` は内部的に fetch と merge（もしくは rebase）をまとめて実行するため、想定外の統合が起きても気づきにくい。

**Q: `--allow-unrelated-histories` を毎回付けなければいけないのは面倒です。デフォルトで許可できませんか？**
グローバル設定でこの挙動自体を無効化するオプションはない。これは「誤って無関係なリポジトリをマージする」という重大な事故を防ぐための意図的な安全策なので、必要なときだけ都度オプションを付けるのが安全。頻繁に同じ2つのリポジトリを統合する運用であれば、そもそも `git subtree` や `git submodule` など別の統合方法が適していないかを見直したほうがいい。

## まとめ

- `fatal: refusing to merge unrelated histories` は、共通の祖先コミットを持たない2つのリポジトリをマージしようとした時にGitが安全のために出す拒否メッセージ。
- 意図的な統合であれば `git merge --allow-unrelated-histories` を付けて明示的に許可すればよい。ただし同名ファイルがあればコンフリクトは通常通り発生するので、そこは別途手動で解消する。
- 逆に言えば、心当たりのないタイミングでこのエラーが出た場合は「本当は無関係なリポジトリを誤ってマージしようとしていないか」を先に疑ったほうがいい。安全策として出ているエラーを無条件にオプションで突破するのは避ける。

## 関連記事

- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [git reflogで消えたコミットを復元する方法](/posts/git-reflog)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
