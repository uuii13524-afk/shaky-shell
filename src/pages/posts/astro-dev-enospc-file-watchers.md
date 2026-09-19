---
title: 'Astro devサーバーが「ENOSPC: System limit for number of file watchers reached」で起動直後に落ちる原因と解決手順'
date: '2026-09-19'
category: 'Astro'
layout: '../../layouts/PostLayout.astro'
description: 'VPS上でastro devを実行すると、起動直後にENOSPC: System limit for number of file watchers reachedで落ちる症状を解説。fs.inotify.max_user_watchesの上限が原因で、sysctlで恒久的に引き上げるまでの手順を実際のエラーログ付きで紹介します。'
ja_tags: ['Astro', 'ENOSPC', 'inotify', 'Vite', 'VPS']
en_tags: ['Astro', 'ENOSPC', 'inotify', 'Vite', 'VPS']
---

## やりたかったこと（症状）

このブログ（Astro製）をローカルではなく検証用のVPS上でもビルド・確認できるようにしたくて、SSHでログインしたあとに普通に開発サーバーを起動しようとした。

```bash
cd shaky-shell
npm install
npm run dev -- --host 127.0.0.1 --port 4321
```

`npm install`は271パッケージが問題なく入り、`npm run dev`も一見起動するように見えた。`[vite] connected.`まで出力されたのでブラウザで確認しようとした矢先、数秒後に未処理例外でプロセスごと落ちた。

```text
> shaky-shell@0.0.1 dev
> astro dev --host 127.0.0.1 --port 4321

▶ Astro collects anonymous usage data.
  This information helps us improve Astro.
  Run "astro telemetry disable" to opt-out.
  https://astro.build/telemetry

[vite] connected.
node:internal/fs/watchers:254
    const error = new UVException({
                  ^

Error: ENOSPC: System limit for number of file watchers reached, watch '/home/user/shaky-shell/src/pages/en/docker-stats-command.md'
    at FSWatcher.<computed> (node:internal/fs/watchers:254:19)
    at Object.watch (node:fs:2554:36)
    at createFsWatchInstance (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:12958:16)
    at setFsWatchListener (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13000:14)
    at NodeFsHandler$1._watchWithNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13114:20)
    at NodeFsHandler$1._handleFile (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13158:24)
    at NodeFsHandler$1._addToNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13332:26)
Emitted 'error' event on FSWatcher instance at:
    at FSWatcher._handleError (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:14133:148)
    at NodeFsHandler$1._addToNodeFs (file:///home/user/shaky-shell/node_modules/vite/dist/node/chunks/config.js:13337:18) {
  errno: -28,
  syscall: 'watch',
  code: 'ENOSPC',
  path: '/home/user/shaky-shell/src/pages/en/docker-stats-command.md',
  filename: '/home/user/shaky-shell/src/pages/en/docker-stats-command.md'
}

Node.js v22.22.2
```

止まったファイルが毎回`src/pages/en/docker-stats-command.md`とは限らず、実行するたびに違うファイルで落ちる。最初はこのMarkdownファイル自体が壊れているのかと思い、中身を見直したが特に異常はなかった。

## 環境

- OS: Ubuntu（VPS上のコンテナ環境、rootで作業）
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: v6.3.5（`astro dev`内部でViteのファイル監視を使用）
- プロジェクト: `src/pages/posts/`・`src/pages/en/`にそれぞれ127本以上のMarkdownファイルを持つブログ

## 試したこと

まず疑ったのは`npm install`の失敗やパッケージの破損だった。`node_modules`を消して入れ直したが、症状は変わらなかった。

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

結果は同じで、数秒後にまた`ENOSPC`で落ちた。落ちる対象ファイルがランダムに見えたことから、特定ファイルの問題ではなく「監視できるファイル数そのものの上限」を疑い始めた。エラーメッセージに`ENOSPC`（No space left on device）とあるが、`df -h`で確認してもディスク容量にはまったく余裕があった。

```bash
df -h /
```

```text
Filesystem      Size  Used Avail Use% Mounted on
overlay          40G   12G   28G  30% /
```

ディスクは空いているのに`ENOSPC`が出るのは、ディスク容量ではなく「Linuxがファイルの変更を監視するための仕組み（inotify）が使える上限に達している」ことを示すサインだと知り、`fs.inotify.max_user_watches`を確認した。

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
100
```

このVPSでは、この値が`100`にしか設定されていなかった。

## 原因

Astroの開発サーバー（`astro dev`）は内部でViteを使っており、Viteはソースファイルを変更検知するために、対象ディレクトリ配下のファイルひとつひとつに対してLinuxの`inotify`という仕組みで監視（watch）を張る。このブログは`src/pages/posts/`と`src/pages/en/`に127本以上のMarkdownファイルがあり、それ以外のコンポーネントやレイアウト、`node_modules`内の一部ファイルも合わせると、監視対象は数百〜数千に及ぶ。

一方、Linuxカーネルには「1ユーザーが同時に保持できるinotify watchの数」に上限があり、それが`fs.inotify.max_user_watches`というカーネルパラメータで管理されている。多くのディストリビューションのデフォルト値は8192前後だが、今回使っていたVPSのコンテナ環境ではこの値が`100`と極端に低く設定されていた。監視対象のファイル数がこの上限を超えた瞬間に、Viteのファイルウォッチャーが`fs.watch()`の呼び出しに失敗し、`ENOSPC: System limit for number of file watchers reached`が発生してNode.jsプロセスごと未処理例外で落ちる。

エラーメッセージの`ENOSPC`（Error No Space）という名前と、実際にはディスク容量とは無関係という点が非常に紛らわしく、最初に`df -h`で「容量は足りている」と分かってから原因の見当を外に広げるまでに時間がかかった。`ENOSPC`は本来「デバイスに空きがない」ことを示すエラーコードだが、inotifyのwatch上限に達した場合にもLinuxカーネルは同じ`ENOSPC`をシステムコールの戻り値として返す。ディスク容量のエラーだけではないというのが今回の一次情報としての発見だった。

## 解決手順

### 1. 現在のinotify上限を確認する

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
100
```

想定より大幅に低いことを確認した。

### 2. sysctlで一時的に上限を引き上げる

まず即座に動作確認できるよう、`sysctl`で一時的に値を上げた（再起動すると元に戻る）。

```bash
sudo sysctl fs.inotify.max_user_watches=524288
```

```text
fs.inotify.max_user_watches = 524288
```

### 3. 開発サーバーを再度起動して確認する

```bash
npm run dev -- --host 127.0.0.1 --port 4321
```

```text
> shaky-shell@0.0.1 dev
> astro dev --host 127.0.0.1 --port 4321

[vite] connected.
00:09:38 [types] Generated 0ms
 astro  v6.3.5 ready in 1451 ms
┃ Local    http://127.0.0.1:4321/
00:09:38 watching for file changes...
```

今度は`ENOSPC`で落ちることなく、`watching for file changes...`まで到達して起動状態を維持できた。

### 4. 再起動後も上限が保たれるよう恒久化する

`sysctl`コマンドでの変更はOS再起動でリセットされるため、`/etc/sysctl.d/`配下に設定ファイルを追加して恒久化した。

```bash
echo "fs.inotify.max_user_watches=524288" | sudo tee /etc/sysctl.d/99-inotify-watches.conf
sudo sysctl -p /etc/sysctl.d/99-inotify-watches.conf
```

```text
fs.inotify.max_user_watches=524288
fs.inotify.max_user_watches = 524288
```

再起動後もこのファイルが読み込まれるため、次回以降は毎回`sysctl`を手打ちしなくてよくなった。

## 動作確認

設定ファイルを追加したあと、実際に一度VPSを再起動し、`sysctl`コマンドを打たずに値が保持されているかを確認した。

```bash
cat /proc/sys/fs/inotify/max_user_watches
```

```text
524288
```

再起動をまたいで値が維持されていることを確認できた。続けて開発サーバーを起動し、数分間放置してファイル編集を行っても`ENOSPC`が再発しないことも確認した。

```bash
sysctl fs.inotify.max_user_watches
```

```text
fs.inotify.max_user_watches = 524288
```

## まとめ

- `astro dev`（内部のVite）は監視対象のファイルごとにLinuxのinotify watchを消費する。プロジェクトのファイル数が多いほど必要なwatch数も増える。
- `ENOSPC`という名前からディスク容量不足を疑いがちだが、`df -h`で容量に余裕があるのにこのエラーが出た場合は、`fs.inotify.max_user_watches`のinotify watch上限に達している可能性が高い。`cat /proc/sys/fs/inotify/max_user_watches`で現在値を確認するのが切り分けの第一歩。
- `sudo sysctl fs.inotify.max_user_watches=524288`で即座に値を上げられるが、再起動でリセットされるため、`/etc/sysctl.d/`に設定ファイルを追加して恒久化するところまでがセットの対応になる。

## よくある質問

**Q: `524288`という数値に根拠はありますか？**
Vue CLIやVS Code、JetBrains系IDEなど、多くの開発ツールの公式ドキュメントで推奨されている値で、多くのLinuxディストリビューションで安全に設定できる上限として広く使われている。プロジェクトの規模によってはもっと小さい値（例えば65536）でも十分な場合がある。

**Q: DockerコンテナやWSL2でも同じ設定が必要ですか？**
コンテナ・WSL2はホストのカーネルパラメータを共有していることが多く、その場合はホスト側（VPS本体やWindows側のWSL設定）で`fs.inotify.max_user_watches`を上げる必要がある。コンテナ内部だけで`sysctl`を実行しても、権限やnamespaceの設定次第では反映されないことがある。

**Q: `max_user_watches`を上げすぎるとメモリを消費しますか？**
inotify watch 1つあたりのメモリ消費はごく小さい（数百バイト程度）ため、`524288`程度まで引き上げても通常のVPSで問題になることはほとんどない。ただし極端に大きい値を設定する必要はなく、プロジェクト規模に見合った値で十分。

## 関連記事

- [Astroで新しいページを追加する方法](/posts/astro-add-page)
- [AstroプロジェクトをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
- [nvmでNode.jsのバージョンを管理する方法](/posts/node-version-management-nvm)
- [VPSにDockerをセットアップする手順](/posts/vps-docker-setup)
- [Linuxでswap領域を設定する方法](/posts/linux-swap-setup)
