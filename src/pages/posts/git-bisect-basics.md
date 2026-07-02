---
title: 'git bisectでバグ混入コミットを特定する方法'
date: '2026-07-02'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['git', 'bisect', 'デバッグ', 'バージョン管理']
description: 'git bisectを使ってバグが混入した原因のコミットを二分探索で特定する方法を解説。good/badの指定方法や、テストを自動実行するbisect runの使い方も紹介します。'
---

## ひとことで言うと

```bash
git bisect start
git bisect bad              # 現在のコミットはバグあり
git bisect good v1.0.0      # このコミットは正常だった
```

Gitが自動的に中間のコミットへ移動するので、動作確認して `good` / `bad` を繰り返す。

---

## やりたかったこと / 現象

いつの間にかバグが混入していたが、原因のコミットがわからない。
コミット履歴が数百件もある場合、1件ずつ手作業で確認するのは現実的ではない。
`git bisect` を使うと二分探索でバグ混入コミットを効率的に特定できる。

---

## 環境

- Git 2.20以降（`bisect run` を使う場合は自動テストスクリプトを用意）
- 動作確認: Git 2.39

---

## 解決策

### 手順1: bisectを開始する

```bash
git bisect start
```

### 手順2: 現在のコミットに bad を指定

```bash
git bisect bad
```

### 手順3: 正常だったとわかっているコミットに good を指定

```bash
git bisect good v1.0.0
```

タグやコミットハッシュ、ブランチ名を指定できる。これで対象範囲が確定し、Gitが自動的に中間のコミットにチェックアウトする。

### 手順4: 動作確認して good / bad を判定

チェックアウトされたコミットでバグが再現するか確認し、以下のどちらかを実行する。

```bash
git bisect bad   # バグが再現した場合
git bisect good  # バグが再現しなかった場合
```

これを繰り返すと、最終的に「最初にバグが入ったコミット」がGitによって特定される。

### 手順5: 終了する

```bash
git bisect reset
```

元のブランチ・コミットに戻る。

### スクリプトで自動化する（git bisect run）

手動判定の代わりにテストスクリプトを使えば全自動で特定できる。

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run npm test
```

テストが失敗（終了コードが0以外）すれば `bad`、成功（終了コード0）すれば `good` と自動判定される。

---

## よくあるエラーと対処

### fatal: bad revision '...'

指定したタグやコミットが存在しない。`git log --oneline` や `git tag` で対象が存在するか確認する。

### bisectの途中でビルドが通らないコミットに当たる

そのコミット自体を判定対象から除外したい場合は次を使う。

```bash
git bisect skip
```

### git bisect run で判定がおかしくなる

Gitは終了コード125を「テスト不能（ビルド失敗など）」として扱い、そのコミットをスキップする仕様になっている。テストスクリプト側でビルドが失敗する場合は125を返すようにしておくと精度が上がる。

---

## よくある質問

**Q: bisectの途中で中断してもいい？**
`git bisect reset` でいつでも中断でき、元のブランチに戻れる。

**Q: goodとbadの判定を間違えたらどうする？**
`git bisect log` で判定履歴を確認できる。ログを修正して `git bisect replay` でやり直すことも可能。

**Q: 大量のコミットがあっても時間がかかる？**
二分探索なので、1000件のコミットでもlog2(1000)≈10回程度の判定で特定できる。

**Q: リモートの変更履歴に対しても使える？**
ローカルにフェッチ済みであれば使える。リモート上のコミットに直接アクセスすることはできない。

---

## 関連記事

- [git logでコミット履歴を確認する方法](/posts/git-log-history)
- [git reflogで消えたコミットを復元する方法](/posts/git-reflog)
- [git cherry-pickで特定のコミットだけ別ブランチに適用する](/posts/git-cherry-pick)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
