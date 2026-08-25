---
title: 'git commitで「gpg failed to sign the data」の原因と解決手順'
date: '2026-08-25'
category: 'Git'
layout: '../../layouts/PostLayout.astro'
description: 'git commitを実行すると「error: gpg failed to sign the data」でコミットが失敗する症状を解説。tmuxやSSH接続の新しいセッションでGPG_TTYが未設定のまま署名しようとすると発生する原因と、GPG_TTYの設定とgpg-agent再起動での解決手順を紹介します。'
ja_tags: ['Git', 'GPG', 'commit署名']
en_tags: ['Git', 'GPG', 'commit signing']
---

## やりたかったこと（または「症状」）

普段からコミットにGPG署名を付けるようにしていて、`~/.gitconfig`で`commit.gpgsign = true`を設定している。ある日、VPS上で新しく開いたtmuxのペインからリポジトリを操作し、いつも通りコミットしようとしたところ失敗した。

```bash
git commit -m "fix: update dependencies"
```

```text
error: gpg failed to sign the data
fatal: failed to write commit object
```

同じ変更内容で何度リトライしても同じエラーになった。直前まで別のSSHセッションでは問題なく署名付きコミットができていたので、リポジトリ側やGPG鍵そのものが壊れたわけではなさそうだと考えた。

```bash
git commit -m "fix: update dependencies"
```

```text
error: gpg failed to sign the data
fatal: failed to write commit object
```

## 環境

- OS: Ubuntu 24.04.4 LTS
- Git: 2.51.0
- GnuPG: 2.4.4
- pinentryプログラム: pinentry-curses
- 接続方法: SSHでVPSにログイン後、`tmux new -s work`で新しいセッションを開いて作業
- GPG鍵: 事前に作成済みのローカル署名用鍵（`user.signingkey`に設定済み）

## 試したこと

まず、Gitのエラーメッセージだけでは原因が特定できなかったので、GPGを直接呼び出して署名だけを単独で試した。

```bash
echo "test" | gpg --clearsign
```

```text
gpg: signing failed: Inappropriate ioctl for device
gpg: [stdin]: clear-sign failed: Inappropriate ioctl for device
```

Gitのエラーとは別に、GPG自体がpinentryを起動できずに失敗していることが分かった。「Inappropriate ioctl for device」は、pinentryがパスフレーズ入力用のプロンプトを出そうとして、対象の端末（tty）を掴めなかった場合によく出るメッセージだった。

そこで、GPGがどの端末をパスフレーズ入力先として認識しているか確認した。

```bash
echo $GPG_TTY
```

```text

```

出力は空だった。以前の別セッションでは`~/.bashrc`で`export GPG_TTY=$(tty)`を実行していたはずだが、今回新しく開いたtmuxペインではそれが反映されていないようだった。実際に`.bashrc`の中身を確認した。

```bash
grep GPG_TTY ~/.bashrc
```

```text
export GPG_TTY=$(tty)
```

設定自体は書かれていた。念のため今のtty名を確認する。

```bash
tty
```

```text
/dev/pts/3
```

`.bashrc`には記述があるのに、現在のシェルで`GPG_TTY`が空になっている。ここで、このtmuxセッションを開いた際に`.bashrc`が正しく読み込まれていない、または読み込まれた後に何らかの理由で`GPG_TTY`が上書きされている可能性を疑った。

## 原因

GPGでコミットに署名する際、パスフレーズの入力を求めるpinentryは「今操作している端末（tty）」に向けてプロンプトを出そうとする。GPGはその宛先を環境変数`GPG_TTY`から判断しており、この値が正しく設定されていないと、pinentryはどの端末に出力すればよいか分からず`Inappropriate ioctl for device`で失敗する。

今回のケースでは、`.bashrc`に`export GPG_TTY=$(tty)`という記述自体は存在していたが、`tmux new`で新しいペインを開いた時点でのシェル初期化のタイミングと、gpg-agentが以前のセッション（別のtty）の情報をまだキャッシュしていたことが重なり、`GPG_TTY`が今のペインの`/dev/pts/3`を正しく指していない状態になっていた。加えて、gpg-agentはバックグラウンドで常駐し続けるため、古いセッション情報を保持したまま新しいtmuxペインからの署名要求を処理しようとしていたことも分かった。つまり、鍵やGitの設定は正しいのに、「pinentryがどの端末に向けて入力を求めればいいか」という情報だけが古くなっていたのが根本原因だった。

## 解決方法

### 1. 現在のシェルでGPG_TTYを明示的に再設定する

```bash
export GPG_TTY=$(tty)
```

### 2. 設定できているか確認する

```bash
echo $GPG_TTY
```

```text
/dev/pts/3
```

今使っているペインのtty名と一致していることを確認した。

### 3. gpg-agentを再起動し、古いセッション情報を破棄する

```bash
gpgconf --kill gpg-agent
```

`gpgconf --kill`はエージェントを安全に終了させるコマンドで、次にGPGを使ったタイミングで新しいエージェントが自動的に起動する。

### 4. 単独でGPG署名だけを再テストする

```bash
echo "test" | gpg --clearsign
```

```text
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512
test
-----BEGIN PGP SIGNATURE-----
...
-----END PGP SIGNATURE-----
```

pinentry-cursesのパスフレーズ入力プロンプトが端末上に正しく表示され、署名が成功した。

### 5. git commitを再実行する

```bash
git commit -m "fix: update dependencies"
```

```text
[main a1c2e3f] fix: update dependencies
 1 file changed, 3 insertions(+), 1 deletion(-)
```

エラーなくコミットできた。

### 6. 恒久対応として.bashrcの読み込みタイミングを見直す

今後同じtmuxペインを開くたびに再発しないよう、`.bashrc`の`export GPG_TTY=$(tty)`をシェル起動時に必ず評価される位置（対話シェル判定ブロックの外に出さない範囲で先頭寄り）に移動し、さらにtmuxの`.tmux.conf`にペイン切り替え時のフック`set-hook -g pane-focus-in 'run-shell "tmux setenv GPG_TTY $(tty)"'`に近い仕組みを検討することにした。

## 動作確認

```bash
git log --show-signature -1
```

```text
gpg: Signature made Tue 25 Aug 2026 10:14:02 AM UTC
gpg: using RSA key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
gpg: Good signature from "Acia <acia@example.com>" [ultimate]
commit a1c2e3f4b5d6...
Author: Acia <acia@example.com>
Date:   Tue Aug 25 10:14:02 2026 +0000

    fix: update dependencies
```

`gpg: Good signature`と表示され、コミットが正しく署名済みであることを確認できた。

## ハマったポイント

- `.bashrc`に`GPG_TTY`の設定を書いていても、新しいtmuxペインやSSHの多重接続では反映タイミングがずれることがある。「設定は書いてあるのに効いていない」場合は、まず`echo $GPG_TTY`と`tty`の出力を突き合わせて実際の値を確認するべきだった
- `gpg-agent`はバックグラウンドで常駐し続けるため、以前のセッションの情報を持ち越すことがある。パスフレーズ入力まわりで原因不明のエラーが出たときは、鍵やGit設定を疑う前に`gpgconf --kill gpg-agent`で一度リセットしてみると切り分けが早い
- Gitの`error: gpg failed to sign the data`だけでは詳細が分からないため、`git commit`を直接デバッグするのではなく、`echo test | gpg --clearsign`のようにGPG単体を切り離してテストした方が原因特定が早かった

## よくある質問

**Q: 毎回`export GPG_TTY=$(tty)`を手打ちしなくて済む方法はありますか？**
シェルの起動ファイル（`.bashrc`や`.zshrc`）に記述しておけば通常は自動で設定される。ただしtmuxやscreenのように複数の疑似端末を使い回す環境では、ペインを切り替えるたびに値がずれることがあるため、tmux側のフック機能で都度更新する運用が確実。

**Q: `gpgconf --kill gpg-agent`を実行すると、キャッシュされていたパスフレーズも消えますか？**
消える。次に署名するタイミングで再度パスフレーズの入力を求められるが、鍵自体が失われるわけではないので安全に実行できる。

**Q: 署名なしで一時的にコミットする方法はありますか？**
`git commit --no-gpg-sign`で一時的に署名を無効化できる。ただしリポジトリ側で署名付きコミットを必須にしている場合は、後から改めて署名し直す必要があるため、根本原因を直す方が結果的に早い。

## 関連記事

- [git commitを取り消す方法まとめ](/posts/git-commit-undo)
- [git remoteの基本操作](/posts/git-remote-operations)
- [SSH鍵をGitHubに登録する手順](/posts/ssh-key-github)
- [Linuxの環境変数の設定方法](/posts/linux-env-variables)
