---
title: 'git reflogで消えたコミットを復元する方法'
date: '2026-06-04'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['git', 'reflog', 'コミット復元', 'バージョン管理']
en_tags: ['git', 'reflog', 'recover commits', 'version control']
description: 'git reflogを使って誤ってリセット・削除したコミットを復元する方法。git reset --hardやrebaseで消えたと思ったコミットも復活できる。'
---

## やりたかったこと

`git reset --hard` でコミットを消してしまい、元に戻せないかと焦った。
git reflogを使えば、削除したと思ったコミットも復元できることがわかった。

## reflogとは

git reflogはHEADの移動履歴を記録しているコマンド。
通常の`git log`には表示されない「消えたコミット」も確認できる。

```bash
git reflog
```

出力例：

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~2
e4f5g6h HEAD@{1}: commit: フォームのバリデーション追加
i7j8k9l HEAD@{2}: commit: ログイン機能を実装
```

## コミットを復元する手順

### 手順1：reflogで対象のコミットを探す

```bash
git reflog
```

復元したいコミットのハッシュ（例：`e4f5g6h`）をメモする。

### 手順2：cherry-pickで取り込む

そのコミットだけ復元したい場合：

```bash
git cherry-pick e4f5g6h
```

### 手順3：resetでその時点まで戻す

その時点以降のコミットをまとめて戻したい場合：

```bash
git reset --hard e4f5g6h
```

## stashで消えたと思った変更を復元する

stashした変更がわからなくなった場合も、reflogで確認できる。

```bash
git reflog show stash
```

または、dangling commitを全部探したい時：

```bash
git fsck --lost-found
```

## ハマったポイント

- reflogの履歴はデフォルトで90日間保持される（それ以降は参照不可）
- reflogはローカルにしかない。新しいクローン環境には引き継がれない
- リモートにpush済みのコミットを取り消した場合は別途`git push --force`が必要になる
- `--orphan`ブランチでの作業はreflogに残らないことがある

## 関連記事

- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git cherry-pickで特定のコミットだけ別ブランチに適用する](/posts/git-cherry-pick)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)

## おすすめのVPS／ドメイン／スクール

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
