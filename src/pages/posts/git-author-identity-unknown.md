---
title: 'git commitで「Author identity unknown」が出る原因と解決手順'
date: '2026-08-07'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '使い捨てのDockerコンテナ内でgit commitすると「Author identity unknown」で失敗する症状を解説。コンテナ起動のたびに~/.gitconfigが消えることが原因で、リポジトリ単位でuser.email/user.nameを設定する解決手順を紹介します。'
ja_tags: ['Git', 'git commit', 'Docker']
en_tags: ['Git', 'git commit', 'Docker']
---

## やりたかったこと（または「症状」）

CIの動作確認のために、ローカルで使い捨ての`ubuntu:24.04`コンテナを起動し、その中にリポジトリをcloneして動作検証をしていた。検証用に1行だけファイルを直して`git add`し、いつも通り`git commit`しようとしたところ、コミットが作成されずにエラーで止まった。

```bash
git add README.md
git commit -m "first commit"
```

```text
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'root@vm.(none)')
```

普段使っているホスト側のマシンでは`git config --global`で設定した`user.name`/`user.email`がずっと有効になっているため、こんなエラーは見たことがなかった。同じ`git commit -m "first commit"`をホスト側で実行すると問題なく成功する。コンテナ側だけで再現する症状だった。

## 環境

- OS（コンテナ内）: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- コンテナの起動方法: `docker run --rm -it ubuntu:24.04 bash` で毎回まっさらな状態から起動し、その都度リポジトリをcloneして検証
- ホスト側: `~/.gitconfig`にuser.name/user.emailを設定済み（過去に一度だけ`git config --global`を実行済み）

## 試したこと

まず、コンテナ内で本当にidentityが未設定なのかを`git config --list --show-origin`で確認した。

```bash
git config --list --show-origin
```

```text
(何も表示されない)
```

`user.`から始まる項目が1件も出力されなかった。ホスト側では同じコマンドを打つと`file:/root/.gitconfig  user.name=...`のように表示されるので、コンテナ内の`~/.gitconfig`自体が存在しないことが分かった。

```bash
ls -la ~/.gitconfig
```

```text
ls: cannot access '/root/.gitconfig': No such file or directory
```

念のため、エラーメッセージの指示どおりに`--global`でuser.email/user.nameを設定し、その場でコミットし直してみた。

```bash
git config --global user.email "dev@example.com"
git config --global user.name "Dev User"
git commit -m "first commit"
```

```text
[master (root-commit) a20a8cf] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

このときは無事にコミットできた。ところが、一度`exit`でコンテナを抜けて`docker run --rm -it ubuntu:24.04 bash`をやり直すと、また同じ`Author identity unknown`が再発した。`--global`で設定したはずなのに、次に起動したコンテナには一切引き継がれていない。

## 原因

原因は、コンテナの起動オプションに`--rm`を付けていたことだった。`--rm`付きのコンテナは終了と同時にコンテナ自体（コンテナレイヤーに書き込んだファイルも含めて）が破棄される。`git config --global`はコンテナ内の`$HOME/.gitconfig`（今回は`/root/.gitconfig`）にuser.name/user.emailを書き込むが、そのファイルはコンテナのレイヤーの中にしか存在しない。

つまり「グローバル設定」という言葉通りに永続化されるのは、あくまで同一コンテナが生き続けている間だけであり、コンテナを`--rm`で毎回作り直す運用では、起動のたびにまっさらな`$HOME`からスタートすることになる。ホスト側の`~/.gitconfig`とコンテナ内の`~/.gitconfig`は別ファイルであり、bind mountでもしない限り共有されない。今回は検証用に毎回コンテナを使い捨てる運用にしていたため、設定してもその場限りで消えていた。

## 解決方法

恒久的にコンテナを使い回すなら`--global`のままで問題ないが、今回のように毎回使い捨てる運用では、identityをコンテナの外から持ち込むほうが根本的な解決になる。試した中で有効だったのは次の2通り。

### 方法1: ホストの`~/.gitconfig`をコンテナにマウントする

```bash
docker run --rm -it -v "$HOME/.gitconfig:/root/.gitconfig:ro" ubuntu:24.04 bash
```

ホスト側で設定済みのuser.name/user.emailを読み取り専用でそのままコンテナに渡す。コンテナを何度作り直しても、ホスト側の設定ファイルを参照するだけなので消えない。

```bash
git config --list --show-origin
```

```text
file:/root/.gitconfig  user.email=dev@example.com
file:/root/.gitconfig  user.name=Dev User
```

### 方法2: リポジトリ単位（ローカル設定）で毎回明示的に設定する

ホスト側の設定ファイルをそのまま渡したくない場合は、clone直後にリポジトリ単位で設定するコマンドをセットで実行する運用にする。

```bash
git clone https://example.com/sample-repo.git
cd sample-repo
git config user.email "dev@example.com"
git config user.name "Dev User"
git commit -m "first commit"
```

```text
[master (root-commit) a20a8cf] first commit
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

`--global`を付けないことで設定は`.git/config`側に書き込まれ、コンテナのライフサイクルに依存せず、そのリポジトリの中でだけ確実に効く。CIスクリプトの中に組み込むなら、こちらの方が「どこから実行しても同じ挙動になる」という意味で扱いやすい。

## 動作確認

方法2の設定後、`.git/config`に書き込まれた内容を確認した。

```bash
cat .git/config | grep -A2 "\[user\]"
```

```text
[user]
	email = dev@example.com
	name = Dev User
```

`git log`でも意図したauthor/committerになっていることを確認できた。

```bash
git log --pretty=fuller -1
```

```text
commit a20a8cfb2e3fdf3572eb32021384b21dbba21a83
Author:     Dev User <dev@example.com>
AuthorDate: Fri Aug 7 00:16:28 2026 +0000
Commit:     Dev User <dev@example.com>
CommitDate: Fri Aug 7 00:16:28 2026 +0000

    first commit
```

コンテナを一度`exit`して`docker run --rm -it`で作り直しても、方法1・方法2のどちらの手順を踏めばエラーが再発しないことも確認済み。

## まとめ

- `Author identity unknown`は、実行中のシェルの`$HOME`に`.gitconfig`が存在しない（=user.email/user.nameが1件も見つからない）ときに出る。
- `--rm`付きのDockerコンテナで`git config --global`しても、コンテナを作り直せば消える。「グローバル」はコンテナのライフサイクルの中でしか永続しない。
- 使い捨て環境で毎回同じ設定を通したいなら、ホストの`.gitconfig`をread-onlyでマウントするか、リポジトリ単位の`git config user.email/user.name`をセットアップ手順に組み込むのが確実。同じ考え方はGitHub ActionsのようなCI環境でも当てはまる。

## ハマったポイント

- エラーメッセージが「今すぐ`--global`で設定すれば直る」ように読めるため、その場でコミットが通るとつい根本原因を確認せずに終わらせてしまう。実際にはコンテナを作り直した瞬間に同じ問題が再発するので、「使い捨て環境かどうか」を意識する必要があった。
- `git config --list --show-origin`を使わずに`cat ~/.gitconfig`だけで確認すると、ファイルが存在しないケースと空ファイルのケースを区別しづらい。`--show-origin`付きで確認する方が原因の切り分けが早い。
- ホストの`.gitconfig`をそのままマウントする方法は手軽だが、ホスト側に複数のメールアドレス（会社用・個人用など）を使い分けている場合は、意図しないアカウントでコミットされてしまうことがある。マウントする前にホスト側の`user.email`を確認しておくとよい。

## よくある質問

**Q: `git commit --author="Name <email>"`オプションで毎回指定すれば回避できますか？**
できますが、コミットのたびにオプションを付け忘れるリスクがあります。CIスクリプトなど自動化された環境では、事前に`git config`で設定しておく方が確実です。

**Q: `-v "$HOME/.gitconfig:/root/.gitconfig:ro"`でマウントすると、`.gitconfig`に書かれた他の設定（aliasなど）も一緒にコンテナへ渡りますか？**
はい、ファイル全体をそのままマウントするため、user.name/user.email以外の設定も含めて渡ります。identityだけを渡したい場合は、方法2のようにリポジトリ単位で明示的に設定する方が安全です。

**Q: GitHub Actions上の`actions/checkout`でも同じエラーは起きますか？**
`actions/checkout`自体はcloneのみでcommitはしないため通常は発生しません。ただし、ワークフロー内で`git commit`する自動コミット処理を書いている場合は、ランナーにuser.email/user.nameが設定されていないと同じエラーになります。ジョブの中で`git config user.email`/`git config user.name`を明示的に実行しておく必要があります。

## 関連記事

- [git commitを取り消す方法](/posts/git-commit-undo)
- [fatal: not a git repositoryエラーの対処法](/posts/git-fatal-not-a-git-repository)
- [GitHubに初めてpushする手順](/posts/github-first-push)
- [Windowsに Git をインストールする手順](/posts/windows-git-install)
