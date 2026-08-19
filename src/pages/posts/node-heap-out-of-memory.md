---
title: 'Node.jsでheap out of memoryが出た時の対処法'
date: '2026-07-21'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
description: 'ConoHaのメモリ1GB VPSでnpm run build実行時にJavaScript heap out of memoryが発生。原因はswap未設定による物理メモリ不足で、2GBのswapfile作成とNODE_OPTIONS=--max-old-space-size=1536設定で解決しました。'
ja_tags: ['Node.js', 'heap out of memory', 'メモリ不足', 'VPS']
en_tags: ['Node.js', 'heap out of memory', 'memory', 'VPS']
---

## やりたかったこと（または「症状」）

契約している格安VPS（メモリ1GBプラン）にNext.jsのプロジェクトを持ち込み、`npm run build`でプロダクションビルドを試した。ローカルのMacでは3分もかからず終わるビルドが、VPS上ではしばらく進捗が止まったように見えたあと、次のエラーを吐いて強制終了した。

```text
<--- Last few GCs --->
[12345:0x55f8e2a1b000]    45231 ms: Mark-sweep 987.3 (1024.0) -> 980.1 (1024.0) MB, 1245.6 / 0.0 ms  (average mu = 0.123, current mu = 0.045) allocation failure; scavenge might not succeed

<--- JS stacktrace --->

FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
 1: 0xb01110 node::Abort() [node]
 2: 0xa1b8f4 node::OOMErrorHandler(char const*, v8::OOMDetails const&) [node]
 3: 0xcf5a20 v8::Utils::ReportOOMFailure(v8::internal::Isolate*, char const*, bool) [node]
Aborted (core dumped)
```

ローカルとVPSで同じNode.jsのバージョン、同じ`package-lock.json`を使っていたので、最初はビルド対象のコード側に何か問題があるのではないかと疑った。

## 環境

- OS: Ubuntu 22.04.4 LTS（ConoHa VPS、メモリ1GBプラン）
- Node.js: v20.11.1
- npm: 10.2.4
- フレームワーク: Next.js 14.1.0
- スワップ: 未設定（インスタンス作成直後のデフォルト状態）

## 試したこと

まず疑ったのは依存関係の破損だった。`node_modules`と`package-lock.json`を削除し、`npm install`からやり直して再度ビルドを実行した。

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

インストール自体は問題なく完了したが、ビルドは同じ箇所（`Collecting page data`のフェーズ）で同じ`JavaScript heap out of memory`エラーを再現した。依存関係の破損が原因ではなく、ビルドプロセスが使えるメモリ量そのものが不足していると分かった。

次に`free -h`で空きメモリを確認した。

```bash
free -h
```

```text
               total        used        free      shared  buff/cache   available
Mem:           973Mi       210Mi        98Mi        1.0Mi       664Mi        620Mi
Swap:             0B          0B          0B
```

物理メモリが1GB弱しかなく、スワップも0Bだった。Next.jsのビルドはページデータの収集時に複数のNode.jsプロセスを並列に立ち上げるため、物理メモリを使い切った時点でOSが新たなメモリを確保できず、ビルドプロセスがクラッシュしていたと分かった。

## 原因

Node.jsが内部で使うV8エンジンには、ガベージコレクション対象となる「old space」ヒープにデフォルトの上限がある。この上限はNode.jsのバージョンやシステムの物理メモリ量から自動的に決まり、64bit環境では2GB前後になることが多い。ヒープ使用量がこの上限に近づくと、V8はガベージコレクション（mark-compact）を繰り返して未使用領域の回収を試みるが、回収してもすぐに埋まってしまう状態（Ineffective mark-compacts）になると、これ以上ヒープを増やせないと判断してプロセスを異常終了させる。今回のケースでは、V8のヒープ上限そのものに達する前に、物理メモリ1GBというOS側の制約に到達していた。スワップが0Bだったため、物理メモリを使い切った瞬間にLinuxカーネルがメモリ確保に失敗し、Node.jsプロセスがOOM（Out Of Memory）状態に陥っていた。

## 解決方法

### 1. スワップ領域を作成する

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

```bash
free -h
```

```text
               total        used        free      shared  buff/cache   available
Mem:           973Mi       215Mi        90Mi        1.0Mi       667Mi        615Mi
Swap:          2.0Gi          0B       2.0Gi
```

物理メモリが足りなくなった際、OSがディスク上のスワップ領域を仮想的なメモリとして使えるようになるため、ビルドプロセスが即座にOOM Killerの対象にならずに済む。

### 2. 再起動後もスワップを有効にする

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

`swapon`コマンドだけでは再起動時にスワップが無効化されてしまう。`/etc/fstab`に登録しておくことで、次回起動時も自動的にマウントされるようになる。

### 3. NODE_OPTIONSでV8のヒープ上限を明示する

```bash
export NODE_OPTIONS="--max-old-space-size=1536"
npm run build
```

```text
   ▲ Next.js 14.1.0

   Creating an optimized production build ...
 ✓ Compiled successfully
 ✓ Collecting page data
 ✓ Generating static pages (12/12)
```

`--max-old-space-size`はV8が使うヒープの上限をMB単位で指定するオプションで、スワップを加えた実メモリの範囲内に収まる値を設定することで、際限のないメモリ確保によるOOM Killerでの強制終了を避けやすくなる。

## ハマったポイント

- swapfileを作成した直後は`free -h`で反映されていたが、別作業でVPSを再起動したら`Swap: 0B`に戻っていた。`/etc/fstab`への追記を忘れていたのが原因だった
- `--max-old-space-size`を4096（4GB）のように実メモリを大きく超える値に設定したところ、ビルドはしばらく進んだが最終的に`dmesg`に`Out of memory: Killed process`のログが残り、プロセスがOOM Killerに強制終了された。ヒープ上限を上げても物理メモリとスワップの合計を超えることはできない
- Dockerコンテナ内でビルドしていた際は、ホスト側にスワップを追加してもコンテナの`docker run --memory`の制限が優先され、同じエラーが再発した。コンテナ側のメモリ上限も合わせて見直す必要があった
- `npm run build`を`&`でバックグラウンド実行していたところ、OOM Killerに殺されたプロセスの終了状況が分かりづらく、原因特定に時間がかかった。フォアグラウンドで実行してエラー出力を直接確認すべきだった

## よくある質問

**Q: Node.jsのheap out of memoryエラーを直すには最低どれくらいのメモリが必要ですか？**
プロジェクトの規模によるが、Next.jsやNuxtなど中規模のフロントエンドプロジェクトのビルドであれば、物理メモリとスワップを合わせて2GB以上を目安にすると安定しやすい。`free -h`で現在の合計メモリを確認し、不足していればスワップを追加するか、VPSのメモリプラン自体を見直すことを検討する。

**Q: Dockerコンテナ内でだけnode heap out of memoryが出るのはなぜですか？**
Dockerコンテナは`--memory`オプションや`docker-compose.yml`の`mem_limit`で、ホストとは別にメモリ上限を持てる。ホスト側にどれだけ空きメモリがあっても、コンテナ側の上限に達すればコンテナ内のNode.jsプロセスはOOM Killerに殺される。`docker inspect コンテナ名 | grep -i memory`で現在の上限を確認できる。

**Q: swapを使うとディスクI/Oで遅くなりませんか？**
スワップは物理メモリよりアクセス速度が大幅に遅いため、常時大量のスワップが発生する状態は避けたい。今回のようにビルド時などメモリ使用量が一時的に跳ね上がる場面の保険として使う分には実用上問題になりにくいが、恒常的にスワップを使い続けている場合は`vmstat 1`で発生状況を確認し、根本的にメモリを増設した方がよい。

## 関連記事

- [Linuxでswap領域を作成・設定する方法](/posts/linux-swap-setup)
- [VPSにDockerをインストールしてWebサーバーを構築する方法](/posts/vps-docker-setup)
- [npmのキャッシュをクリアする方法](/posts/npm-cache-clear)
- [nvmでNode.jsのバージョンを管理する方法](/posts/node-version-management-nvm)
- [docker statsでコンテナのリソース使用状況を確認する方法](/posts/docker-stats-command)
