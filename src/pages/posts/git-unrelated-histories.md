---
title: 'git mergeで「fatal: refusing to merge unrelated histories」が出る原因と解決手順'
date: '2026-08-10'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '別々に git init した2つのリポジトリの履歴を統合しようとすると発生する「fatal: refusing to merge unrelated histories」の原因を解説。--allow-unrelated-historiesでの解決と、その後に起きるadd/addコンフリクトの直し方まで手順化しました。'
ja_tags: ['Git', 'merge', 'unrelated histories']
en_tags: ['Git', 'merge', 'unrelated histories']
---

## やりたかったこと（症状）

以前個人で作っていた小さなスクリプト置き場のリポジトリ（`old-scripts`）を、新しく育てているメインのリポジトリ（`main-project`）に取り込みたかった。単純にファイルをコピーするだけだとコミット履歴（いつ・なぜその変更をしたか）が失われてしまうので、`old-scripts`をリモートとして追加し、`fetch`してから`merge`することで履歴ごと取り込もうとした。

```bash
cd main-project
git remote add old-scripts ../old-scripts
git fetch old-scripts
git merge old-scripts/master
```

ここで以下のエラーが出て、マージが即座に拒否された。

```text
fatal: refusing to merge unrelated histories
```

`fetch`自体は正常に終わっており、`git log old-scripts/master`でリモートのコミットも確認できる。にもかかわらず`merge`だけが弾かれる状態だった。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- 統合元リポジトリ: `old-scripts`（`git init`で単独に作成、コミット1件）
- 統合先リポジトリ: `main-project`（`git init`で単独に作成、コミット1件、`old-scripts`とは完全に無関係な履歴）

再現用に、実際と同じ状況を最小構成で作り直して確認した。

```bash
mkdir repoA && cd repoA && git init -q
echo "# Project A" > README.md
git add README.md && git commit -q -m "Initial commit A"

cd .. && mkdir repoB && cd repoB && git init -q
echo "# Project B" > README.md
git add README.md && git commit -q -m "Initial commit B"

git remote add origin-a ../repoA
git fetch origin-a -q
git merge origin-a/master
```

```text
fatal: refusing to merge unrelated histories
```

同じエラーを再現できた。

## 試したこと

最初は「リモートの追加やfetchのやり方が間違っているのでは」と考え、`git remote -v`でリモートが正しく登録されているか、`git log origin-a/master --oneline`でコミットが取得できているかを確認した。

```bash
git remote -v
```

```text
origin-a	/path/to/repoA (fetch)
origin-a	/path/to/repoA (push)
```

```bash
git log origin-a/master --oneline
```

```text
4dc2c0e Initial commit A
```

リモートの登録もfetchも問題なく、ローカルから`origin-a/master`のコミットも参照できている。つまり「取得」はできているのに「統合」だけが拒否されているという状態だと分かった。ここで`git merge --help`を確認し、`unrelated histories`という語で調べ直したところ、Git 2.9以降で追加された安全機構であることに気づいた。

## 原因

`git merge`はデフォルトで、マージ対象の2つのブランチが「共通の祖先コミット」を持つことを前提にしている。しかし今回のように、それぞれを個別に`git init`して作った2つのリポジトリには、共通の祖先が存在しない。

Git 2.9より前はこの場合でも警告なくマージできてしまい、無関係な2つのプロジェクトを誤って`merge`してしまう事故が起きていた（例えば、間違ったディレクトリで`git pull`した結果、意図せず無関係なリポジトリの内容が混ざり込むケース）。この事故を防ぐため、Git 2.9で「共通の祖先を持たない履歴同士のマージはデフォルトで拒否する」という安全策が導入された。これが`fatal: refusing to merge unrelated histories`の正体で、バグではなく意図的なガードレールになる。

今回のケースは「無関係な履歴を意図的に1つに統合したい」という、まさにこのガードが警告している状況そのものだった。したがって単純にガードを解除すればよいと判断した。

## 解決手順

### 1. `--allow-unrelated-histories`を付けてマージする

このオプションを付けると、共通祖先の有無チェックをスキップしてマージを進めてくれる。

```bash
git merge origin-a/master --allow-unrelated-histories
```

```text
Auto-merging README.md
CONFLICT (add/add): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
```

ガード自体は通過したが、今度は`README.md`が両方のリポジトリに存在し、内容が異なるため`add/add`コンフリクトが発生した。これは無関係な履歴を統合する際にほぼ確実に起きる想定内の事態なので、通常のコンフリクト解消と同じ手順で対応する。

### 2. コンフリクトの状態を確認する

```bash
git status
```

```text
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
	both added:      README.md
```

```bash
cat README.md
```

```text
<<<<<<< HEAD
# Project B
=======
# Project A
>>>>>>> origin-a/master
```

`HEAD`側（統合先の`main-project`相当）と`origin-a/master`側（統合元の`old-scripts`相当）の両方の内容が競合マーカーで表示されている。

### 3. コンフリクトを解消してコミットする

今回は両方の内容を活かす形に手動で書き換え、競合マーカーを削除した。

```bash
cat > README.md <<'EOF'
# Project B

Merged history from Project A.
EOF

git add README.md
git commit -m "Merge project-a into project-b (unrelated histories)"
```

コミットメッセージにはマージであることが分かるよう`--allow-unrelated-histories`を使った旨を残しておくと、後から履歴を追う人が経緯を理解しやすい。

## 動作確認

マージ後のコミットグラフで、2つの独立した履歴が1本に統合されていることを確認した。

```bash
git log --graph --oneline --all
```

```text
*   351b7cd Merge project-a into project-b (unrelated histories)
|\
| * 4dc2c0e Initial commit A
* 8215240 Initial commit B
```

`git status`もクリーンな状態に戻っていることを確認した。

```bash
git status
```

```text
On branch master
nothing to commit, working tree clean
```

統合元リポジトリ（`old-scripts`）にあった全コミットの履歴が、`main-project`側の履歴に枝として組み込まれた状態になっている。

## まとめ

- `fatal: refusing to merge unrelated histories`は、共通の祖先コミットを持たない2つの履歴を`merge`しようとしたときにGit 2.9以降が出す安全機構によるエラーで、故障ではない。
- 意図的に無関係な履歴を1つに統合したい場合は`git merge <branch> --allow-unrelated-histories`でガードを解除する。ただし解除しただけでファイル内容の衝突までは解決しないため、その後の`add/add`コンフリクトは通常どおり手動で解消してコミットする必要がある。
- 逆に、意図せずこのエラーが出た場合（間違ったリモートやブランチをマージしようとしている等）は、オプションで無理に通さず、まず`git remote -v`や`git log <remote>/<branch> --oneline`でマージしようとしている相手が本当に正しいかを確認したほうがよい。

## よくある質問

**Q: `--allow-unrelated-histories`はいつでも安全に使えますか？**
統合したい2つの履歴が本当に「同じ内容を別々に管理していたもの」であれば問題ありません。ただし全く無関係なプロジェクトを誤って指定した状態でこのオプションを使うと、意図しないファイル群がそのまま取り込まれてしまうため、マージ前に`git log <remote>/<branch> --oneline`で相手のコミットを必ず確認してください。

**Q: マージを途中でやめたい場合はどうすればよいですか？**
コンフリクト解消前であれば`git merge --abort`でマージ開始前の状態に戻せます。今回の手順でも、`--allow-unrelated-histories`実行直後の`add/add`コンフリクトが発生した時点でまだコミットはしていないため、`git merge --abort`が有効です。

**Q: `git pull`でも同じエラーが出ますか？**
出ます。`git pull`は内部的に`fetch`＋`merge`を実行しているため、リモート側と共通祖先を持たない状態で`git pull`すると同じ`fatal: refusing to merge unrelated histories`になります。その場合は`git pull <remote> <branch> --allow-unrelated-histories`のように同じオプションを付けます。

## 関連記事

- [git pushがGitHubの100MB制限で拒否される原因と解決手順](/posts/git-push-large-file-rejected)
- [git pull時のマージコンフリクトの解決方法](/posts/git-pull-merge-conflict)
- [git remoteの基本操作](/posts/git-remote-operations)
- [git reflogでコミットを復元する方法](/posts/git-reflog)
- [git cloneしたファイルがLFSポインタ文字列のままになる原因と解決手順](/posts/git-clone-lfs-pointer-file)
