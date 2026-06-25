---
title: 'Gitで.gitignoreを設定してファイルを管理対象から外す方法'
date: '2026-05-09'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'Gitで.gitignoreを設定してnode_modulesや.envなどのファイルを管理対象から外す方法を解説。テンプレートの活用法も紹介します。'
---

## やりたかったこと

`git status` を実行したら `node_modules/` 以下のファイルが何千件も表示されて真っ赤になった。`git add .` するたびに重くなるし、pushしたらリポジトリが数百MBになってしまった。`.gitignore` で管理対象から外す方法を調べた。

---

## 環境

- OS: macOS 13.5 / Ubuntu 22.04
- Git: 2.42.0
- Node.js: 20.11.0

---

## 試したこと・うまくいかなかったこと

`.gitignore` を新しく作って `node_modules/` と書いた。`git status` を確認したら、まだ `node_modules` の中身が表示されていた。

原因は**すでに一度 `git add` していたから**だった。`.gitignore` はgitのトラッキングに入っていないファイルを無視するものであって、すでにトラッキング済みのファイルには効かない。

次に、トラッキングを外せばいいと思って `git rm -r node_modules/` を実行したら、ローカルのファイルまで消えてしまった。`node_modules` を削除してから `npm install` し直すハメになった。

---

## 解決策

### .gitignoreファイルを作る

プロジェクトのルート（`.git` と同じ階層）に `.gitignore` を作る。

```
node_modules/
dist/
.env
.env.local
.astro/
*.log
.DS_Store
```

### すでにトラッキング済みのファイルを管理から外す

`.gitignore` を追加しただけでは既存のトラッキングには効かない。`git rm --cached` でgitのインデックスからだけ削除する（ローカルのファイルは残る）。

```bash
# 特定のファイルをトラッキングから外す
git rm --cached .env

# ディレクトリごと外す
git rm -r --cached node_modules/

# インデックスへの変更をコミットする
git add .
git commit -m "remove node_modules and .env from tracking"
```

`--cached` を付けると、ローカルのファイルはそのままでgitの管理からだけ外れる。

### テンプレートを使って生成する

https://www.toptal.com/developers/gitignore でOS・エディタ・言語を選ぶと自動生成できる。Node.js + macOS + VSCodeの組み合わせで生成したものをベースにして、プロジェクト固有のパスを追加するのが早かった。

### 特定のパターンだけ除外する書き方

```
# *.log は無視するが error.log は無視しない
*.log
!error.log

# ルート直下のTODO.txtのみ無視（サブディレクトリのは無視しない）
/TODO.txt

# buildディレクトリ以下を全て無視
build/
```

---

## ハマったポイント

- `.gitignore` は「まだgitに追加されていないファイル」だけに効く。すでにコミット済みのファイルは `git rm --cached` で明示的に外さないといけなかった。これを知らずに「なぜ効かないんだ」と30分悩んだ
- `git rm -r node_modules/` と `git rm -r --cached node_modules/` は全然違う。`--cached` なしでやるとローカルのファイルが消える
- `.env` をコミットしてしまってGitHubにpushしたことがある。「削除してpushし直せばOK」ではなく、git historyに残るのでAPIキーやパスワードは必ず変更する
- `.gitignore` の書き方はパターンに注意。`node_modules` と書くとルート以外のサブディレクトリの `node_modules` も無視される。`/node_modules` と書くとルート直下のみ。どちらでも大体の用途には問題ないが、モノレポ構成のときは注意が必要だった
- `git status` で除外されているはずのファイルが出てきたら `git check-ignore -v ファイルパス` で `.gitignore` のどのルールが当たっているか（または当たっていないか）確認できる

---

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
