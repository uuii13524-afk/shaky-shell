---
title: 'git push/cloneで "Permission denied (publickey)" が出た時の対処法'
date: '2026-07-28'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git clone・git pull・git pushをSSH経由で実行した際に出る git@github.com: Permission denied (publickey) の原因と直し方を解説。ssh-agentへの鍵登録や複数鍵の切り分け方も紹介します。'
ja_tags: ['Git', 'GitHub', 'SSH', 'Permission denied', 'publickey']
en_tags: ['Git', 'GitHub', 'SSH', 'Permission denied', 'publickey']
---

## やりたかったこと（または「症状」）

新しいノートPCをセットアップし、いくつかのリポジトリをまずHTTPSでクローンして使っていた。そのうちの1つを、毎回トークンを入力しなくて済むようにSSH経由のリモートへ切り替えたところ、直後の `git push` が認証で弾かれた。

```text
$ git push origin main
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

## 環境

- OS: Ubuntu 24.04
- Git: 2.43.0
- SSHクライアント: OpenSSH_9.6p1
- リモート: `git@github.com:example/myrepo.git`

## 試したこと

最初はこのマシン用の鍵がGitHub側にまだ登録されていないのだろうと考え、SSH側が実際に何を保持しているか確認した。

```bash
ssh-add -l
```

```text
The agent has no identities.
```

エージェントは空だった。以前のプロジェクトで作ったSSH鍵がディスク上には残っていたので、直接確認してみた。

```bash
ls -la ~/.ssh
```

```text
-rw-------  1 acia acia  411 Jul 28 09:02 id_ed25519
-rw-r--r--  1 acia acia   99 Jul 28 09:02 id_ed25519.pub
```

鍵ファイル自体は存在していたが、`ssh-add -l` は依然として何も表示しない。つまりエージェントが鍵を保持しておらず、認証時にGitがその鍵を提示できていなかった。

## 原因

`git@github.com: Permission denied (publickey)` は、SSHのハンドシェイク自体は成立したものの、提示された鍵がどれもそのGitHubアカウントに受理されなかったことを意味する。原因として多いのは次の3パターン。

1. **鍵がエージェントに読み込まれていない。** `~/.ssh` に鍵ファイルがあるだけでは自動的には使われず、起動中の `ssh-agent` が保持しているか、`ssh` に明示的に指定してやる必要がある。
2. **公開鍵がGitHubアカウントに登録されていない。** `.pub` ファイルの中身を、リポジトリへのアクセス権を持つGitHubアカウント側の「SSH and GPG keys」に登録しておく必要がある。
3. **複数の鍵がある環境で、意図しない鍵が提示されている。** マシン上に複数の鍵ペアがあると、SSHが順番を誤ったり、どこにも登録されていない鍵をデフォルトで使おうとしたりして、GitHub側がすべての提示を拒否する。

## 解決方法

### 1. GitHub側の権限問題ではなく、SSH/鍵の問題であることを切り分ける

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

正常な状態であれば `Hi <username>! You've successfully authenticated...` と返ってくるので、ここで `Permission denied` になる時点で、Gitを経由するより前のSSH認証自体に問題があると分かる。

### 2. エージェントを起動して鍵を追加する

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

```text
Agent pid 4821
Identity added: /home/acia/.ssh/id_ed25519 (acia@laptop)
```

```bash
ssh-add -l
```

```text
256 SHA256:9fKq...redacted... acia@laptop (ED25519)
```

### 3. 対応する公開鍵がGitHubに登録されているか確認する

```bash
cat ~/.ssh/id_ed25519.pub
```

`ssh-ed25519` で始まりコメントで終わる出力全体をコピーし、GitHub → Settings → SSH and GPG keys → New SSH key に登録する。もしその鍵がリポジトリへのアクセス権を持つのとは別のGitHubアカウントに登録されていた場合も、症状は同じ `Permission denied` になるため、鍵がどのアカウントに登録されているかを確認する。

### 4. 再テストして再実行する

```bash
ssh -T git@github.com
```

```text
Hi acia! You've successfully authenticated, but GitHub does not provide shell access.
```

```bash
git push origin main
```

```text
Enumerating objects: 5, done.
...
To github.com:example/myrepo.git
   a1b2c3d..e4f5g6h  main -> main
```

`ssh -T` が "successfully authenticated" を返すようになれば、`git push`・`git pull`・`git clone` もSSH経由で同様に通るようになる。

### 5. 複数の鍵を使い分けている場合はホストごとに固定する

個人用と仕事用など複数の鍵がある場合、SSHの自動判定に任せず `~/.ssh/config` で明示的に紐付ける。

```text
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

`IdentitiesOnly yes` を指定すると、エージェントが保持している鍵をすべて試すのではなく、ここで指定した鍵だけを使うようになるため、提示回数が多すぎてGitHub側に拒否されるといった事態を避けられる。

## ハマったポイント

- `ssh-add` はそのエージェントセッション中だけ鍵を保持する。再起動後は `ssh-add -l` が再び "no identities" に戻ることが多い（デスクトップ環境では自動起動されていることが多いが、まっさらなサーバー環境では自動化されていないことが多い）。
- `~/.ssh/id_ed25519` のパーミッションが `600` より緩いと、SSHは明確なエラーを出さずに黙って鍵の使用を拒否する。`chmod 600 ~/.ssh/id_ed25519` で解消できる。
- 鍵を間違ったGitHubアカウント（仕事用アカウントと個人用アカウントの取り違えなど）に登録してしまった場合も、まったく同じ `Permission denied (publickey)` になる。「アカウント違い」を示す専用のエラーは出ない。

## よくある質問

**Q: リモートをHTTPSに戻せば回避できますか？**
できます。`git remote set-url origin https://github.com/example/myrepo.git` でSSH鍵の設定自体を回避できますが、代わりにpushのたびにトークンまたはcredential helperによる認証が必要になります。

**Q: `ssh -T git@github.com` は成功するのに `git push` だけ失敗するのはなぜですか？**
その鍵で認証自体は通っていても、該当リポジトリへのpush権限がない（別アカウントに登録されている、または読み取り専用のdeploy keyとして登録されている）ケースが多いです。その鍵がどのアカウントに属し、write権限を持っているか確認してください。

**Q: SSHが実際にどの鍵を提示しているか確認する方法はありますか？**
`ssh -vT git@github.com` を実行し、詳細出力中の `Offering public key` の行を見ると、どの鍵ファイルが試され、GitHubに受理されたか拒否されたかが分かります。

## 関連記事

- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github/)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix/)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push/)
- [Gitのリモート操作: add・remove・set-url](/posts/git-remote-operations/)
- [git status で fatal: not a git repository が出た時の対処法](/posts/git-fatal-not-a-git-repository/)
