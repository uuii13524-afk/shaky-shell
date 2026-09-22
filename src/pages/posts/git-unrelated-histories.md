---
title: 'git pullで「fatal: refusing to merge unrelated histories」が出る原因と解決手順'
date: '2026-09-22'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub上でREADME付きのリポジトリを作った後、ローカルで別途git initしたプロジェクトをpullすると「fatal: refusing to merge unrelated histories」で失敗する症状を解説。--allow-unrelated-historiesで安全にマージする手順を紹介します。'
ja_tags: ['Git', 'git merge', 'unrelated histories']
en_tags: ['Git', 'git merge', 'unrelated histories']
---

## やりたかったこと（症状）

新しいNode.jsプロジェクトをローカルで先に作り始めていた。

```bash
mkdir my-project && cd my-project
git init -b main
echo "console.log('hello')" > src/index.js
git add src
git commit -m "Initial local commit"
```

その後、GitHub側で同名のリポジトリを「Add a README file」にチェックを入れた状態で作成してしまっていたことに気づいた。ローカルにリモートを登録し、`fetch`してから`main`同士をマージしようとした。

```bash
git remote add origin git@github.com:example-org/my-project.git
git fetch origin
git branch -a
```

```text
* main
  remotes/origin/main
```

```bash
git merge origin/main
```

```text
fatal: refusing to merge unrelated histories
```

`git pull origin main`でも同じ理由で失敗する。ローカルの`main`とリモートの`main`はどちらも最初のコミットで、共通の祖先コミットを持っていないため、Gitが「これは本当に同じプロジェクトの続きなのか」を確信できずマージを拒否している状態だった。

## 環境

- OS: Ubuntu 24.04 LTS
- Git: 2.43.0
- 状況: ローカルで`git init`済みのプロジェクトと、GitHub上でREADME付きで新規作成したリポジトリを、後から`git remote add`で結びつけようとしたケース

## 試したこと

最初は単純に`git pull origin main`を再実行すれば直ると思っていたが、何度実行しても同じエラーが出た。

```bash
git pull origin main
```

```text
fatal: refusing to merge unrelated histories
```

次に、リモート側のコミットが本当に存在しているか`git log`で確認した。

```bash
git log --oneline --all --graph
```

```text
* 82e3a6b Initial local commit
* e128024 Initial commit from GitHub template
```

`--graph`表示ではあたかも一本の履歴のように並んで見えるが、これは日付順に並べているだけで、実際には`82e3a6b`と`e128024`のあいだに親子関係（共通の祖先コミット）は一切ない。ここで初めて「単なるコンフリクトではなく、そもそも履歴の出自が違う2つのリポジトリを無理やり繋げようとしている」ことに気づいた。

## 原因

Git 2.9以降、`git merge`と`git pull`は「共通の祖先コミットを持たない2つの履歴」をデフォルトではマージしない仕様になっている。これは、まったく無関係な2つのプロジェクトを誤って`fetch`・`merge`してしまう事故を防ぐための安全装置。

今回のケースでは以下の2つが独立した最初のコミットを持っていたため、これに該当した。

- ローカルで`git init`した時点の最初のコミット（`Initial local commit`）
- GitHubでリポジトリ作成時に「Add a README file」を選んだことで自動生成された最初のコミット（`Initial commit from GitHub template`）

どちらも「そのリポジトリの一番最初のコミット」であり、共通の親を持ちようがない。そのため通常の`fetch`＋`merge`のフローでは合流できず、明示的に「無関係な履歴だと分かった上でマージする」意思表示が必要になる。

## 解決手順

### 1. 現在の状態を確認する

```bash
git branch -a
```

```text
* main
  remotes/origin/main
```

ローカルの`main`とリモートの`origin/main`が両方存在し、まだマージされていないことを確認した。

### 2. `--allow-unrelated-histories`を付けてマージする

```bash
git merge origin/main --allow-unrelated-histories -m "Merge remote-tracking branch 'origin/main' into main"
```

```text
Merge made by the 'ort' strategy.
 README.md | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

エラーにならずマージが完了した。今回はローカルとリモートで同名ファイルの衝突がなかったため、コンフリクトマーカーは発生しなかった。もし双方に同名ファイル（例: 両方に`README.md`がある等）があれば、通常のマージコンフリクトと同様に手動解決が必要になる。

### 3. マージ後の履歴を確認する

```bash
git log --oneline --graph --all
```

```text
*   5ce7cd2 Merge remote-tracking branch 'origin/main' into main
|\
| * e128024 Initial commit from GitHub template
* 82e3a6b Initial local commit
```

2つの独立した履歴が、マージコミット`5ce7cd2`で正しく1本に合流したことが分かる。

### 4. リモートへpushする

```bash
git push -u origin main
```

```text
   e128024..5ce7cd2  main -> main
branch 'main' set up to track 'origin/main'.
```

## 動作確認

```bash
ls -la
```

```text
README.md
src/
```

ローカルの`src/index.js`とGitHub側の`README.md`が両方とも作業ディレクトリに存在していることを確認した。`git status`もcleanで、リモートとの追跡設定（`main` tracks `origin/main`）も正しく張られている。

## まとめ

- `fatal: refusing to merge unrelated histories`は、共通の祖先コミットを持たない2つの履歴を`merge`・`pull`しようとしたときにGitが出す安全装置的なエラーで、コンフリクトそのものではない。
- 典型的な発生パターンは、ローカルで先に`git init`していたプロジェクトと、GitHubで「Add a README file」付きで作成したリポジトリを後から結びつけるケース。両方に独立した最初のコミットができてしまう。
- 本当に同じプロジェクトの続きだと分かっている場合のみ、`git merge origin/main --allow-unrelated-histories`（または`git pull origin main --allow-unrelated-histories`）で明示的に許可してマージする。同名ファイルがあれば通常どおりコンフリクト解決が必要。

## よくある質問

**Q: `git pull`にも`--allow-unrelated-histories`は使えますか？**
使えます。`git pull origin main --allow-unrelated-histories`とすることで、`fetch`＋`merge`を1コマンドで実行できます。内部的には今回の`git merge --allow-unrelated-histories`と同じ処理です。

**Q: このオプションを付けるのが危険なケースはありますか？**
本当に無関係な（別プロジェクトの）リポジトリを誤って`fetch`・マージしようとしている場合に付けてしまうと、無関係なファイル群がそのまま合流してしまいます。付ける前に`git log --oneline --all --graph`で、双方の履歴が本当に同じプロジェクトの続きかを必ず確認してください。

**Q: そもそもこの状況を予防する方法はありますか？**
GitHubでリポジトリを作成する際に「Add a README file」のチェックを外して空のリポジトリとして作成し、ローカルの既存プロジェクトから最初にpushする運用にすれば、最初から片方だけに履歴が存在するため今回のエラー自体が発生しません。

## 関連記事

- [git pullでコンフリクトが発生した時の解決方法](/posts/git-pull-merge-conflict)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Gitのリモートリポジトリ操作まとめ（remote/fetch/pull/push）](/posts/git-remote-operations)
- [git status で fatal: not a git repository が出た時の対処法](/posts/git-fatal-not-a-git-repository)
