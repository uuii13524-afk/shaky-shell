---
title: 'git diff コマンド完全ガイド｜変更差分の確認方法まとめ'
date: '2026-07-12'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Git', 'git diff', '差分確認', 'ステージング', 'コミット比較']
description: 'git diffコマンドの使い方を徹底解説。作業ツリーとステージングの差分、コミット間の比較、ブランチ間の差分確認、特定ファイルのみの表示まで実例付きで紹介。'
---

## ひとことで言うと

```bash
# 作業ツリーとステージングエリアの差分
git diff

# ステージング済みの差分（コミット前確認）
git diff --staged

# 特定のコミット同士を比較
git diff <commit1> <commit2>
```

---

## やりたかったこと / 現象

コミットする前に「実際に何を変更したのか」を確認したい。
`git status` はファイル名しか教えてくれないため、行単位でどこがどう変わったのかを見るには `git diff` が必要になる。

ステージングした変更とまだステージングしていない変更の違いが分からず混乱することも多い。

---

## 環境

- Git 2.30 以上
- OS: Linux / macOS / Windows（WSL2 含む）

---

## 解決策

### 基本: 作業ツリーの変更を確認する

```bash
git diff
```

これは「最後にステージング（`git add`）した状態」と「現在の作業ツリー」の差分を表示する。`git add` する前の変更を確認するときに使う。

### ステージング済みの差分を確認する（--staged / --cached）

```bash
git diff --staged
# または
git diff --cached
```

`git add` した後、コミットする前に「これから何がコミットされるか」を確認できる。

### 特定のファイルだけ差分を見る

```bash
git diff src/app.js

# 複数ファイル
git diff src/app.js src/index.js
```

### コミット同士を比較する

```bash
# 直前のコミットとの差分
git diff HEAD~1 HEAD

# 特定の2つのコミットを比較
git diff a1b2c3d e4f5g6h
```

### ブランチ間の差分を確認する

```bash
# 現在のブランチとmainの差分
git diff main

# featureブランチとmainの差分
git diff main..feature/login
```

### 変更行数のサマリーだけ見る（--stat）

```bash
git diff --stat
```

出力例:
```
 src/app.js   | 12 +++++++-----
 src/index.js |  4 ++--
 2 files changed, 10 insertions(+), 6 deletions(-)
```

ファイルが多いときに、まずどのファイルが変わったかを俯瞰するのに便利。

### 単語単位で差分を見る（--word-diff）

```bash
git diff --word-diff
```

行全体ではなく変更された単語だけをハイライトするので、文章ファイル（Markdownなど）の差分確認に向いている。

### リモートとの差分を確認する

```bash
git fetch origin
git diff origin/main
```

`git fetch` してからでないとリモートの最新状態と比較できない点に注意。

---

## よくあるエラーと対処

### 差分が何も表示されない

```bash
git diff
# 何も出力されない
```

すでに `git add` 済みの場合、`git diff` は空になる（ステージング済みとの差分がないため）。`--staged` を付けて確認する。

```bash
git diff --staged
```

### バイナリファイルで `Binary files differ` としか出ない

```bash
Binary files a/image.png and b/image.png differ
```

画像やコンパイル済みファイルなどのバイナリはテキスト差分を表示できない。必要なら `--text` オプションで強制的にテキストとして扱えるが、文字化けする可能性が高い。

### 改行コード（CRLF/LF）の違いだけで差分だらけになる

Windows と Linux/macOS の混在環境でよく起きる。

```bash
git config core.autocrlf input   # Linux/macOS
git config core.autocrlf true    # Windows
```

を設定して、以後の改行コードを統一する。

### ページャーが開いて操作しづらい

`git diff` はデフォルトで `less` などのページャーに出力される。

```bash
# ページャーを使わず標準出力にそのまま出す
git --no-pager diff

# 常に無効化したい場合
git config --global core.pager cat
```

---

## よくある質問

**Q: `git diff` と `git status` の違いは何ですか？**
`git status` は変更されたファイルの一覧のみを表示します。`git diff` は行単位で具体的にどこがどう変わったかを表示します。

**Q: ステージング前後の全ての差分をまとめて見たいです。**
`HEAD` と作業ツリーを直接比較すると、ステージング済み・未ステージング両方の差分をまとめて確認できます。

```bash
git diff HEAD
```

**Q: 削除された行だけ、追加された行だけを見ることはできますか？**
`git diff` の出力では `-` が削除行、`+` が追加行です。`grep` と組み合わせて絞り込むこともできます。

```bash
git diff | grep "^-"
```

**Q: 特定のディレクトリ配下だけ差分を見たいです。**
パスを指定すればディレクトリ単位で絞り込めます。

```bash
git diff src/components/
```

**Q: `git diff` の出力を別のツールで見やすくできますか？**
`difftool` を設定すると VSCode などの GUI ツールで差分を確認できます。

```bash
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
git difftool
```

---

## 関連記事

- [git stash の使い方](/posts/git-stash-usage)
- [git rebase の基本](/posts/git-rebase-basics)
- [git pull でコンフリクトが起きたときの対処法](/posts/git-pull-merge-conflict)
- [git log でコミット履歴を確認する方法](/posts/git-log-history)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
