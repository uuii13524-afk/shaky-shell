---
title: 'GitHub Actionsのgit pushでPermission deniedが出た時の対処法'
date: '2026-07-15'
category: 'GitHub Actions'
layout: '../../layouts/PostLayout.astro'
description: 'GitHub Actionsのgit pushで403 Permission denied to github-actions[bot]が出る症状を解説します。ワークフローYAMLのpermissions: contents: writeとリポジトリ設定の両方が必要な理由と解決手順を紹介します。'
ja_tags: ['GitHub Actions', 'git push', 'Permission denied', 'GITHUB_TOKEN']
en_tags: ['GitHub Actions', 'git push', 'permission denied', 'GITHUB_TOKEN']
---

## やりたかったこと（または「症状」）

Astroのビルド設定を変更したついでに、GitHub Actions上で `prettier --write` を走らせて自動整形した差分をそのままリポジトリにコミットバックするワークフローを組んでいた。ローカルでは何度も動作確認していたコマンド列だったので、pushして終わりのつもりだった。

ところが、workflowを実行するとフォーマット処理自体は正常に終わるのに、最後の `git push` の直前で止まり、Actionsのログに次のエラーが出た。

```text
remote: Permission to uuii13524-afk/shaky-shell.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/uuii13524-afk/shaky-shell/': The requested URL returned error: 403
```

ローカルの `git push` は普段通り通るので、GitHub Actions環境固有の権限周りの問題だとは分かったが、`git config` の設定ミスなのか、トークンそのものが悪いのか、切り分けに時間がかかった。

## 環境

- GitHub Actions: `ubuntu-latest` ランナー
- `actions/checkout@v4`
- ワークフロートリガー: `push`（`main`ブランチ）
- 認証: デフォルトの `${{ secrets.GITHUB_TOKEN }}`（自動生成、明示的なPAT未設定）
- リポジトリ: 2023年以降に作成（Actionsのデフォルト権限が「読み取り専用」の世代）

## 試したこと

最初に、`git push` の直前に `git remote -v` を挟んでリモートURLを確認したが、`https://github.com/uuii13524-afk/shaky-shell.git` と表示され、URL自体は正しかった。認証情報の中身が問題だと判断した。

次に、`git config` でuser.name/user.emailを`github-actions[bot]`に設定し直せば直ると思い、以下を追加して再実行した。

```yaml
- name: Configure git
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
```

しかし結果は変わらず、同じ`403`エラーが出た。この時点で、ユーザー名・メールの設定はコミットの著者情報を決めるだけで、push時の認証権限とは無関係だと気づいた。認証まわりを疑って調べ直すことにした。

さらに、`secrets.PAT`という名前で個人アクセストークンを作成しリポジトリのSecretsに登録したが、`actions/checkout`の`token`引数に渡すのを忘れており、checkoutステップは相変わらずデフォルトの`GITHUB_TOKEN`で認証情報をキャッシュしていた。そのため`git push`時にも古い（読み取り専用の）認証情報がそのまま使われ、同じ`Permission denied`で失敗した。

## 原因

GitHub Actionsが自動生成する`GITHUB_TOKEN`の書き込み権限は、2つの場所で二重に制御されている。

1つ目はリポジトリ全体のデフォルト設定（Settings → Actions → General → Workflow permissions）で、2023年2月以降に作成されたリポジトリはここが「Read repository contents permission」（読み取り専用）になっているのがデフォルトである。

2つ目はワークフローYAML内の`permissions:`キーで、ジョブ単位・ワークフロー単位で個別に権限を指定できる。ただし、この`permissions:`キーはリポジトリ全体の設定を「上書き」できるだけであり、リポジトリ全体の設定がそもそも書き込みを許可していない、もしくはOrganizationのポリシーでYAML側からの上書き自体が禁止されている場合は、YAMLに`contents: write`と書いても反映されない。

さらに、`actions/checkout`はデフォルトで`GITHUB_TOKEN`を使って認証情報をローカルのgit設定（`.git/config`の`http.https://github.com/.extraheader`）にキャッシュする。このキャッシュされた認証情報の権限は、checkoutを実行した時点でのトークン権限がそのまま使われるため、後から`permissions:`を変えても手遅れになるケースがある。

## 解決方法

まず、ワークフローYAMLの該当ジョブに書き込み権限を明示する。

```yaml
jobs:
  format:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: npx prettier --write .
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --cached --quiet || git commit -m "chore: auto format"
          git push
```

`permissions:`はジョブ単位で書くと、そのジョブでしか書き込み権限が有効にならないため、他のジョブは読み取り専用のまま保てる。全ジョブで共通なら、ワークフローのトップレベル（`jobs:`より上）に書いても良い。

次に、リポジトリ側の設定を確認する。GitHubのWeb UIで対象リポジトリの Settings → Actions → General を開き、「Workflow permissions」のセクションが「Read repository contents permission」になっていないか確認する。「Read and write permissions」に切り替えると、YAML側の`permissions: contents: write`が正しく反映されるようになる。

```text
Workflow permissions
  ( ) Read repository contents permission
  (•) Read and write permissions
```

この2つ（YAMLの`permissions:`とリポジトリ設定の両方）を揃えたうえで再実行すると、`git push`のログは次のような形になる。

```text
To https://github.com/uuii13524-afk/shaky-shell.git
   a1b2c3d..e4f5g6h  main -> main
```

`403`だったログが、pushの差分ハッシュを表示する成功ログに変わっていれば、権限は正しく通っている。なぜこれで直るかというと、`actions/checkout`が使う`GITHUB_TOKEN`の実効的な権限が「リポジトリのデフォルト設定」と「YAMLの`permissions:`」の両方をANDで満たして初めて書き込み可になる仕組みだからで、片方だけ直しても403が消えなかったのはこのためである。

## ハマったポイント

- `git config user.name/user.email`を直しても直らなかった。これはコミットの著者情報の設定であり、push時の認証（誰の権限で書き込むか）とは別レイヤーの話だった。
- PATを`secrets.PAT`として登録したのに、`actions/checkout`の`with: token:`に渡し忘れていた。checkoutステップに渡さない限り、以降のgit操作はデフォルトの`GITHUB_TOKEN`のまま認証情報がキャッシュされ続ける。
- ワークフローYAMLに`permissions: contents: write`を書いただけで満足してpushしたが、リポジトリ設定側が「Read repository contents permission」のままで、結局403が消えなかった。両方揃える必要があることに気づくまで無駄なコミットを何度も積んでしまった。
- `pull_request`トリガー（フォークからのPR）で同じワークフローを試したところ、`permissions:`をwriteにしても403が消えなかった。これはセキュリティ上の別制約で、フォークからのPRでは`GITHUB_TOKEN`が常に読み取り専用に固定される仕様だった。

## よくある質問

**Q: `pull_request`トリガーのワークフローで`permissions: contents: write`にしても直らないのはなぜですか？**
フォークされたリポジトリからのPull Requestでは、セキュリティ上`GITHUB_TOKEN`が常に読み取り専用に固定され、`permissions:`キーで上書きすることはできない。書き込みが必要な処理は`pull_request_target`トリガーに分離するか、書き込み権限を持つ別ワークフロー（`workflow_run`で連鎖させる方式）に分ける必要がある。

**Q: `GITHUB_TOKEN`ではなく個人アクセストークン（PAT）を使うべきタイミングはいつですか？**
自分のリポジトリへの単純なpushバックであれば`GITHUB_TOKEN`で足りるが、別リポジトリへのpush、Organizationのルールでbotによる直接pushが制限されている場合、あるいはpushしたコミットから別のワークフローを連鎖的にトリガーしたい場合（`GITHUB_TOKEN`によるpushはワークフローの再トリガーを起こさない仕様がある）は、書き込み権限を持つPATまたはGitHub Appのトークンを`secrets`に登録し、`actions/checkout`の`token:`引数に明示的に渡す必要がある。

**Q: `permissions:`はワークフロー全体とジョブ単位のどちらに書くべきですか？**
書き込みが必要なジョブが一部だけなら、ジョブ単位で最小権限にする方が安全である。フォーマットやリリースノート生成など特定のジョブだけがpushを行うなら、そのジョブにだけ`contents: write`を付け、他のジョブはデフォルトの読み取り専用のままにしておく。

## 関連記事

- [GitHub Actionsの基本的な使い方](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使う方法](/posts/github-actions-secrets)
- [GitHub ActionsでDockerを使う方法](/posts/github-actions-docker)
- [gitのリモート操作まとめ](/posts/git-remote-operations)
- [SSH鍵をGitHubに登録する方法](/posts/ssh-key-github)
