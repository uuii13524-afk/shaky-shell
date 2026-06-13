---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitで間違えてcommitした時の取り消し方を解説。git reset --softやgit revertを使ったコミットの取り消し・修正方法をまとめて紹介します。'
---

## やりたかったこと

`.env`ファイルを誤ってコミットしていたことに、pushした後で気づいた。GitHubのリポジトリをブラウザで確認したら`.env`の中身が公開されていて焦った。急いで取り消そうとしたが、`git reset`と`git revert`の2種類が出てきてどちらを使えばいいかわからなかった。

コマンドを間違えて`--hard`を指定してしまい、せっかく書いたコードが消えてしまった失敗もした。「コミットの取り消し」を調べるとたくさんのコマンドが出てきて、状況ごとにどれを使うべきか整理できていなかったのが根本の問題だった。

## 環境

- Git 2.44.0
- Windows 11 / Ubuntu 22.04
- GitHub（リモートリポジトリあり）

## 試したこと・うまくいかなかったこと

「commitを取り消す」方法を調べたら`git reset`と`git revert`の2種類が出てきた。「revertの方が安全」という情報を見て`git revert HEAD`を使ったら、取り消し用の新しいコミットが作られた。これだとpushした後に`.env`を含むコミットは履歴に残ったままで、GitHubのコミット履歴を見れば内容が閲覧できる状態が続いていた。「取り消した」のに`.env`の内容はまだGitHub上に存在している状態で、意味がなかった。

次に「commit自体を完全に消したい」と思って`git reset --hard HEAD~1`を使ったら、確かにコミットは消えたが、直前に書いていたコード（`.env`とは関係ない変更）もすべて消えてしまった。`--hard`と`--soft`の違いを理解せずに使った失敗で、1時間分の作業が消えた。

`git commit --amend`でメッセージだけ修正しようとしたら、すでにpushした後だったのでリモートとの差分が生まれてしまい、`git push --force`が必要になってしまった。チームリポジトリだったのでforce pushは使えなかった。

焦って複数のコマンドを試したせいで、最終的に「今のローカルのコミット履歴がどうなっているか」が把握できなくなった。`git log --oneline`で現在の状態を先に確認してから操作する、というのをもっと早く習慣にするべきだった。

`.env`を一度revertしてから「もう安全」と思っていたが、GitHubのコミット履歴ページで古いコミットをクリックしたら`.env`の内容が丸見えのままだった。gitでコミットを「取り消す」ことと「履歴から消す」ことは全く別物だとこのとき初めて理解した。

## 解決策

状況に合わせてコマンドを使い分ける。まだpushしていないか、すでにpushしたかで方法が変わる。

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

**pushする前の場合はこれが最も安全。** コミットは消えるが、変更したファイルはそのままstaged状態で残る。

```bash
git reset --soft HEAD~1
```

実行後は`git status`で確認するとファイルが「Changes to be committed」の状態になっている。`.env`を`git restore --staged .env`でアンステージしてから、`.gitignore`に追加してから改めてコミットする。

```bash
git restore --staged .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: remove .env from tracking"
```

`.gitignore`に先に追加しておかないと、次のコミット時にまた`.env`が含まれてしまうので順番が大事。

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も消す）

ファイルの変更ごと全部なかったことにしたい場合。**元に戻せない**ので、実行前に`git diff HEAD~1`でどんな変更が消えるか確認しておく。

```bash
git diff HEAD~1  # 消える変更を確認してから
git reset --hard HEAD~1
```

実行後は`git log --oneline`でコミット履歴を確認して、意図した状態になっているか確認する。

### 3. commitメッセージだけ変更したい

まだpushしていない場合のみ使う。pushした後に使うとforce pushが必要になる。

```bash
git commit --amend -m "新しいメッセージ"
```

ファイルの変更も含めてamendしたい場合は、先にファイルをステージしてからamendする。

```bash
git add 修正したいファイル
git commit --amend --no-edit  # メッセージはそのまま、内容だけ修正
```

### 4. pushした後に取り消したい場合

pushした後は`reset`で履歴を書き換えるとチームに迷惑がかかる（他の人のローカルと履歴が食い違う）。`revert`で「取り消しコミット」を新しく作る方法が安全。

```bash
git revert HEAD
```

エディタが開いてコミットメッセージを書く画面になる（Vimが開く場合は`:wq`で保存して閉じる）。取り消し用のコミットが作られたあと`git push`すれば完了。

エディタを開かずにデフォルトメッセージでコミットしたい場合：

```bash
git revert HEAD --no-edit
git push
```

`.env`を含むコミットをpushしてしまった場合は、`git revert`だけでは不十分。GitHubのコミット履歴にはまだ`.env`の内容が残っているので、**パスワードや秘密鍵はすぐに変更・再発行するのが先決**。その後、履歴から完全に削除するには`git filter-repo`コマンドを使う。

```bash
# git-filter-repoをインストール
pip install git-filter-repo

# 特定ファイルを全履歴から削除
git filter-repo --path .env --invert-paths
```

実行後は`git push --force`が必要になる。個人リポジトリであれば問題ないが、チームリポジトリの場合は全メンバーへの事前告知が必要。

`git filter-repo`がインストールできない環境では、GitHub側の「Allow Secret Scanning」や「Revoke exposed credentials」機能で対応することもできる。ただしGitHubのトークンスキャン機能はGitHub発行のトークン（PATなど）に限られるので、自分で生成したAPIキーはGitHub側では検知されない。漏洩した認証情報は必ず手動で無効化する。

### 5. 2つ以上前のcommitを取り消したい

`HEAD~1`の数字を変えれば何個でも指定できる。どのコミットまで戻るか確認してから実行する。

```bash
git log --oneline  # 現在の履歴を確認
git reset --soft HEAD~3  # 3つ前まで取り消す場合
```

コミット履歴の確認方法は[git logでコミット履歴を確認する方法](/posts/git-log-history)に詳しくまとめた。

特定のコミットのハッシュで指定することもできる。

```bash
git log --oneline
# d4e5f6g feature: 追加機能
# a1b2c3d fix: バグ修正
# 9z8y7x5 initial commit

# a1b2c3dのコミットだけを取り消したい場合
git revert a1b2c3d
```

この方法は途中のコミットだけを「なかったことにする」のに使える。`reset`と違って他のコミットは保持されたまま。

### 6. --hardで消してしまった変更を復元する

`git reset --hard`で消してしまっても、`git reflog`で一定期間は復元できる。

```bash
git reflog
```

実行すると操作の履歴が出てくる。

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~1
d4e5f6g HEAD@{1}: commit: 1時間かけて書いた変更
```

`HEAD@{1}`のハッシュに戻したい場合：

```bash
git reset --hard d4e5f6g
```

`git reflog`のエントリはデフォルトで90日間保持されるので、消してしまってもすぐに調べれば助かることがある。reflogは`git log`では表示されないローカルの操作履歴で、resetやmergeなどの操作も含めて全部記録されている。

コマンドを実行する前に`git stash`で一時退避しておけば、後から元の状態に戻せる。「ちょっとここを試してみたい」という時には`git stash`が`git reset`より安全な選択肢になる。

```bash
git stash           # 変更を退避
git stash pop       # 退避した変更を戻す
git stash list      # 退避リストを確認
```

## ハマったポイント

- `--soft`と`--hard`の違いは「ファイルの変更を残すかどうか」。`--soft`はコミットだけ消えてファイルはstaged状態で残る。`--hard`はファイルの変更ごと消える。コードが消えて焦った経験から、`--hard`を使う前は必ず`git diff HEAD~1`で何が消えるか確認するようにした
- `reset`と`revert`は使いどころが全然違う。「まだpushしていない」なら`reset`で履歴を書き換えていい。「すでにpushした」なら`revert`で取り消しコミットを追加するのが安全。この使い分けを覚えるまで混乱が続いた
- `git commit --amend`をpush後に使うと`git push --force`が必要になる。チームリポジトリでforce pushは基本禁止なので、push前にcommitメッセージを確認する習慣が大事だった
- `.gitignore`に書いていない`.env`ファイルをコミットしてしまった場合は、`git reset --soft HEAD~1`でコミットを取り消してから`.gitignore`に追加する。先に`.gitignore`を直さないと、再度コミットする時にまた`.env`が含まれてしまう。この順番を間違えて2回同じミスをした
- `git reset --hard`でコードが消えてしまっても諦めないこと。`git reflog`を確認すれば90日間はコミットのハッシュが残っていて復元できる。これを知らなくて1時間分の作業をゼロから書き直したことがあった
- `.env`をpushしてしまった場合は`git revert`だけでは足りない。GitHubのコミット履歴は「取り消しコミット」を作っても過去のコミットの内容は残る。gitのコミットをブラウザで開いて差分を確認すれば`.env`の内容が見えてしまう。漏洩したパスワードは必ず即座に変更する
- 複数の操作を焦って連続で実行すると`git log --oneline`で現在の状態が把握できなくなる。操作前に必ず現在のコミット履歴を確認してから次の操作に進む。「今何番目のコミットにいるか」を常に意識する習慣が大事だった

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
