---
title: 'Gitで間違えてcommitした時の取り消し方'
date: '2026-05-06'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitで間違えてcommitした時の取り消し方を解説。git reset --softやgit revertを使ったコミットの取り消し・修正方法をまとめて紹介します。'
---

## やりたかったこと

`.env`ファイルを誤ってコミットしていたことに、pushした後で気づいた。GitHubのリポジトリをブラウザで確認したら`.env`の中身がそのまま公開されていた。`STRIPE_SECRET_KEY=sk_live_xxxxxxxx`という行がコミットの差分ビューに丸見えになっていて、かなり焦った。

しかも気づくまでに3日かかった。pushした翌日でも翌々日でもなく、3日後にGitHubのセキュリティbotから「Secret exposed in commit」という通知のissueが自動で作られていて、それで初めて気づいた。つまり3日間、誰でも`.env`の中身を見られる状態が続いていた。その間に自分のStripeのシークレットキーが悪用されていないかを確認するために、Stripeダッシュボードのアクセスログを見て回るという作業をすることになった。

急いで取り消そうとしたが、「コミットを取り消す」方法を調べると`git reset`と`git revert`の2種類が出てきてどちらを使えばいいか判断できなかった。

```
remote: error: GH007: Your push would publish a private email address.
```

別の日には上記のエラーでpushが弾かれることもあったが、`.env`は何のエラーも出ずにpushできてしまった。「弾かれるもの」だと思っていたのに、実際にはGitは内容をチェックせず何でもpushできてしまう。これが盲点だった。

コマンドを間違えて`--hard`を指定してしまい、せっかく書いたコード（`.env`とは関係ない変更）がごっそり消えてしまうという失敗もした。

```bash
git reset --hard HEAD~1
# 実行後に git status したら全部消えていた
# 1時間書いたコードがなくなっていた
```

「取り消す」操作なのに余計な変更が積み重なっていく一方で、最終的にローカルのコミット履歴が何がどうなっているか自分でもわからなくなってしまった。`git log --oneline`と`git reflog`で現在地を確認してから操作をやり直したら短時間で解決した。

`.env`を一度pushしてしまった場合、gitで履歴を消したとしてもパスワードや秘密鍵は「漏洩済み」として扱う必要がある。gitでファイルを消しても、GitHubのコミット履歴には記録が残り続けるからだ。「削除完了まで漏洩中」という意識で、コミット取り消しと同時進行でパスワード・秘密鍵の再発行が必要だったことを最初は知らなかった。

## 環境

- Git 2.44.0
- Windows 11 / Ubuntu 22.04
- GitHub（リモートリポジトリあり）

## 試したこと・うまくいかなかったこと

最初は「revertの方が安全」という情報を見て`git revert HEAD`を試した。実行するとエディタが開いてコミットメッセージを書く画面になった。Vimが開いて`:wq`で閉じたら、「Revert "add .env file"」という新しいコミットが作られた。「これで取り消せた」と思ってブラウザでGitHubを開いたら、古いコミットをクリックすると`.env`の内容が丸見えのままだった。`git revert`は「取り消しコミット」を追加するだけで、過去のコミット自体は消えていない。意味がなかった。

次に「commit自体を完全に消したい」と思って`git reset --hard HEAD~1`を使った。コミットは確かに消えたが、その時に書いていたコード全部（`.env`とは関係ない別の変更）も消えてしまった。`--soft`と`--hard`の違いを理解せずに使った結果で、1時間以上かかって書いた実装がゼロになった。`git status`を見ても何も残っていなかった。

```bash
git reset --hard HEAD~1
# 実行後
git status
# nothing to commit, working tree clean
# 1時間分の変更が跡形もなく消えた
```

`git reset`を試す前に「とりあえず一旦退避しよう」と思って`git stash`を使ったこともあった。でも`git stash`はステージングエリアやワーキングツリーの変更を退避するもので、既にコミット済みの変更には効かなかった。「stashしてから`.env`だけ取り除いてもとに戻せるかも」と思ったが、コミットが既に作られている以上stashで操作できる対象ではなかった。30分試してから「stashはコミット済みには使えない」と気づいた。

焦って複数のコマンドを試したせいで、最終的に「今のローカルのコミット履歴がどうなっているか」がわからなくなった。`git log --oneline`で現在の状態を先に確認してから操作する、というのをもっと早く習慣にするべきだった。

`git commit --amend`でコミットメッセージを修正しようとしたら、すでにpushした後だったのでリモートとの差分が生まれてしまい`git push --force`が必要になった。チームリポジトリだったのでforce pushは使えなかった。push後のコミットに`--amend`は使えない、ということを身をもって学んだ。

`.env`をrevertしてから「もう安全」と思って2日間放置してしまった。その2日間も、GitHubのコミット一覧から古いコミットをクリックすれば`.env`の内容は見えていた。コミット取り消しとパスワード変更は同時進行でやるべきだった。優先順位は「まずパスワード変更、その後履歴から削除」が正しい順番だった。

## 解決策

状況に合わせてコマンドを使い分ける。まだpushしていないか、すでにpushしたかで方法が変わる。

### 1. 直前のcommitを取り消したい（ファイルの変更は残す）

**pushする前の場合はこれが最も安全。** コミットは消えるが、変更したファイルはstaged状態で残る。

```bash
git reset --soft HEAD~1
```

実行後は`git status`で確認するとファイルが「Changes to be committed」の状態になっている。`.env`を`git restore --staged .env`でアンステージしてから、`.gitignore`に追加して改めてコミットする。

```bash
git restore --staged .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: remove .env from tracking"
```

`.gitignore`に先に追加しておかないと、次のコミット時にまた`.env`が含まれてしまう。順番が重要で、「アンステージ」→「.gitignoreに追加」→「.gitignoreをコミット」という流れをこの通りに実行する。

実行後に`git log --oneline`でコミットが消えたことを確認して、`git status`でファイルの状態が期待通りになっているか確認してから次の操作に進む。

### 2. 直前のcommitを完全に取り消したい（ファイルの変更も消す）

ファイルの変更ごと全部なかったことにしたい場合。**元に戻せないので実行前に`git diff HEAD~1`でどんな変更が消えるか必ず確認する。**

```bash
git diff HEAD~1  # 消える変更を先に確認
git reset --hard HEAD~1
```

実行後は`git log --oneline`でコミット履歴を確認して、意図した状態になっているか確認する。

`--hard`を実行する前に必ず現在のコミットハッシュをメモしておく。万が一間違えた場合でも`git reflog`から復元できる（後述）。実行前のコミットハッシュは`git log --oneline`の一番上に表示されている。

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

amendを使う前に「まだpushしていないか」を確認する方法は`git status`の出力を見ること。「Your branch is ahead of 'origin/main' by 1 commit」が出ていればpush前でamendを使っていい。「Your branch is up to date」が出ていれば既にpushされているのでamendは使わない。

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

ただし`.env`を含むコミットをpushしてしまった場合は、`git revert`だけでは不十分。GitHubのコミット履歴にはまだ`.env`の内容が残っているので、**パスワードや秘密鍵はすぐに変更・再発行するのが先決**。その後、履歴から完全に削除するには`git filter-repo`を使う。

```bash
# git-filter-repoをインストール（Python環境が必要）
pip install git-filter-repo

# 特定ファイルを全履歴から削除
git filter-repo --path .env --invert-paths
```

実行後は`git push --force`が必要になる。個人リポジトリであれば問題ないが、チームリポジトリの場合は全メンバーへの事前告知が必要（後述）。

`git filter-repo`がインストールできない環境では、GitHub側の「Allow Secret Scanning」や「Revoke exposed credentials」機能で対応できることもある。ただしGitHubのトークンスキャン機能はGitHub発行のトークン（PATなど）に限られる。自分で生成したAPIキーはGitHub側では検知されないので、漏洩した認証情報は必ず手動で無効化する。

### 5. filter-repo実行後の注意点

`git filter-repo`で履歴を書き換えた後、GitHubにpushしても古いコミットがGitHubのキャッシュに残ることがある。完全に削除されたことを確認するには、GitHubのサポートにキャッシュのクリアを依頼する必要がある場合もある。

`git filter-repo`実行後にforce pushした後は、全コラボレーターがローカルのリポジトリをcloneし直す必要がある。古いリポジトリ状態でpullしても正常にマージできないことがある。「filter-repoを実行する前に全員に告知してcloneし直してもらう」という段取りが必要だった。告知なしでforce pushしたら、チームメンバーからすぐに「pushできなくなった」と連絡が来た。

`git filter-repo`実行後はローカルのリポジトリ自体も「履歴が書き換わったリポジトリ」になっているため、`git pull`では取得できなくなる。「filter-repo後に`git pull`したら`fatal: refusing to merge unrelated histories`と出てpullできなくなった」という状況になった。この場合は自分も含めてクリーンな状態から`git clone`し直すのが一番早い。

### 6. 2つ以上前のcommitを取り消したい

`HEAD~1`の数字を変えれば何個でも指定できる。どのコミットまで戻るか確認してから実行する。

```bash
git log --oneline  # 現在の履歴を確認
git reset --soft HEAD~3  # 3つ前まで取り消す場合
```

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

### 7. --hardで消してしまった変更を復元する

`git reset --hard`で消してしまっても、`git reflog`で一定期間は復元できる。これを知らずに1時間分の作業をゼロから書き直したことがあった。

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

`git reflog`のエントリはデフォルトで90日間保持される。消してしまってもすぐに調べれば助かることがある。reflogは`git log`では表示されないローカルの操作履歴で、resetやmergeなどの操作も含めて全部記録されている。

`git reset --hard`を「完全に元に戻せない操作」だと思っていたが、実際には90日以内ならreflogで復元できる「ほぼ元に戻せる操作」だった。この事実を知ってから`--hard`への恐怖感が薄れた。

### 8. 操作前にgit stashで一時退避する

「ちょっとここを試してみたい」という時には`git stash`が`git reset`より安全な選択肢になる。

```bash
git stash           # 変更を退避
git stash pop       # 退避した変更を戻す
git stash list      # 退避リストを確認
```

stashは複数個積み重ねることができる。`git stash list`で一覧を確認して、`git stash pop stash@{1}`で特定のstashを取り出す使い方もある。破壊的な操作を試したい前に`git stash`しておくと、失敗しても`git stash pop`で元に戻せる。

stashはコミット前の変更を退避する機能で、既にコミット済みの変更には効かない。「コミット済みの変更をstashで取り消せるかも」と思って試したが、コミット後の変更はstashの対象外だった。

### 9. .envを誤ってpushした時の緊急対応手順

`.env`や認証情報を含むファイルをpushしてしまった場合の対応は「Gitの操作」と「認証情報の無効化」を必ず並行して進める。Git操作だけでは不十分で、その間も漏洩が続いている。

**Step 1：認証情報を即時無効化する（最優先）**

```
- Stripe/AWS/GCPなどのダッシュボードにログインして該当キーを削除または無効化する
- GitHubのPATが含まれている場合はGitHub Settings → Developer settings から削除する
- DBパスワードが含まれている場合はDBのパスワードを即時変更する
- 新しいキー/パスワードを発行して.envを更新する（まだGitにはコミットしない）
```

Step 1は文字通り最初にやること。git filter-repoを実行している間も漏洩は続いている。

**Step 2：.gitignoreに追加してローカルでアンステージ**

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "remove .env from tracking"
```

**Step 3：git filter-repoで全履歴から削除**

```bash
pip install git-filter-repo
git filter-repo --path .env --invert-paths
```

**Step 4：force pushしてチームに通知**

```bash
git push --force origin main
```

force push前に必ずチームメンバーに連絡する。「force pushします。完了したら全員git cloneし直してください」という内容で。

**Step 5：re-clone（自分自身も含む）**

```bash
# 旧ディレクトリを削除または別名でバックアップ
cd ..
mv my-project my-project-old
git clone https://github.com/yourname/my-project.git
cd my-project
# .envを新しいキーで作成する
```

filter-repo後は`git pull`ができなくなるため、自分自身もcloneし直す必要がある。

**Step 6：GitHubのキャッシュクリアを依頼（必要に応じて）**

force push後もGitHubのキャッシュに古いコミットが残ることがある。`https://github.com/yourname/repo/commit/古いハッシュ`のURLにアクセスして`.env`の内容が見えないことを確認する。まだ見える場合はGitHub Supportに連絡してキャッシュクリアを依頼する。

## ハマったポイント

- `--soft`と`--hard`の違いは「ファイルの変更を残すかどうか」だと思っていたが、実際にはもう少し厳密に言うと「インデックス（ステージ）とワーキングツリーをどこまでリセットするか」の違いだった。`--soft`はコミットだけ消えてファイルはstaged状態で残る。`--mixed`（デフォルト）はコミットとステージが消えてファイルは残る。`--hard`はコミット・ステージ・ワーキングツリーすべて消える。「とりあえずコードを消さずにコミットだけ取り消したい」なら`--soft`一択だった
- `git revert`は「安全な取り消し方法」だと思っていたが、実際には「取り消しコミットを追加する方法」で、過去のコミット内容は履歴に残り続けることを理解していなかった。`.env`を含むコミットを`git revert`してもGitHubのコミット一覧で古いコミットをクリックすれば`.env`の内容は見えてしまう。pushしてしまった機密情報は「リポジトリから削除した」ではなく「漏洩済み」として扱うべきだった
- `git commit --amend`はpush前限定の操作だと思っていたが、push後にもコマンド自体は動いてしまう。実行すると「ローカルのコミット履歴がリモートより進んでいる」状態になり、次の`git push`が弾かれる。その時に`git push --force`で強引に通そうとして、チームのリモート履歴を書き換えてしまった。push後のコミットには絶対にamendを使わないと決めた
- `.gitignore`に追加する順番を間違えていた。「`git reset --soft HEAD~1`でコミットを取り消す」→「`.env`をアンステージ」→「`.gitignore`に追加してコミット」という順番で操作したつもりが、`.gitignore`を追加する前に`git add .`してしまい`.env`がまた含まれてしまった。2回同じミスをしてようやく順番の重要性を理解した
- `git reset --hard`でコードが消えてしまっても諦めないこと。「`--hard`で消えたものは永遠に戻らない」と思っていたが、実際には90日以内なら`git reflog`からコミットのハッシュを探して復元できる。これを知らなくて1時間分の作業をゼロから書き直したことがあった。`git reset --hard`を実行する前に現在のハッシュをメモしておく癖をつけた
- `.env`をpushしてしまった後、「git revertで取り消した後は安全」だと思っていたが、GitHubの古いコミットをブラウザで開くと`.env`の内容が丸見えだった。gitの操作でできることは「新しい状態を作る」ことだけで、過去の履歴は`git filter-repo`を使わない限り消せない。コミット取り消しと認証情報の再発行は別々の問題だった
- `git filter-repo`を実行したら全コラボレーターにcloneし直しを依頼する必要があると思っていたが、実際に告知せずにforce pushしてしまって「pushできない」という連絡がチームメンバーから来た。force pushで共有ブランチの履歴を書き換えると、他の人のローカルリポジトリは「存在しないコミットの子」という状態になる。事前告知は必須だった
- 複数の操作を焦って連続で実行すると`git log --oneline`を見ても現在の状態が把握できなくなる、と思っていたが、`git log --oneline`は「現在地」を教えてくれるだけで「どういう操作をしたか」は`git reflog`を見ないとわからなかった。操作に行き詰まったら`git reflog`で操作の全履歴を確認するのが一番状況を整理しやすかった
- `git revert`でコミットを取り消した後も、GitHubのコミット一覧には「Revert "コミットメッセージ"」という新しいコミットが追加されるだけで、元のコミットは履歴上で閲覧可能な状態のまま残る。「履歴から完全に消す」ためには`git filter-repo`が必要で、これはrevertとは全く別の操作だった。この違いを理解するのに時間がかかった
- GitHubのSecret Scanning機能はGitHub発行のトークン（PAT、GitHub Actionsシークレットなど）を自動検知するが、StripeのシークレットキーやカスタムのAPIキーは検知対象外だった。「GitHubが自動で検知して教えてくれる」と思い込んでいたが、任意のAPIキーは自分で気づくしかない。GitHub Secret Scanningが通知してくれたのはGitHub PATだけで、Stripeキーは3日間スルーされていた
- `.env`をpushしてから気づくまで3日かかった。GitHubのセキュリティbotが自動issueを作成してくれたことで発覚したが、それまでリポジトリは誰でも見られる状態だった。pushした後に一度ブラウザでGitHubのコミット差分を確認する習慣があれば即日気づけた。今は必ずpush後に差分をブラウザで確認するようにしている
- `git filter-repo`実行後に`git pull`をしようとしたら`fatal: refusing to merge unrelated histories`と出てpullできなくなった。filter-repoで履歴が書き換わったため、ローカルとリモートが「別のリポジトリ」という扱いになってしまった。`git pull`で解決しようとして時間を無駄にしたが、正解は`git clone`でやり直すことだった

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
