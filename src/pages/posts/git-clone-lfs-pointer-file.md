---
title: 'git cloneしたファイルがLFSポインタ文字列のままになる原因と解決手順'
date: '2026-08-03'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git clone直後、Git LFS管理下のファイルが実体ではなくoidやsizeが書かれたポインタ文字列のままになる症状を解説。原因を切り分け、git lfs pullで実体を取得するまでの手順を紹介します。'
ja_tags: ['Git', 'Git LFS', 'クローン']
en_tags: ['Git', 'Git LFS', 'clone']
---

## やりたかったこと（症状）

チームで運用している`design-assets`リポジトリを新しいマシンにセットアップするため、`git clone`した。このリポジトリは以前からGit LFSで`*.psd`と`*.mp4`を管理している。

```bash
git clone git@github.com:example-team/design-assets.git
cd design-assets
ls -lh assets/banner_main.psd
```

サイズを確認したところ、本来100MB近くあるはずのファイルが、わずか130バイトしかなかった。

```text
-rw-r--r-- 1 user user 130 Aug  3 09:12 assets/banner_main.psd
```

中身を`cat`で見てみると、画像データではなくテキストが表示された。

```bash
cat assets/banner_main.psd
```

```text
version https://git-lfs.github.com/spec/v1
oid sha256:9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a
size 104857600
```

Photoshopで開こうとしても「ファイルが破損している可能性があります」というエラーで開けない。他のメンバーの環境では問題なく開けているとのことだったので、自分の環境固有の問題だと判断した。

## 環境

- OS: Windows 11 23H2（WSL2 Ubuntu 22.04.4上で作業）
- Git: 2.43.0
- Git LFS: 未インストール（今回の直接原因）
- リポジトリ: `design-assets`（GitHub、`.gitattributes`でLFS設定済み）
- 該当ファイル: `assets/banner_main.psd`（実体は約100MB）

## 試したこと

最初は「クローンが途中で失敗したのでは」と考え、`.git`ディレクトリごと削除して再クローンした。

```bash
rm -rf design-assets
git clone git@github.com:example-team/design-assets.git
```

結果は同じで、`banner_main.psd`は130バイトのポインタ文字列のままだった。ネットワーク起因ではなく、クローン自体は正常に完了しているのに中身だけが実体化していない、という状態だと分かった。

次に、リポジトリ内に`.gitattributes`が存在するかを確認した。

```bash
cat .gitattributes
```

```text
*.psd filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
```

LFSの設定自体はリポジトリ側に正しく存在していた。ここで、自分のマシン側に何か足りないのではと考え、`git lfs`コマンドを実行してみた。

```bash
git lfs version
```

```text
git: 'lfs' is not a git command. See 'git --help'.
```

この時点で、`git-lfs`拡張そのものがマシンにインストールされていないことに気づいた。`.gitattributes`の`filter=lfs`が指定するスムージング（チェックアウト時にポインタを実体に置き換える処理）は`git-lfs`本体がフックとして登録しないと機能しない。インストールされていない環境では、`git clone`はポインタファイルの中身をそのままワーキングツリーに展開するだけになる。

## 原因

Git LFSは、`git clone`や`git checkout`時に「ポインタファイルを実データに置き換える」処理をクリーン・スムージフィルターというGitの拡張機構で行っている。このフィルターは`git lfs install`を実行してはじめてグローバルのGit設定（`~/.gitconfig`）に登録される仕組みで、`git-lfs`コマンド自体がインストールされていないマシンでは登録のしようがない。

そのため、`git-lfs`未インストールの環境で`.gitattributes`にLFS設定のあるリポジトリを`clone`すると、Gitは`filter=lfs`を認識できず「そのままの中身」、つまりリポジトリに実際にコミットされているポインタテキスト（`version` / `oid` / `size`の3行）をそのままファイルとして書き出す。これはエラーにも警告にもならず、`git clone`自体は正常終了として扱われるため、ファイルサイズを確認するまで気づきにくい。

## 解決手順

### 1. git-lfsをインストールする

WSL2のUbuntu側で作業していたため、APTでインストールした。

```bash
sudo apt update
sudo apt install git-lfs
```

```text
Setting up git-lfs (3.4.0-1) ...
Git LFS initialized.
```

### 2. git lfs installでフィルターを登録する

インストールしただけではリポジトリに紐付いていないため、明示的にフィルターを登録する。

```bash
git lfs install
```

```text
Updated Git hooks.
Git LFS initialized.
```

`~/.gitconfig`に`filter.lfs.*`の設定が追加されたことを確認した。

```bash
git config --global --get-regexp filter.lfs
```

```text
filter.lfs.clean git-lfs clean -- %f
filter.lfs.smudge git-lfs smudge -- %f
filter.lfs.process git-lfs filter-process
filter.lfs.required true
```

### 3. 既存のワーキングツリーをLFS実体で上書きする

再クローンせずに済むよう、既存の作業ディレクトリ内でポインタファイルを実体に置き換える`git lfs pull`を実行した。

```bash
cd design-assets
git lfs pull
```

```text
Downloading LFS objects:  50% (1/2), 52 MB | 8.1 MB/s
Downloading LFS objects: 100% (2/2), 100 MB | 8.4 MB/s, done.
```

### 4. ファイルサイズを確認する

```bash
ls -lh assets/banner_main.psd
```

```text
-rw-r--r-- 1 user user 100M Aug  3 09:41 assets/banner_main.psd
```

実データのサイズに戻っていることを確認した。

## 動作確認

Photoshopで`assets/banner_main.psd`を開き、正常にレイヤーが読み込まれることを確認した。念のため、まっさらな別ディレクトリに再クローンしても同じ結果になるかを試した。

```bash
git clone git@github.com:example-team/design-assets.git design-assets-check
cd design-assets-check
ls -lh assets/banner_main.psd
```

```text
-rw-r--r-- 1 user user 100M Aug  3 09:55 assets/banner_main.psd
```

`git lfs install`を済ませた環境であれば、`clone`の時点から実体としてチェックアウトされることを確認できた。

## まとめ

- `git-lfs`未インストールの環境で`clone`すると、LFS管理下のファイルは`version` / `oid` / `size`が書かれたポインタ文字列のままワーキングツリーに展開される。これはエラーにならないため、ファイルサイズを見るまで気づきにくい。
- 対処は`git-lfs`のインストールと`git lfs install`によるフィルター登録、既存クローンなら追加で`git lfs pull`。新しいマシンをセットアップする際は、`clone`前に`git lfs install`を済ませておくのが確実。
- 同種の「サイズが極端に小さいファイルが実体を持たない」症状は、動画・デザインファイル・モデルファイルなど、LFSで管理しがちな種類のファイルを扱うリポジトリで起こりやすい。中身を`cat`して`version https://git-lfs.github.com/spec/v1`が出てきたら、まずこの原因を疑うとよい。

## よくある質問

**Q: `git lfs install`はリポジトリごとに実行する必要がありますか？**
`git lfs install`自体はマシン単位（グローバルGit設定）で一度実行すれば十分です。以降はそのマシン上でLFS対応リポジトリを`clone`するたびに自動でフィルターが働きます。ただし`git-lfs`本体のインストールは今回のようにマシンが変わるたびに必要です。

**Q: 既にポインタファイルのままcloneしてしまった場合、再クローンは必須ですか？**
不要です。`git-lfs`をインストールし`git lfs install`を実行したあとで、既存の作業ディレクトリ内で`git lfs pull`を実行すれば、ポインタファイルを実体に置き換えられます。

**Q: CI環境でも同じ問題が起きますか？**
起きます。CIのビルドイメージに`git-lfs`が入っていないと、`checkout`アクション等でLFSファイルがポインタのまま展開され、ビルドが実体を期待する処理で失敗します。CI側の環境にも`git-lfs`のインストールと`git lfs install`（もしくは対応するCIアクションのLFSオプション）が必要です。

## 関連記事

- [git pushがGitHubの100MB制限で拒否される原因と解決手順](/posts/git-push-large-file-rejected)
- [git remoteの基本操作](/posts/git-remote-operations)
- [GitHubへの初回pushでつまずいた話](/posts/github-first-push)
- [git reflogでコミットを復元する方法](/posts/git-reflog)
- [SSH鍵をGitHubに登録する方法](/posts/ssh-key-github)
