---
title: 'npm installでEACCES権限エラーが出た時の対処法'
date: '2026-07-22'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'さくらのVPSでnpm install -g pm2実行時にEACCES: permission deniedエラーが発生。原因はグローバルprefixがroot所有の/usr配下だったためで、npm config set prefixで自分のホーム配下に変更し解決しました。'
ja_tags: ['Node.js', 'npm', 'EACCES', '権限エラー']
en_tags: ['Node.js', 'npm', 'EACCES', 'permission denied']
---

## やりたかったこと（または「症状」）

新しく借りたVPSにNodeSourceのスクリプトでNode.jsを入れ、プロセス管理用に `pm2` をグローバルインストールしようとした。`npm install -g pm2` を叩くと、インストール自体は始まらずいきなり赤い文字でエラーが出た。

```text
npm error code EACCES
npm error syscall mkdir
npm error path /usr/lib/node_modules/pm2
npm error errno -13
npm error Error: EACCES: permission denied, mkdir '/usr/lib/node_modules/pm2'
npm error [Error: EACCES: permission denied, mkdir '/usr/lib/node_modules/pm2'] {
npm error   errno: -13,
npm error   code: 'EACCES',
npm error   syscall: 'mkdir',
npm error   path: '/usr/lib/node_modules/pm2'
npm error }
npm error
npm error The operation was rejected by your operating system.
npm error It's possible that the file was already in use (by a text editor or antivirus),
npm error or that you lack permissions to access it.
npm error
npm error If you believe this might be a permission issue, please double-check the
npm error permissions of the file and its containing directories, or try running
npm error the command again as root/Administrator.
npm error A complete log of this run can be found in: /home/user/.npm/_logs/2026-07-22T02_14_08_211Z-debug-0.log
```

ローカルのMacでは同じコマンドが何の問題もなく通っていたので、なぜVPS側だけ弾かれるのか最初は見当がつかなかった。

## 環境

- OS: Ubuntu 22.04.4 LTS（さくらのVPS）
- Node.js: v20.11.1（NodeSourceのsetup_20.xスクリプト経由でapt install）
- npm: 10.2.4
- ログインユーザー: deploy（sudo権限あり、root本人ではない）

## 試したこと

エラーメッセージの `mkdir '/usr/lib/node_modules/pm2'` という部分だけを見て、単純にディレクトリのパーミッションを緩めれば直ると考え、まず `chmod` で `/usr/lib/node_modules` に書き込み権限を足そうとした。

```bash
chmod -R 777 /usr/lib/node_modules
```

```text
chmod: changing permissions of '/usr/lib/node_modules': Operation not permitted
```

`chmod` 自体が `Operation not permitted` で弾かれた。`/usr/lib/node_modules` の所有者がrootで、`deploy` ユーザーには権限を変更する権限すらなかったためだった。sudoを付ければ通ることは分かったが、毎回 `sudo npm install -g` するのは事故のもとだと感じ、根本的な原因を調べ直すことにした。

## 原因

NodeSourceのセットアップスクリプトやディストリのパッケージマネージャ（apt）でNode.jsを入れると、npmのグローバルインストール先（`prefix`）が `/usr/lib/node_modules`（実行ファイルは `/usr/bin` 配下）というOS標準のシステムディレクトリに設定される。このディレクトリはroot以外への書き込みが許可されていないため、一般ユーザーが `npm install -g` を実行するとファイル作成の時点で `EACCES` になる。

`sudo npm install -g` を付ければエラーは消えるが、それはroot権限でnpmを実行して無理やり書き込んでいるだけで、原因である「グローバルインストール先が一般ユーザーの書き込み範囲外にある」こと自体は解決していない。

## 解決方法

### 1. 現在のprefixを確認する

```bash
npm config get prefix
```

```text
/usr
```

`/usr` 配下はシステム管理者向けの領域で、一般ユーザーの書き込み対象外になっているのが分かる。

### 2. ユーザー専用のグローバルインストール先を作る

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
```

`npm config set prefix` で、以降のグローバルインストール先を自分のホームディレクトリ配下に変更する。ここは自分が所有者なので、sudoなしで書き込める。

### 3. PATHにグローバルインストール先のbinを追加する

```bash
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

```text
(何も出力されない。sourceが成功すれば設定が即座に反映される)
```

`~/.npm-global/bin` にインストールされる実行ファイル（`pm2` コマンドなど）にPATHを通さないと、インストールはできてもコマンドが見つからない状態になる。

### 4. sudoなしで再インストールする

```bash
npm install -g pm2
```

```text
added 39 packages in 4s

7 packages are looking for funding
  run `npm fund` for details
```

```bash
which pm2
```

```text
/home/deploy/.npm-global/bin/pm2
```

`sudo` を使わずにインストールが完了し、`which pm2` で `~/.npm-global/bin/pm2` が見つかることも確認できた。以後 `npm install -g` は自分のホームディレクトリ配下に書き込むだけなので、`EACCES` は発生しない。

## ハマったポイント

- `chmod -R 777` で強引に権限を変えようとしたら、`chmod` コマンド自体が `Operation not permitted` で拒否された。所有者がrootのディレクトリは、一般ユーザーは中身どころか権限設定自体を変更できない
- `sudo npm install -g` で一度は解決したように見えたが、後日 `npm install -g` を叩くたびに毎回sudoパスワードを求められるようになり、CI用のデプロイスクリプトに組み込めなかった。sudoは対症療法でしかなく、prefix変更が必要だった
- `npm config set prefix` を実行した直後に `pm2 --version` を叩いたら `command not found` になった。設定変更はその場で反映されるが、シェルのPATHは `source ~/.bashrc` するか新しいターミナルを開くまで更新されないことを忘れていた
- 同じVPS上で以前 `sudo npm install -g` していたパッケージ（`/usr/lib/node_modules` 配下）は、prefix変更後の `npm list -g` には表示されなくなった。古い環境と新しい環境でグローバルパッケージの置き場所が分かれるため、移行時は入れ直しが必要になる

## よくある質問

**Q: `sudo npm install -g` を使い続けるのはダメですか？**
動作はするが、root所有のファイルが増えていき、後から一般ユーザー権限でアップデートやアンインストールをしようとした時に再び `EACCES` が起きる原因になる。CI環境ではsudo自体が使えないことも多く、prefix変更かnvmの利用に切り替えるのが安全。

**Q: nvmを使っていても同じエラーは起きますか？**
基本的に起きない。nvmは各Node.jsバージョンをホームディレクトリ配下（`~/.nvm/versions/node/...`）にインストールするため、グローバルインストール先も最初から自分の所有物になる。新規にサーバーを構築するなら、apt経由のNode.jsではなくnvm導入を検討するとこの問題自体を避けられる。

```bash
nvm install 20
nvm use 20
npm install -g pm2
```

**Q: prefixを変更したら既存のグローバルパッケージはどうなりますか？**
自動では移行されない。`npm list -g --depth=0` で変更前のprefix配下にあったパッケージ名を確認し、prefix変更後に同じコマンドで入れ直す必要がある。

```bash
npm list -g --depth=0
```

## 関連記事

- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [package.jsonのscriptsを活用して作業を効率化する方法](/posts/npm-package-json-scripts)
- [Linuxで Permission denied が出た時の対処法](/posts/linux-permission-denied)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
