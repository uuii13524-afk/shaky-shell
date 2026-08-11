---
title: 'WSL2でgit pushが「Permission denied (publickey)」になる原因と解決手順（Ubuntu 24.04）'
date: '2026-08-11'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'WSL2のUbuntu環境でgit pushやgit cloneを実行すると「Permission denied (publickey)」で拒否される症状を解説。SSH秘密鍵のパーミッションが原因で認証情報がまるごと無視されるケースの見分け方と、chmodによる解決手順を紹介します。'
ja_tags: ['Git', 'SSH', 'WSL2', 'permission denied']
en_tags: ['Git', 'SSH', 'WSL2', 'permission denied']
---

## やりたかったこと（症状）

Windows 11のPCを新調し、これまでWindows側の`C:\Users\me\.ssh`に置いていた鍵ペアをWSL2のUbuntuにコピーして、既存のGitHubリポジトリで作業を続けようとした。エクスプローラー経由で`.ssh`フォルダを丸ごとzip圧縮し、WSL2側の`~/.ssh`に展開してから、いつも通り`git push`を実行した。

```bash
cd ~/projects/errsolved
git push origin main
```

しかし見慣れないエラーで撥ねられた。

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

念のため単体でSSH接続を試したが、同じく拒否された。

```bash
ssh -T git@github.com
```

```text
git@github.com: Permission denied (publickey).
```

鍵はGitHub側にすでに登録済みのはずで、同じ鍵をWindows側のGit Bashから使っていたときは問題なく`push`できていた。ファイルをコピーしただけで壊れるとは思っていなかったので、原因の切り分けに時間がかかった。

## 環境

- OS: Windows 11 23H2 / WSL2 Ubuntu 24.04.1 LTS
- Git: 2.43.0
- OpenSSH クライアント: 9.6p1
- 鍵の種類: `ed25519`（`id_ed25519` / `id_ed25519.pub`）
- 鍵の移行方法: Windows `.ssh` フォルダをzip圧縮 → WSL2側に展開

## 試したこと

まず「鍵自体がGitHub未登録なのでは」と疑い、公開鍵の中身を確認して、GitHubの `Settings > SSH and GPG keys` に登録済みの鍵と1文字ずつ突き合わせた。完全に一致していたので、鍵の内容自体は問題ないと判断した。

次に、SSH agentに鍵が読み込まれているかを確認した。

```bash
ssh-add -l
```

```text
The agent has no identities.
```

何も登録されていなかったので、明示的に追加を試みた。

```bash
ssh-add ~/.ssh/id_ed25519
```

```text
Identity added: /home/me/.ssh/id_ed25519 (me@example.com)
```

追加自体は成功したように見えたが、再度`ssh -T git@github.com`を実行しても結果は変わらず`Permission denied (publickey)`のままだった。ここで「追加はできているのに使われていない」という不自然さに気づき、`-v`オプションで詳細ログを見ることにした。

```bash
ssh -vT git@github.com
```

出力の中に、見落としていた警告行があった。

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/me/.ssh/id_ed25519' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/me/.ssh/id_ed25519": bad permissions
git@github.com: Permission denied (publickey).
```

OpenSSHが「このファイルは他人からも読めるパーミッションだから安全のため無視する」と明言していた。つまり鍵の中身や登録状況はまったく問題なく、パーミッション設定だけが原因で認証プロセスから鍵が黙って除外されていた。

## 原因

`ls -la`で実際の権限を確認すると、原因がはっきりした。

```bash
ls -la ~/.ssh
```

```text
drwxr-xr-x  2 me me 4096 Aug 11 09:02 .
-rw-r--r--  1 me me  411 Aug 11 09:02 id_ed25519
-rw-r--r--  1 me me  103 Aug 11 09:02 id_ed25519.pub
```

秘密鍵`id_ed25519`が`644`（所有者以外も読み取り可能）、`.ssh`ディレクトリ自体も`755`になっていた。zip展開時にWindows側のACLがLinuxのパーミッションビットに正しく変換されず、標準の`644`権限で書き出されたことが直接の原因だった。

OpenSSHは秘密鍵ファイルが所有者以外から読み取り可能な状態（グループ・その他に読み取り権限がある）だと、盗用リスクを防ぐためにその鍵を認証候補から除外する仕様になっている。エラーにはならず単に「無視」されるため、`ssh-add`は成功して見えるのに実際の認証では使われない、という分かりにくい状態が生まれていた。

## 解決手順

### 1. `.ssh`ディレクトリと鍵ファイルの権限を修正する

秘密鍵は所有者のみ読み書き可能な`600`、公開鍵は`644`、ディレクトリは`700`が標準的な権限。

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### 2. 権限が正しく反映されたか確認する

```bash
ls -la ~/.ssh
```

```text
drwx------  2 me me 4096 Aug 11 09:14 .
-rw-------  1 me me  411 Aug 11 09:14 id_ed25519
-rw-r--r--  1 me me  103 Aug 11 09:14 id_ed25519.pub
```

### 3. SSH agentに鍵を再登録する

一度失敗した状態のagentをそのまま使い続けると混乱するので、鍵を登録し直した。

```bash
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```

```text
256 SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx me@example.com (ED25519)
```

### 4. GitHubへの接続を再確認する

```bash
ssh -T git@github.com
```

```text
Hi myuser! You've successfully authenticated, but GitHub does not provide shell access.
```

`Permission denied`ではなく認証成功メッセージに変わった。

## 動作確認

実際に`git push`を再実行し、正常にリモートへ反映されることを確認した。

```bash
git push origin main
```

```text
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 312 bytes | 312.00 KiB/s, done.
To github.com:myuser/errsolved.git
   a1b2c3d..e4f5g6h  main -> main
```

念のため`ssh -vT git@github.com`のログも再確認し、`bad permissions`の警告が出なくなっていることも確かめた。

## まとめ

- `Permission denied (publickey)`は鍵そのものが間違っている場合だけでなく、秘密鍵のファイルパーミッションが緩い（`644`など所有者以外も読める状態）ためにOpenSSHが鍵を丸ごと無視しているケースがある。
- `ssh-add`が成功して見えても、パーミッション不良の鍵は認証候補から除外されているため、`ssh -T git@github.com`や`git push`が失敗し続ける。原因を切り分けるには`ssh -vT`の詳細ログで`bad permissions`の警告を確認するのが確実。
- 解決は`chmod 700 ~/.ssh`と`chmod 600`（秘密鍵）・`chmod 644`（公開鍵）。特にWindowsとWSL2間でzip展開やエクスプローラー経由の手動コピーで`.ssh`を移行すると、Linux側のパーミッションビットが緩く復元されやすいので、移行直後は必ず`ls -la ~/.ssh`で確認する習慣をつけるとよい。

## よくある質問

**Q: `ssh-add -l`で鍵が表示されるのに、なぜ認証に失敗するのですか？**
`ssh-add`は鍵ファイルの中身が読み込める限り「登録」自体は成功します。しかしOpenSSHクライアントは実際の接続時にファイルパーミッションを再チェックし、所有者以外が読めるパーミッションの鍵は接続直前に候補から除外します。そのため`ssh-add -l`では表示されても、認証には使われません。

**Q: WSL2以外（純粋なLinuxサーバーなど）でも同じ現象は起きますか？**
起きます。原因はWSL2固有ではなく、OpenSSHクライアント共通の仕様です。`scp`や`rsync`でバックアップから`.ssh`ディレクトリを復元した場合や、他のユーザーのホームディレクトリから鍵をコピーした場合にも同様に発生します。

**Q: `chmod`だけで解決しない場合は何を疑うべきですか？**
`.ssh`ディレクトリ自体のパーミッションも見落としがちです。ディレクトリが`755`のままでも警告が出ることがあるため、`chmod 700 ~/.ssh`を鍵ファイルと合わせて必ず実行してください。それでも解決しない場合は、GitHub側に登録されている公開鍵が実際に使おうとしている秘密鍵と対になっているか、`ssh-keygen -y -f ~/.ssh/id_ed25519`で公開鍵を再生成して比較すると切り分けやすくなります。

## 関連記事

- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [git pushでrejectedになった時の対処法](/posts/git-push-rejected-fix)
- [git status で fatal: not a git repository が出た時の対処法](/posts/git-fatal-not-a-git-repository)
- [Linuxのファイルパーミッション（chmod/chown）完全ガイド](/posts/linux-file-permissions)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
