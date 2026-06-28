---
title: 'Linuxで環境変数を設定する方法（export・.bashrc・永続化）'
date: '2026-06-28'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', '環境変数', 'export', 'bashrc', 'シェル']
description: 'Linuxで環境変数を設定・確認・永続化する方法を解説。exportコマンドの使い方から.bashrcへの書き方、/etc/environmentによるシステム全体への設定まで網羅。'
---

## ひとことで言うと

```bash
# 一時的に設定（現在のセッションのみ）
export MY_VAR="hello"

# 永続化（ログイン後も有効にする）
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc
```

---

## やりたかったこと / 現象

Linuxで環境変数を設定したいが、ターミナルを閉じると消えてしまう。
または、特定のコマンドに必要な環境変数を永続的に反映したい。

---

## 環境

- OS: Ubuntu 22.04 / Debian 12（他のLinuxディストリビューションでも同様）
- シェル: bash / zsh

---

## 解決策

### 1. 現在の環境変数を確認する

```bash
# すべての環境変数を表示
env

# 特定の変数を確認
echo $HOME
echo $PATH
echo $MY_VAR
```

### 2. 一時的に環境変数を設定する（セッション内のみ）

```bash
export MY_VAR="hello"
echo $MY_VAR
# → hello
```

ターミナルを閉じると消える。

### 3. .bashrc に書いて永続化する（ユーザー限定）

```bash
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc
```

`.bashrc` はログインシェルではなく、インタラクティブシェルで毎回読み込まれる。

### 4. .bash_profile / .profile に書く（ログインシェル）

```bash
echo 'export MY_VAR="hello"' >> ~/.bash_profile
source ~/.bash_profile
```

SSH接続時や初回ログイン時に読み込まれる。

### 5. /etc/environment でシステム全体に設定する

```bash
sudo nano /etc/environment
```

ファイルに以下のフォーマットで追記する（`export` は不要）：

```
MY_VAR="hello"
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

再起動または再ログイン後に有効になる。

### 6. 環境変数を削除する

```bash
unset MY_VAR
echo $MY_VAR
# → （空白）
```

### 7. コマンド実行時だけ一時的に設定する

```bash
MY_VAR="hello" node app.js
```

このプロセスのみに有効で、シェルの環境変数には影響しない。

---

## よくあるエラーと対処

### `export: not valid in this context`

```
export: 'MY_VAR=hello world' is not valid in this context
```

**原因:** スペースを含む値をクォートで囲んでいない。  
**対処:**

```bash
export MY_VAR="hello world"
```

### `source: command not found`

`sh` で実行しているとき `source` が使えない。  
**対処:** `.` を使う（同義）

```bash
. ~/.bashrc
```

### 再起動後に環境変数が消える

`.bashrc` に書いたのに消える場合、ログインシェルが `.bash_profile` だけ読んでいる可能性がある。

**対処:** `.bash_profile` から `.bashrc` を呼び出す。

```bash
# ~/.bash_profile に追記
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
```

### PATH が壊れて `ls` や `cd` が使えなくなった

```bash
# 現在のセッションで一時的にPATHを修復
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

その後 `.bashrc` のPATH設定を確認・修正する。

---

## よくある質問

**Q: `export` と代入（`VAR=value`）の違いは何ですか？**  
`VAR=value` は現在のシェルのみ有効で、子プロセスには引き継がれません。`export VAR=value` にすると子プロセス（コマンドやスクリプト）にも環境変数が渡されます。

**Q: zsh を使っているときはどのファイルに書けばいいですか？**  
zsh では `~/.zshrc` に書くと永続化できます。ログインシェルなら `~/.zprofile` または `~/.zlogin` も使えます。

**Q: `env` と `printenv` の違いは何ですか？**  
どちらも環境変数の一覧を表示しますが、`printenv 変数名` で特定の変数だけ表示することもできます。`env` は新しい環境で別のコマンドを実行するためにも使えます。

**Q: .bashrc と .bash_profile どちらに書くのが正しいですか？**  
ターミナルを開くたびに有効にしたい場合は `.bashrc`、SSHログインや初回ログイン時だけでよい場合は `.bash_profile` に書きます。多くの場合 `.bashrc` で十分です。

**Q: システム全体に環境変数を設定するにはどうすればいいですか？**  
`/etc/environment` に書くと全ユーザーに適用されます。`/etc/profile` や `/etc/profile.d/*.sh` も使えますが、`/etc/environment` が最もシンプルです。

**Q: Node.jsやPythonでも同じ環境変数が使えますか？**  
はい。`export` で設定した環境変数は `process.env.MY_VAR`（Node.js）や `os.environ['MY_VAR']`（Python）でアクセスできます。

---

## 関連記事

- [Linuxの基本コマンド一覧](/posts/linux-basic-commands)
- [Linux ファイルのパーミッション設定（chmod・chown）](/posts/linux-file-permissions)
- [Linux systemd サービスの作り方と管理](/posts/linux-systemd-service)
- [WSL2をWindowsにインストールする方法](/posts/wsl2-install-windows)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
