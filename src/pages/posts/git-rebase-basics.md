---
title: 'git rebaseの基本的な使い方'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Git', 'rebase', 'バージョン管理']
en_tags: ['Git', 'rebase', 'version control']
---

## やりたかったこと

featureブランチをmainに取り込む前に、コミット履歴をきれいに整理したかった。
mergeだと余計なマージコミットが増えるのが気になっていた。

## rebaseの基本

```bash
# mainの最新をfeatureブランチに取り込む
git switch feature/my-feature
git rebase main
```

mergeと違い、コミット履歴が一直線になる。

```bash
# rebase前
main:    A - B - C
feature:     D - E

# rebase後
main:    A - B - C
feature:         D' - E'
```

コミットが新しいベースの上に「移植」されるイメージ。

## コンフリクトが起きたとき

```bash
# コンフリクト発生
git rebase main
# CONFLICT (content): Merge conflict in app.js

# ファイルを手動で修正してから
git add app.js
git rebase --continue

# やっぱりやめる場合
git rebase --abort
```

mergeと同様にファイルを編集して `git add` → `git rebase --continue` の流れ。

## インタラクティブrebaseでコミットを整理する

```bash
# 直近3コミットを編集する
git rebase -i HEAD~3
```

エディタが開き、各コミットの操作を指定できる。

```
pick abc1234 fix typo
pick def5678 add feature
pick ghi9012 fix bug

# よく使う操作
# pick   = そのまま使う
# squash = 前のコミットに合体させる
# reword = コミットメッセージを書き直す
# drop   = コミットを削除する
```

細かいコミットをまとめてプルリクをきれいにするときに使いやすい。

```bash
# squashで2つを1つにまとめる例
pick abc1234 add feature
squash def5678 fix typo in feature
```

保存するとメッセージを編集するエディタが開く。

## リモートにpush済みのブランチをrebaseしたとき

```bash
# rebase後にpushするとエラーになる
git push origin feature/my-feature
# error: failed to push some refs

# 強制pushが必要（自分だけが使うブランチのみ）
git push --force-with-lease origin feature/my-feature
```

`--force-with-lease` は他の人が同じブランチにpushしていた場合に上書きを防いでくれる。
共有ブランチ（mainやdevelopなど）には絶対に使わない。

## ハマったポイント

- `git rebase --abort` を知らずにパニックになった。迷ったら中止できる
- rebase後はコミットのハッシュが変わるので、pushにforce系が必要になる
- mainブランチを直接rebaseすると履歴が壊れる。featureブランチ側でやる
- コンフリクトが多いときは `git rebase --abort` してmergeに切り替えるのもあり
- squashしすぎるとどこで何を変えたか分からなくなる

## 関連記事

- [Gitのブランチ操作まとめ](/posts/git-branch-basics)
- [git commitを取り消す方法](/posts/git-commit-undo)
- [git pullでコンフリクトが起きたときの解決方法](/posts/git-pull-merge-conflict)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
- [git stashの使い方](/posts/git-stash-usage)
