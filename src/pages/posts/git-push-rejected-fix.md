---
title: 'git pushでrejectedになった時の対処法'
date: '2026-07-19'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git pushが! [rejected] (fetch first)で拒否される症状を解説します。権限エラーと誤解しがちですが原因はリモートとの分岐で、git pull --rebaseで取り込んでから再度pushする解決手順を紹介します。'
ja_tags: ['Git', 'GitHub', 'push', 'rejected', 'rebase']
en_tags: ['Git', 'github', 'push', 'rejected', 'rebase']
---

## やりたかったこと

チームで触っている機能ブランチの作業を終えて、いつも通り `git push` をしようとしたら、見慣れないエラーで撥ねられた。直前に同僚が同じブランチに別のコミットをpushしていたことに気づかず、手元のブランチが古いままローカルでコミットを積んでしまっていた。

```text
$ git push origin feature/user-settings
To github.com:example/myapp.git
 ! [rejected]        feature/user-settings -> feature/user-settings (fetch first)
error: failed to push some refs to 'github.com:example/myapp.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes
hint: (e.g., 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

「rejected」という単語だけを見て、権限の問題かと思い最初は見当違いの対応をしてしまった。

---

## 環境

- OS: Windows 11 23H2
- Git: 2.45.2 (Git for Windows)
- ターミナル: Git Bash
- リモート: GitHub（origin, SSH接続）

---

## 試したこと

最初は「rejected」という表示だけを見て権限まわりのエラーだと思い込み、SSH鍵の設定を疑って `ssh -T git@github.com` で接続確認をした → 結果は認証成功で `Hi username! You've successfully authenticated` と表示され、権限の問題ではないことが分かった → 実際にはエラーメッセージの `(fetch first)` の部分に原因が書かれていたのに、そこを読まずに関係ない箇所を調べていたのが遠回りだった。

次に、エラーメッセージ通りに `git pull` を試したところ、今度は別の警告が出て止まった。

```text
$ git pull origin feature/user-settings
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.rebase interactive # rebase (interactive)
fatal: Need to specify how to reconcile divergent branches.
```

`pull.rebase` の設定をしていなかったため、mergeとrebaseのどちらで取り込むかGitが判断できずに止まっていた。

---

## 原因

`push` が拒否されたのは、リモートのブランチが手元のローカルブランチよりも新しい状態になっていたためだ。Gitはリモートとローカルの履歴が分岐した状態で無条件に上書きされることを防ぐガードを持っており、ローカルのHEADがリモートの最新コミットの祖先になっていない場合（fast-forwardできない場合）はpushを拒否する仕組みになっている。今回は同僚のpushによってリモート側に自分の知らないコミットが追加されたため、ローカルとリモートの履歴が分岐し、このガードに引っかかった。

---

## 解決方法

### リモートの変更を取り込む（rebase）

```bash
git pull --rebase origin feature/user-settings
```

```text
Successfully rebased and updated refs/heads/feature/user-settings.
```

`--rebase` を付けることで、自分のローカルコミットをリモートの最新コミットの上に積み直してくれる。マージコミットを作らずに履歴を直線的に保てるため、機能ブランチでの作業ではこちらを選ぶことが多い。

### 取り込んだ上で改めてpushする

```bash
git push origin feature/user-settings
```

```text
Enumerating objects: 7, done.
To github.com:example/myapp.git
   a1b2c3d..9f8e7d6  feature/user-settings -> feature/user-settings
```

ローカルのHEADがリモートの最新コミットを含む状態になったことで、fast-forwardの条件を満たし、pushが通るようになる。

### コンフリクトが出た場合

rebase中に同僚と同じ箇所を編集していた場合は、以下のような表示で止まることがある。

```text
CONFLICT (content): Merge conflict in src/settings.js
error: could not apply 9f8e7d6... update user settings form
```

この場合はコンフリクト箇所を手動で解消し、`git add` してから `git rebase --continue` で再開する。

---

## ハマったポイント

- エラーメッセージの `[rejected]` という単語だけを見て権限エラーだと勘違いした。実際は `(fetch first)` の部分にヒントが書かれており、そこまで読めば遠回りせずに済んだ
- `pull.rebase` を設定していなかったため、`git pull` を実行しただけでは「mergeかrebaseか選べ」と怒られて止まった。`git config --global pull.rebase true` を先に設定しておけば毎回聞かれずに済んだ
- rebase中にコンフリクトが起きた際、焦って `git rebase --abort` を連打しそうになったが、それをすると自分のローカルコミットごと巻き戻ってしまう。落ち着いてコンフリクト箇所だけ直すべきだった
- 一度 `git push --force` で強引に上書きしようとしかけたが、それをすると同僚のコミットがリモートから消えてしまうところだった。force pushは自分だけが触っているブランチ以外では絶対にやってはいけないと再認識した

---

## よくある質問

**Q: git push rejected fetch first と git push rejected non-fast-forward の違いは？**
どちらも「ローカルとリモートの履歴が分岐していてfast-forwardできない」ことが原因で、実質同じ状況を指しています。表示される文言はGitのバージョンや操作内容によって多少異なりますが、対処法はどちらも同じで、`git pull`（または `git pull --rebase`）でリモートの変更を取り込んでから再度pushします。

**Q: git push --force を使ってもいい場面はある？**
自分一人しか触っていない個人用のブランチであれば、履歴を書き換えて `git push --force` することもあります。ただし共有ブランチで使うと他の人のコミットを消してしまう危険があるため、共有ブランチでは `git push --force-with-lease` を使い、リモートが自分の想定通りの状態の時だけ上書きされるようにするのが安全です。

**Q: pull.rebase の設定はどこで確認・変更できる？**
`git config pull.rebase` で現在の設定を確認できます。`git config --global pull.rebase true` を実行しておくと、以降 `git pull` は常にrebase方式で取り込まれるようになり、pull時に方式を毎回聞かれることがなくなります。

---

## 関連記事

- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHubに初めてpushする手順](/posts/github-first-push)
- [git reflogで消えたコミットを復元する方法](/posts/git-reflog)
