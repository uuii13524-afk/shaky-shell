---
title: 'git checkoutで「Your local changes...would be overwritten」が出て切り替えられない原因と解決手順'
date: '2026-09-26'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git checkoutでブランチを切り替えようとすると「Your local changes to the following files would be overwritten by checkout」で失敗する症状を解説。原因の切り分けとgit stashによる解決手順を紹介します。'
ja_tags: ['Git', 'git checkout', 'git stash']
en_tags: ['Git', 'git checkout', 'git stash']
---

## やりたかったこと（症状）

`main`ブランチで作業中の設定ファイル`config.json`を一旦置いたまま、別チームが`feature/add-retry-option`ブランチに追加した変更を先に確認したくなった。よくある「ちょっと他のブランチを見てから戻ってくる」だけのつもりで、深く考えずに`git checkout`を実行した。

```bash
git checkout feature/add-retry-option
```

しかし次のエラーで止まった。

```text
error: Your local changes to the following files would be overwritten by checkout:
	config.json
Please commit your changes or stash them before you switch branches.
Aborting
```

`exit=1`で終了しており、ブランチは切り替わっていない。commitした覚えはないのに「local changesが上書きされる」と言われて、最初は何が起きているのか分からなかった。

## 環境

- OS: Ubuntu 24.04.4 LTS (Noble Numbat)
- Git: 2.43.0
- 対象ファイル: `config.json`（`main`と`feature/add-retry-option`の両方で追跡されているファイル）
- 状況: `main`ブランチ上で`config.json`を編集したが、commitもstashもしていない状態

## 試したこと

まず「エラーメッセージのとおり、そもそも何がuncommittedなのか」を`git status`で確認した。

```bash
git status
```

```text
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   config.json

no changes added to commit (use "git add" and/or "git commit -a")
```

たしかに`config.json`がmodified状態のままだった。デバッグ用に`"debug": false`を`"debug": true`に書き換えて、そのまま放置していたのを忘れていた。

```bash
git diff
```

```text
diff --git a/config.json b/config.json
index 9bb899a..6000699 100644
--- a/config.json
+++ b/config.json
@@ -1,4 +1,4 @@
 {
   "env": "production",
-  "debug": false
+  "debug": true
 }
```

ここで一瞬「`commit`していないだけなら`checkout`くらいできるのでは」と思ったが、Gitの立場で考えると理由が見えてくる。`feature/add-retry-option`側の`config.json`は`retry`キーが追加された別バージョンであり、作業ツリーの`config.json`（未commitの変更入り）を単純に上書きしてブランチを切り替えると、`debug: true`にした変更が跡形もなく消えてしまう。Gitはこの「破棄されうる未保存の変更」を検知すると、`checkout`自体を中止して警告を出す仕様になっている。

## 原因

`git checkout <branch>`は、切り替え先のブランチが記録している内容でワーキングツリーのファイルを置き換える。もし対象ファイルが切り替え元・切り替え先の両方で追跡されており、かつワーキングツリー側にcommitされていない変更があると、Gitはその変更を「これから上書きされて失われる可能性がある差分」と判断する。

今回のケースでは、

- `main`側の`config.json`：`debug: true`（未commit）
- `feature/add-retry-option`側の`config.json`：`retry: 3`が追加されたcommit済みバージョン

という状態で、どちらも同じファイルパスを追跡しているため、Gitはこの二つをマージすることができず、安全側に倒して`checkout`を中止する。これはGitが持つ「未commitの変更を黙って消さない」という設計上の保護機能であり、バグではない。むしろここでエラーにならずに黙って上書きされていたら、`"debug": true`に直した変更は復元不可能な形で消えていたはずである。

紛らわしいのは、エラーメッセージが「would be overwritten」と言っているだけで、なぜ上書きされるのか（別ブランチ側にも同じファイルの別バージョンがあるから）までは説明してくれない点だった。`git diff`で自分の変更内容を、`git log --oneline feature/add-retry-option -- config.json`のようなコマンドで相手ブランチ側の変更内容を確認すると、双方が同じファイルを触っていることがはっきりする。

## 解決手順

### 1. 未commitの変更内容を確認する

```bash
git diff
```

先に見た通り、`debug`フィールドの変更のみだった。消えても困らないゴミ変更なら`git restore config.json`で捨ててもよいが、今回は後で使う変更だったので残したい。

### 2. git stashで変更を一時退避する

```bash
git stash
```

```text
Saved working directory and index state WIP on main: d9f2ad0 initial commit
```

### 3. ワーキングツリーがcleanになったことを確認する

```bash
git status
```

```text
On branch main
nothing to commit, working tree clean
```

### 4. 目的のブランチへ切り替える

```bash
git checkout feature/add-retry-option
```

```text
Switched to branch 'feature/add-retry-option'
```

今度はエラーなく切り替わった。

```bash
cat config.json
```

```text
{
  "env": "production",
  "debug": false,
  "retry": 3
}
```

`feature/add-retry-option`側の内容（`retry: 3`入り）が正しく展開されている。

### 5. 確認が終わったらmainへ戻り、stashを復元する

```bash
git checkout main
git stash pop
```

```text
Switched to branch 'main'
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   config.json

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (95b4ca24866e1dbd45da2592e314864d1b4426b5)
```

## 動作確認

`config.json`の中身が、退避前と同じ`debug: true`の状態に戻っていることを確認した。

```bash
cat config.json
```

```text
{
  "env": "production",
  "debug": true
}
```

`git stash list`も空になっており、stashの取りこぼしがないことも確認できた。これで`main`側の未commitの変更を保ったまま、一時的に`feature/add-retry-option`の内容を確認するという当初の目的を達成できた。

## まとめ

- `git checkout`は、切り替え先ブランチと現在のワーキングツリーで同じファイルが競合する未commitの変更を検知すると、それを保護するために処理を中止する。「Your local changes...would be overwritten by checkout」はバグではなく、変更を失わせないための安全装置。
- 対処は「消してよい変更」か「残したい変更」かで分かれる。残したくない場合は`git restore <file>`で破棄、残したい場合は`git stash`で退避してから`checkout`する。
- 戻ってきたら`git stash pop`で退避内容を復元する。複数回stashしている場合は`git stash list`で対象を確認してから`pop`や`apply`を使うと事故が減る。

## よくある質問

**Q: `git stash`せずに直接ブランチを切り替える方法はありますか？**
Git 2.23以降なら`git switch --discard-changes <branch>`で強制的に切り替えられますが、その名の通り未commitの変更は破棄されて戻せません。今回のように変更を残したい場合は素直に`git stash`を使うほうが安全です。

**Q: `git stash pop`で「CONFLICT」が出た場合はどうすればよいですか？**
stash退避後にブランチ側でも同じ箇所が変更されていると競合します。コンフリクトマーカー（`<<<<<<<`など）が入ったファイルを手動で解消し、`git add`した上で、`git stash drop`で該当のstashを削除すれば完了です（`pop`は復元に失敗した場合stashを自動削除しないため、解消後に`drop`が必要です）。

**Q: 毎回`git status`で確認するのが面倒です。省略できますか？**
`checkout`前に`git diff --stat`を打つ癖をつけておくと、どのファイルが未commitなのか一目で分かります。それでも今回のようなエラーに遭遇したら、まず慌てずに`git status`と`git diff`で「何を残したいか」を確認するのが最短ルートです。

## 関連記事

- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git worktree addで「is already used by worktree」の原因と解決手順](/posts/git-worktree-already-checked-out)
- [git cloneしただけではsubmoduleが空のままビルドに失敗する原因と解決手順](/posts/git-submodule-not-initialized)
