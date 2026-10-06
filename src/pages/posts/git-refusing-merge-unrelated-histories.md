---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順【Git 2.43】'
date: '2026-10-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pullやgit mergeで「fatal: refusing to merge unrelated histories」と拒否される症状を再現して解説。共通の祖先コミットがない原因の確認方法と、--allow-unrelated-historiesでの統合・README競合の解消手順まで紹介します。'
ja_tags: ['Git', 'unrelated histories', 'git pull', 'merge']
en_tags: ['Git', 'unrelated histories', 'git pull', 'merge']
---

## やりたかったこと（症状）

手元で先に`git init`してコードを書き始め、あとからGitHub上に作った空ではないリポジトリ（READMEつきで作成したもの）をリモートとして登録し、ローカルの作業を合流させようとしました。`git remote add origin`のあとに`git pull origin main`を実行したところ、次のエラーで止まります。

```text
From ../remote
 * branch            main       -> FETCH_HEAD
fatal: refusing to merge unrelated histories
```

`git merge origin/main`でも同じ文言です。

```text
fatal: refusing to merge unrelated histories
```

この記事は、この状況をローカルのベアリポジトリで再現し、出力を確認しながら原因と解決手順をまとめたものです。GitHubのURLではなく`../remote.git`をリモートにしているため、パス表記だけは実際のGitHub URLと異なります。

## 環境

- OS: Linux（カーネル 6.18）
- Git: 2.43.0
- 再現方法: ローカルにベアリポジトリ（`remote.git`）を作り、別ディレクトリで`git init`した2つのリポジトリを用意
- ブランチ名: `main`

## 試したこと

### 1. まずpushしてみる

最初に考えたのは、ローカルのコミットをそのままpushすることでした。

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
```

リモートに自分の持っていないコミットがあるため拒否されました。ヒントに従って`git pull`することになります。

### 2. 素の`git pull`

Git 2.43で`pull.rebase`を未設定のまま実行すると、先に別のエラーが出ます。

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

これはmergeかrebaseかを選べという案内です。`--no-rebase`を付けて再実行すると、冒頭の`refusing to merge unrelated histories`にたどり着きました。

```bash
git pull origin main --no-rebase
```

```text
fatal: refusing to merge unrelated histories
```

つまり「divergent branches」の警告は入口にすぎず、本当の問題は別にあります。

## 原因

2つのブランチに**共通の祖先コミットが1つもない**ことが原因です。Gitのmergeは、2つのブランチの共通祖先（merge base）を起点に3-wayマージを行います。共通祖先がないと起点が決まらないため、Git 2.9以降は既定でマージを拒否します。

実際に共通祖先があるかどうかは、次のコマンドで確認できます。

```bash
git fetch origin
git merge-base main origin/main
echo "exit=$?"
```

```text
exit=1
```

共通祖先があればコミットのハッシュが表示されますが、ここでは何も出力されず終了コードが`1`でした。これが「無関係な履歴（unrelated histories）」の正体です。

履歴を並べても確認できます。

```bash
git log --oneline --all
```

```text
125e717 first local commit
3616893 Initial commit (remote)
```

どちらも最初のコミット（親を持たないroot commit）が別物になっています。ローカルで`git init`して作った履歴と、GitHub側でREADMEつきで作成されたときに生まれた履歴は、別々のroot commitから始まっているため、つながりません。典型的な発生パターンは次のとおりです。

- ローカルで`git init`したあと、READMEやLICENSE付きで作成したGitHubリポジトリを`remote add`した
- 別々に`git init`した2つのプロジェクトを1つにまとめようとした
- `rm -rf .git`してから`git init`し直したあと、元のリモートにpullした

## 解決手順

### 1. 統合してよい履歴かを先に確認する

`--allow-unrelated-histories`は「本当に関係のない履歴でも結合してよい」と明示するオプションです。誤ったリモートを指定していると、無関係なプロジェクトが混ざってしまいます。実行前にリモートのURLと中身を確認します。

```bash
git remote -v
git log --oneline origin/main
```

### 2. `--allow-unrelated-histories`でマージする

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

ファイル名が重ならない場合は、これだけで統合が完了します。今回の再現ではローカルに`index.js`、リモートに`README.md`だけがあったため、次のように成功しました。

```text
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

履歴は共通祖先のない2本が1つのマージコミットで合流する形になります。

```bash
git log --oneline --graph
```

```text
*   5ba6043 Merge branch 'main' of ../remote
|\  
| * 3616893 Initial commit (remote)
* 125e717 first local commit
```

### 3. 同名ファイルがある場合は競合を解消する

実際に多いのは、ローカルにもリモートにも`README.md`があるケースです。この場合、`add/add`競合になります。

```bash
git merge origin/main --allow-unrelated-histories --no-edit
```

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

`git status -sb`では、両側で追加されたことを示す`AA`が表示されます。

```text
## main
AA README.md
```

ファイルを開くと、通常の競合マーカーが入っています。

```text
# my-app

<<<<<<< HEAD
local notes
=======
Created on GitHub
>>>>>>> origin/main
```

エディタで必要な内容を残してマーカー行を消し、ステージしてコミットします。

```bash
git add README.md
git commit --no-edit
```

途中でやめたい場合は`git merge --abort`で元に戻せます。

### 4. rebaseで統合したい場合

履歴を一直線にしたいならrebaseも使えます。ただしrebaseは自分のコミットを相手のroot commitの上に載せ直すため、同名ファイルがあるとコミットごとに競合を解消することになります。再現では次のように止まりました。

```bash
git rebase origin/main
```

```text
Could not apply a2112a0... first local commit
```

```bash
git status -sb | head -3
```

```text
## HEAD (no branch)
AA README.md
A  index.js
```

競合を直して`git add`したあと、`git rebase --continue`で進めます。やめる場合は`git rebase --abort`です。なお、このrebaseでは`--allow-unrelated-histories`は不要でした。rebaseは共通祖先を前提にせず、自分のコミットを指定先の上に再適用するためです。mergeだけが共通祖先を要求します。

## 動作確認

統合後にpushします。リモートに自分にない履歴はもう残っていないので、通常のfast-forwardとして通ります。

```bash
git push -u origin main
```

```text
To ../remote.git
   3616893..5ba6043  main -> main
branch 'main' set up to track 'origin/main'.
```

念のため、共通祖先が見つかるようになったことも確認します。

```bash
git merge-base main origin/main
```

今度はコミットのハッシュが表示され、終了コードも`0`になります。

## まとめ

- `refusing to merge unrelated histories`は、2つのブランチに共通祖先がないときにmergeが拒否される挙動。`git merge-base`が何も返さなければ確定です。
- 統合してよい履歴だと確認できたら、`git pull origin main --allow-unrelated-histories`で合流させる。同名ファイルは`add/add`競合になるので手で解消する。
- 次回から避けるには、先にGitHubで空のリポジトリ（READMEなし）を作ってローカルをpushするか、`git clone`したディレクトリで作業を始める。

同じ「履歴が合わない」系のエラーとして、リモートが先に進んでいる`rejected`や、片方の履歴を置き換える強制pushの判断にも応用できます。まず`git log --oneline --all --graph`で履歴の形を見る癖をつけると、原因の切り分けが早くなります。

## FAQ

**Q: `--allow-unrelated-histories`を付けて大丈夫ですか？**
同じプロジェクトの履歴だと確認できているなら問題ありません。リモートURLを間違えているだけの場合、無関係なコードが履歴に混入するので、実行前に`git remote -v`と`git log origin/main`で確認してください。やってしまったときは、pushする前なら`git reset --hard ORIG_HEAD`でマージ直前に戻せます。

**Q: `git pull`で毎回divergent branchesの案内が出ます。**
`git config --global pull.rebase false`（merge）か`true`（rebase）を設定すると出なくなります。ただしこれは別の警告で、unrelated historiesとは無関係です。

**Q: リモートの履歴は捨ててローカルで上書きしたいです。**
`git push --force-with-lease`で上書きできますが、リモートの履歴が消えます。共同作業者がいる場合は事前に合意を取ってください。

## 関連記事

- [git pullでマージ競合が起きたときの解決手順](/posts/git-pull-merge-conflict)
- [git pushが拒否されるときの原因と解決手順](/posts/git-push-rejected-fix)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
