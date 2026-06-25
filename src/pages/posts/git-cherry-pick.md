---
title: 'git cherry-pickで特定のコミットだけ別ブランチに適用する'
date: '2026-05-21'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Git', 'cherry-pick', 'バージョン管理']
en_tags: ['Git', 'cherry-pick', 'version control']
description: 'git cherry-pickコマンドで特定のコミットだけを別ブランチに適用する方法を解説。複数コミットの指定方法やコンフリクト時の対処法も紹介します。'
---

## やりたかったこと

featureブランチで開発中に緊急のバグ修正をしてしまった。その修正だけmainブランチにも入れたかったが、featureブランチをまるごとmergeすると開発途中の機能まで入ってしまう。「特定のコミット1つだけを別ブランチに持っていきたい」と思って調べたら `git cherry-pick` にたどり着いた。

---

## 環境

- OS: macOS 13.5 / Ubuntu 22.04
- Git: 2.42.0

---

## 試したこと・うまくいかなかったこと

最初は「featureブランチからmainへmergeすればいい」と思って試したが、開発途中のコードが一緒に入ってしまった。hotfixブランチを作って修正を移植しようとしたが、そこでも同じ変更を2回手で書き直すことになって非効率だった。

`git cherry-pick` を初めて使ったとき、コミットハッシュをフルで入力しようとして長さに戸惑った。7〜8文字の短縮形でよかったと後で気づいた。

また、複数コミットをcherry-pickしたとき範囲指定の `A..B` でAが含まれないと知らずに、必要なコミットを1つ漏らして「あれ、変更が足りない」と気づくまで時間がかかった。

---

## cherry-pickの基本

```bash
# コミットハッシュを確認する（7文字の短縮形でOK）
git log --oneline

# 特定のコミットを現在のブランチに適用する
git cherry-pick abc1234
```

`git log` で持ってきたいコミットのハッシュを確認してから実行する。cherry-pickはそのコミットの変更内容を現在のブランチに新しいコミットとして追加する。

---

## 複数コミットをcherry-pickする

```bash
# 複数のコミットを個別に指定
git cherry-pick abc1234 def5678

# 連続したコミットをまとめて（abc1234の次から ghi9012 まで）
git cherry-pick abc1234..ghi9012
```

範囲指定 `A..B` はAを含まずBを含む。Aも含めたいときは `A^..B` と書く。

---

## コンフリクトが起きたとき

```bash
# コンフリクト発生
git cherry-pick abc1234
# CONFLICT (content): Merge conflict in app.js
# error: could not apply abc1234... fix: null check for user object

# ファイルを手動で修正してから
git add app.js
git cherry-pick --continue

# やっぱりやめる場合
git cherry-pick --abort
```

rebaseと同じく、コンフリクトしたファイルを修正 → `git add` → `--continue` の流れ。

---

## cherry-pickを取り消す

```bash
# cherry-pickしたコミットを打ち消すコミットを作る（push済みの場合）
git revert abc1234

# cherry-pickしたコミット自体を削除（未pushのとき）
git reset --hard HEAD~1
```

すでにpushしている場合は `git revert` で取り消しコミットを作るほうが安全。`reset --hard` は未pushのときだけ使う。

---

## ハマったポイント

- コミットハッシュは `git log --oneline` で確認するのが一番早い。フルハッシュ（40文字）を入力する必要はなく先頭7〜8文字でOK
- cherry-pickするとコミットハッシュが変わる。元のブランチとは別の独立したコミットとして記録される。「同じ変更なのに別ハッシュで2つあって混乱」という状況になりやすい
- 範囲指定 `A..B` はAを含まずBを含む。rebaseの範囲指定と同じ挙動で、これを知らずにAを漏らした
- 同じ変更を複数回cherry-pickするとコンフリクトが起きやすい。「すでに適用済みです」的なエラーは出ないので、二重に適用してしまわないように注意
- push済みのコミットを取り消すときは `reset` ではなく `revert` を使う。`reset --hard` でやってしまってforced pushが必要になった

---

## 関連記事

- [Gitのブランチ操作まとめ](/posts/git-branch-basics)
- [git commitを取り消す方法](/posts/git-commit-undo)
- [git rebaseの基本的な使い方](/posts/git-rebase-basics)
- [git logでコミット履歴を確認する方法](/posts/git-log-history)
- [git pullでコンフリクトが起きたときの解決方法](/posts/git-pull-merge-conflict)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
