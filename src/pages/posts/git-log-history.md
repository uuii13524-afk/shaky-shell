---
title: 'git logでコミット履歴を確認する方法'
date: '2026-05-17'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git logコマンドでコミット履歴を確認する方法を解説。--oneline・--graph・--since等のオプションを使った見やすいログ表示方法をまとめて紹介します。'
---

## やりたかったこと

デプロイ後に「どのコミットでこのバグが入ったか」を調べようとして `git log` を実行したが、情報が多すぎてどう絞り込めばいいかわからなかった。また、cherry-pickするためにコミットハッシュを取り出そうとしたときも、どのコマンドが一番手軽か迷った。

---

## 環境

- OS: macOS 13.5 / Ubuntu 22.04
- Git: 2.42.0

---

## 試したこと・うまくいかなかったこと

素の `git log` を実行したら1コミットあたり6行ほどの情報が表示されて、数百件のログが流れてスクロールが止まらなかった。`q` キーで終了できることすら知らずに、ターミナルを閉じて別のタブを開いた。

`--oneline` を知ってからは随分楽になったが、ブランチが分岐しているときにどこでどのブランチが分かれたのかがわからなかった。`--graph` を追加することで視覚的に確認できるとわかった。

コミットメッセージでフィルタリングしようとして `git log | grep "バグ修正"` とやっていたが、`git log --grep="バグ修正"` で直接できると知ってその方法に切り替えた。

---

## 基本的な使い方

```bash
git log --oneline              # 1行で表示（コミットハッシュ + メッセージ）
git log --oneline -10          # 最新10件のみ表示
git log --oneline --graph --all  # 全ブランチの分岐をグラフ表示
git log -p                     # 各コミットのdiffも表示
git show abc1234               # 特定コミットの詳細（diff含む）
```

`git log` はページャー（less）で開くので `q` で終了する。

---

## 検索・フィルタリング

```bash
# 特定の作者のコミットだけ見る
git log --author="Taro"

# 期間で絞る
git log --since="2026-01-01" --until="2026-06-01"

# コミットメッセージで絞る（大文字小文字を区別しない場合は -i）
git log --grep="fix" -i

# 特定のファイルに触れたコミットだけ見る
git log -- src/index.js

# 特定の文字列を追加・削除したコミットを探す（バグ調査に便利）
git log -S "getUserById"
```

---

## 差分を確認する

```bash
# 現在の変更をステージング前後で確認
git diff
git diff --staged

# 特定コミットとの差分
git diff HEAD~1
git diff abc1234..def5678

# 特定ファイルだけ見る
git diff HEAD~1 -- src/login.js
```

---

## よく使う組み合わせ

```bash
# ブランチの分岐を確認しながら最新20件
git log --oneline --graph --all -20

# デプロイ後に入った変更を確認（前回デプロイのハッシュから）
git log --oneline abc1234..HEAD

# 今日コミットしたものだけ
git log --oneline --since="today"
```

---

## ハマったポイント

- `git log` は `q` で終了する。知らないとターミナルが操作不能になったと思って焦る
- `git log --oneline` で表示される7文字のハッシュは `git cherry-pick` や `git show` でそのまま使える。フルハッシュ（40文字）を使う必要はなかった
- `--graph` は `--all` をつけないと現在のブランチの履歴しか表示されない。他のブランチの動きを確認したいときは `--all` が必要だった
- `git log -S "検索文字列"` は「その文字列がソースコードに存在した行数が変化したコミット」を探す。削除したコードがどこにあったか調べるのに便利で、`--grep` はコミットメッセージ検索、`-S` はコード内容検索と使い分けている
- `git log -- ファイルパス` のように `--` を書かないとブランチ名とファイル名の区別がつかずエラーになることがある

---

## 関連記事

- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git stashで作業を一時退避する方法](/posts/git-stash-usage)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [git cherry-pickで特定のコミットだけ別ブランチに適用する](/posts/git-cherry-pick)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
