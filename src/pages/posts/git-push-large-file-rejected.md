---
title: 'git pushが「remote rejected」でファイルサイズ超過（100MB超）により弾かれる原因と解決手順'
date: '2026-08-02'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git push実行時に「remote rejected」となり、GitHubのファイルサイズ上限100MBを超過したファイルが原因で拒否される症状を解説。git filter-repoで履歴から大容量ファイルを削除し、Git LFSで再発を防ぐまでの手順を紹介します。'
ja_tags: ['Git', 'GitHub', '大容量ファイル']
en_tags: ['Git', 'GitHub', 'large file']
---

## やりたかったこと（症状）

`study-notes`という個人用リポジトリに、検証用のサンプル動画ファイル`assets/demo.mp4`（約105MB）を追加してコミットし、そのままGitHubへ`git push`しようとした。

```bash
git add assets/demo.mp4
git commit -m "add demo video for docs"
git push origin main
```

コミット自体は問題なく成功したが、`push`が途中で止まり、次のようなエラーで拒否された。

```text
remote: error: GH001: Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.
remote: error: Trace: 3f5a1e2b8c9d4a7f6e2c1b0a9d8e7f6c5b4a3d2e
remote: error: See http://git.io/iEPt8g for more information.
remote: error: File assets/demo.mp4 is 105.34 MB; this exceeds GitHub's file size limit of 100.00 MB
To github.com:example-user/study-notes.git
 ! [remote rejected] main -> main (pre-receive hook declined)
error: failed to push some refs to 'github.com:example-user/study-notes.git'
```

`git commit`は通っているのに`push`だけが拒否される、という挙動に最初は戸惑った。ローカルのコミット自体は正常に見えるため、何が悪いのか一見分かりにくい。

## 環境

- OS: Ubuntu 22.04.4 LTS
- Git: 2.43.0
- リモート: GitHub.com（プライベートリポジトリ、SSH接続）
- Git LFS: 未導入（今回問題の原因の一つ）
- 該当ファイル: `assets/demo.mp4`（105.34 MB）

## 試したこと

まず、`push`が失敗しただけで、コミット自体は取り消せばよいだろうと考え、最新コミットで該当ファイルを削除する追加コミットを作って再度`push`した。

```bash
git rm assets/demo.mp4
git commit -m "remove large demo video"
git push origin main
```

```text
remote: error: File assets/demo.mp4 is 105.34 MB; this exceeds GitHub's file size limit of 100.00 MB
To github.com:example-user/study-notes.git
 ! [remote rejected] main -> main (pre-receive hook declined)
error: failed to push some refs to 'github.com:example-user/study-notes.git'
```

ワーキングツリーからもインデックスからもファイルは消えているのに、まったく同じエラーで拒否され続けた。ここで、`push`が拒否しているのは「現在のファイル一覧」ではなく「これから送信しようとしているコミット履歴に含まれるすべてのオブジェクト」だと気づいた。実際、`git rm`で削除するコミットを新たに積んでも、1つ前のコミットにはまだ105MBの`demo.mp4`のBlobが残ったままで、`push`時にはその履歴も含めてリモートへ送信されようとしていた。

念のため、履歴のどこにそのファイルが存在するかを確認した。

```bash
git rev-list --objects --all | grep demo.mp4
```

```text
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 assets/demo.mp4
```

やはりオブジェクトとしては履歴中に残存しており、単にワーキングツリーから消しただけでは不十分だと確認できた。

## 原因

GitHubは1ファイルあたり100.00 MBを超えるBlobを含むpushをサーバー側の`pre-receive`フックで一律拒否する仕様になっている（50MB超では警告のみで通過するが、100MB超は必ず拒否される）。この判定は「pushしようとしているコミット群に含まれる全オブジェクト」に対して行われるため、**最新コミットでファイルを削除しても、過去のコミットにそのファイルのBlobが残っている限りpushは通らない**。

今回のケースは、`git commit -m "remove large demo video"`によって作業ディレクトリ上のファイルは消えたが、`git log`上は「追加したコミット」と「削除したコミット」の両方が履歴に残っており、`push`はその両方を送ろうとしていた。つまり履歴を書き換えない限り、この105MBのBlob自体はリポジトリのオブジェクトとして送信対象から外れないという、Git・GitHub双方の仕様どおりの挙動だった。

## 解決方法

### 1. 問題のオブジェクトが含まれるコミットを特定する

```bash
git log --oneline --all -- assets/demo.mp4
```

```text
7c8d9e0 remove large demo video
4b5c6d7 add demo video for docs
```

過去のコミットにBlobとして残っていることを再確認する。

### 2. 安全のため作業用に別ディレクトリへ再クローンする

履歴書き換えは元に戻せない操作なので、既存の作業ディレクトリを直接いじらず、別の場所にクリーンな状態で作業する。

```bash
git clone git@github.com:example-user/study-notes.git study-notes-cleanup
cd study-notes-cleanup
```

### 3. `git filter-repo`で履歴から該当ファイルを完全に削除する

`git filter-repo`（`git filter-branch`の後継として公式に推奨されているツール）を使い、全履歴から`assets/demo.mp4`を取り除く。

```bash
sudo apt install git-filter-repo
git filter-repo --path assets/demo.mp4 --invert-paths
```

`--invert-paths`を付けることで「指定パス以外を残す」ではなく「指定パスだけを履歴から除去する」動作になる。

### 4. 履歴からオブジェクトが消えたことを確認する

```bash
git rev-list --objects --all | grep demo.mp4
```

出力が空になっていれば、全コミットからBlobが除去できている。

### 5. force pushでリモートの履歴を書き換える

自分一人だけで使っているブランチであることを確認したうえで、書き換え後の履歴でリモートを上書きする。

```bash
git push origin --force --all
git push origin --force --tags
```

```text
Enumerating objects: 42, done.
...
To github.com:example-user/study-notes.git
 + 4b5c6d7...9f8e7d6 main -> main (forced update)
```

今度は`pre-receive hook declined`が出ず、正常にpushが完了した。

### 6. 今後のためにGit LFSで大容量ファイルを管理する

同じ問題を繰り返さないよう、動画・バイナリなど大きくなりがちなファイルはGit LFSで追跡する運用に切り替えた。

```bash
git lfs install
git lfs track "*.mp4"
git add .gitattributes
git commit -m "track mp4 files with Git LFS"
```

## 動作確認

```bash
git push origin main
```

```text
Everything up-to-date
```

新たに`assets/demo.mp4`相当のファイルを追加し直して確認したところ、`.gitattributes`の設定どおりLFSポインタとして扱われ、pushも問題なく完了した。

```bash
git add assets/demo.mp4
git commit -m "re-add demo video via LFS"
git push origin main
```

```text
Uploading LFS objects: 100% (1/1), 105 MB | 4.2 MB/s, done.
Enumerating objects: 4, done.
...
To github.com:example-user/study-notes.git
   9f8e7d6..1a2b3c4  main -> main
```

`pre-receive hook declined`が出なくなり、正常にリモートへ反映されたことを確認できた。

## ハマったポイント

- `git rm`でファイルを削除するコミットを積んでも、それは「新しいコミットを追加している」だけで、過去のコミットに残ったBlobは消えない。pushはそのコミット群すべてを送信対象にするため、削除コミットだけでは根本解決にならなかった。
- `git filter-repo`はデフォルトで「フレッシュなクローンでない限り実行を拒否する」安全策が入っている。既存の作業ディレクトリでいきなり実行しようとすると止められるので、素直に再クローンしてから作業するのが結局早かった。
- 履歴書き換え後の`--force`pushは、共同作業しているリポジトリでは他の人のローカル履歴と食い違いを起こす。今回は自分専用のリポジトリだったため実行したが、共有ブランチであれば事前に必ずチームへ共有してから行うべき操作だと理解した。
- GitHubのファイルサイズ制限は「50MB超で警告、100MB超で拒否」という2段階になっており、警告段階を見逃して放置すると今回のように後から100MBを超えて詰まることがある。

## よくある質問

**Q: 最初からGit LFSを使っていればこの問題は起きませんでしたか？**
起きなかったはずです。LFSで追跡されているファイルは実体ではなくポインタファイルとしてGitの通常履歴に記録されるため、100MB制限の対象になりません。大きくなりがちな種類のファイルは、追加する前に`.gitattributes`でLFS管理下に置いておくのが安全です。

**Q: `git filter-repo`と`BFG Repo-Cleaner`はどちらを使うべきですか？**
現在はGit公式ドキュメントでも`git filter-branch`より`git filter-repo`が推奨されています。今回のような「特定パスを履歴全体から除去する」用途であればどちらでも対応可能ですが、開発が活発でオプションも分かりやすい`git filter-repo`を選びました。

**Q: 50MB〜100MBのファイルはpushできますか？**
できます。ただし`push`時に警告メッセージが表示されるため、リポジトリが大きくなりすぎないよう、警告が出た時点でLFS移行を検討するのがよいと感じました。

## 関連記事

- [git pushがrejectedになる原因と対処法](/posts/git-push-rejected-fix)
- [git rebaseの基本操作](/posts/git-rebase-basics)
- [git reflogでコミットを復元する方法](/posts/git-reflog)
- [git stashの使い方](/posts/git-stash-usage)
- [GitHubへの初回pushでつまずいた話](/posts/github-first-push)
