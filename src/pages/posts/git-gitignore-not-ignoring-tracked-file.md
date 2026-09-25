---
title: '.gitignoreに.envを追記したのにgit statusに変更が出続ける原因と解決手順'
date: '2026-09-25'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: '.gitignoreに.envを追記したのに、編集するたびgit statusに変更が表示され続ける症状を解説。原因はファイルが既に追跡対象になっていること。git rm --cachedで追跡を外して解決する手順を紹介します。'
ja_tags: ['Git', '.gitignore', 'git rm --cached']
en_tags: ['Git', '.gitignore', 'git rm --cached']
---

## やりたかったこと（症状）

個人開発中のNode.jsプロジェクトで、データベース接続情報を`.env`にまとめていた。プロジェクト初期に`.gitignore`を用意し忘れたまま最初のコミットをしてしまい、後から気づいて`.gitignore`に`.env`を追記した。

```bash
printf 'node_modules/\n.env\n' > .gitignore
git status --short
```

```text
?? .gitignore
```

この時点では`.env`が`git status`に出てこなかったので、「もうignoreされた」と思い込んだ。ところがその後、`.env`のパスワードを更新して保存し、もう一度`git status`を確認すると、しっかり変更として拾われていた。

```bash
echo "DB_PASS=changed_after_gitignore" >> .env
git status --short
```

```text
 M .env
?? .gitignore
```

`.gitignore`に書いたはずなのに、なぜ`.env`の変更だけ律儀に拾われ続けるのか分からず、`.gitignore`の書き方自体が間違っているのだと思い込み、しばらく記法を疑っていた。

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.43.0
- Node.js: v22.22.2
- npm: 10.9.7
- プロジェクト構成: `.env`（DB接続情報）、`.gitignore`、`index.js`のみの小規模リポジトリ

## 試したこと

まず`.gitignore`の中身を見直した。

```bash
cat .gitignore
```

```text
node_modules/
.env
```

パターン自体は間違っていない。次に、`.gitignore`のパターンが実際に`.env`にマッチしているか、`git check-ignore`で確認してみた。

```bash
git check-ignore -v .env
echo "exit=$?"
```

```text
exit=1
```

何も出力されず、終了コードも`1`（マッチなし）。`.gitignore`のパターンが認識されていないように見えたため、記法を`.env`から`/.env`や`**/.env`に変えて何度も試したが、結果は変わらなかった。

ここで一旦冷静になり、`git ls-files`で「そもそも今、何がgitの追跡対象になっているか」を確認した。

```bash
git ls-files
```

```text
.gitignore
index.js
.env
```

`.env`が`git ls-files`の出力に含まれていた。つまり`.env`は既に**追跡対象（tracked）**としてgitに登録済みだった。`.gitignore`をいくら書き換えても意味がなかった理由がここでようやく分かった。

## 原因

`.gitignore`は「まだgitの管理下に入っていない未追跡（untracked）ファイル」を対象外にする仕組みであり、**既に`git add`・`git commit`済みで追跡対象になっているファイルには一切効果がない**。

今回のケースでは、`.gitignore`を用意する前の最初のコミットで`.env`を含めて`git add .`してしまっていたため、`.env`は最初から追跡対象だった。その後で`.gitignore`に`.env`を追記しても、gitはすでに「このファイルは追跡します」という決定を過去のコミットで済ませているため、無視されない。

`git check-ignore -v .env`が何も出力しなかった（終了コード`1`）のも同じ理由による。`git check-ignore`はデフォルトでは追跡済みファイルに対してマッチ判定を行わない仕様になっており、パターンの書き方が間違っていたわけではなかった。事実、`git rm --cached`で追跡を外した後に同じコマンドを実行すると、今度はきちんとマッチが表示される。

```bash
git check-ignore -v .env
```

```text
.gitignore:2:.env	.env
```

このように「未追跡になって初めて`check-ignore`の判定対象になる」という挙動を知らないと、`.gitignore`の記法自体を延々と疑ってしまう。

## 解決手順

### 1. 追跡を外したいファイルをキャッシュ（インデックス）からだけ削除する

```bash
git rm --cached .env
```

```text
rm '.env'
```

`--cached`を付けることで、作業ディレクトリ上の実ファイルは残したまま、gitの追跡対象（インデックス）からのみ`.env`を外せる。これを付け忘れると`.env`自体が物理的に削除されるので注意が必要。

### 2. 状態を確認する

```bash
git status --short
```

```text
D  .env
?? .gitignore
```

`.env`が「削除（追跡解除）」としてステージされ、`.gitignore`はまだ未追跡のまま並んでいる。

### 3. `.gitignore`と一緒にコミットする

```bash
git add .gitignore
git commit -m "add gitignore and untrack .env"
```

```text
[main 2f779ab] add gitignore and untrack .env
 2 files changed, 2 insertions(+), 1 deletion(-)
 create mode 100644 .gitignore
```

これで「`.env`を追跡対象から外した」という事実そのものが履歴に残る。

### 4. 以降の編集がignoreされるか確認する

```bash
echo "DB_PASS=another_change" >> .env
git status --short
```

```text
(出力なし)
```

`.env`をさらに編集しても`git status`には一切表示されなくなった。狙い通り、以降は`.gitignore`のルールが効いている。

## 動作確認

念のため`git ls-files`で追跡対象一覧を再確認した。

```bash
git ls-files
```

```text
.gitignore
index.js
```

`.env`が一覧から消えており、`index.js`と`.gitignore`だけが追跡対象として残っていることを確認できた。`git log`で履歴も確認しておく。

```bash
git log --oneline
```

```text
2f779ab add gitignore and untrack .env
570018c initial commit
```

意図した通り、追跡解除のコミットが履歴に残っている。

## まとめ

- `.gitignore`は未追跡ファイルにしか効かない。既に`git add`・`git commit`済みのファイルは、`.gitignore`に書いても無視されない。
- `git check-ignore -v <file>`は追跡済みファイルに対して何も出力しない（終了コード`1`）。これは記法が間違っているサインではなく、「そもそも判定対象外」というサイン。まず`git ls-files`で追跡状態を確認するのが近道。
- 誤って追跡済みになってしまったファイルは`git rm --cached <file>`で実ファイルを残したまま追跡だけ外し、`.gitignore`と一緒にコミットする。過去のコミット履歴自体に含まれてしまった機密情報（今回の`.env`のパスワードなど）は、`rm --cached`しても履歴には残るため、外部に公開済みのリポジトリでは別途ローテーションや履歴の書き換えを検討する必要がある。

## よくある質問

**Q: `git rm --cached .env`を実行すると、手元の`.env`ファイルも消えますか？**
消えません。`--cached`を付けるとgitの追跡（インデックス）からのみ除外され、作業ディレクトリ上の実ファイルはそのまま残ります。`--cached`を付け忘れて`git rm .env`を実行すると実ファイルごと削除されるので注意してください。

**Q: 過去のコミットに含まれてしまった`.env`の中身（パスワードなど）はどうすればいいですか？**
`git rm --cached`は「今後の追跡から外す」だけで、過去のコミット履歴には残ったままです。リポジトリが外部に公開済みの場合は、履歴からの完全な削除（`git filter-repo`等）に加えて、漏えいした可能性のある認証情報のローテーション（パスワードやAPIキーの再発行）を必ず行ってください。

**Q: ディレクトリごと`.gitignore`に追記したのに、中の一部ファイルだけ反映されないことがあります。**
同じ原因のことが多いです。ディレクトリ内の一部ファイルだけ以前のコミットで個別に`git add`されていると、そのファイルだけ追跡対象として残り続けます。`git ls-files <ディレクトリ>`で該当ディレクトリの追跡状況を確認し、不要なものを`git rm --cached`で外してください。

## 関連記事

- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [Gitで間違えてcommitした時の取り消し方](/posts/git-commit-undo)
- [docker-composeで.envファイルを使って環境変数を管理する方法](/posts/docker-compose-env-file)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)
