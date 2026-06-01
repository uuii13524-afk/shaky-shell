---
title: 'Node.jsアプリをPM2で本番環境に常駐させる方法'
date: '2026-05-31'
category: 'Node.js'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Node.js', 'PM2', 'VPS', 'Linux', 'プロセス管理']
en_tags: ['Node.js', 'PM2', 'VPS', 'Linux', 'process management']
description: 'Node.jsアプリをPM2で本番環境に常駐させる手順。インストールから起動・自動起動設定・ログ確認まで、VPSでの実際の手順をまとめた。'
---
## やりたかったこと
VPSで動かしているNode.jsアプリがSSHを切断するたびに終了してしまった。PM2を使ってバックグラウンドで常駐させたかった。

## PM2のインストール

```bash
npm install -g pm2
```

グローバルインストールするので、nvmを使っている場合はバージョンを固定しておく。

## アプリの起動

```bash
pm2 start app.js
# または
pm2 start app.js --name myapp
```

`--name`でプロセス名を指定しておくと後で管理しやすい。

## よく使うコマンド

```bash
# プロセス一覧確認
pm2 list

# ログ確認
pm2 logs
pm2 logs myapp

# 再起動
pm2 restart myapp

# 停止
pm2 stop myapp

# 削除
pm2 delete myapp
```

`pm2 list`でCPU・メモリ使用量も一覧で確認できる。

## サーバー再起動後も自動起動させる

```bash
pm2 startup
```

実行すると以下のようなコマンドが出力されるので、そのままコピーして実行する。

```bash
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

その後、現在の起動設定を保存する。

```bash
pm2 save
```

これでサーバーを再起動してもPM2が自動で立ち上がり、登録済みのアプリも起動する。

## ecosystem.config.jsで設定をまとめる

複数アプリや環境変数が多い場合は設定ファイルにまとめた方が管理しやすかった。

```js
module.exports = {
  apps: [{
    name: 'myapp',
    script: './app.js',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log'
  }]
};
```

```bash
pm2 start ecosystem.config.js
```

## ハマったポイント
- nvmでNode.jsを管理している場合、`pm2 startup`後にnvmのパスが通らなくてアプリが起動しないことがある → `pm2 startup`の出力コマンドにPATHを追加して解決
- `pm2 save`を忘れるとサーバー再起動後に登録が消える
- ログが溜まり続けるので`pm2 install pm2-logrotate`でローテーション設定しておくと良い
- nginxのリバースプロキシと組み合わせる時はPORTの設定を揃えること
- `pm2 startup`は実行ユーザーのホームディレクトリを参照するので、rootとuserで混在しないよう注意

## 関連記事
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [nginxのリバースプロキシ設定（Node.jsアプリをnginxで公開する）](/posts/nginx-reverse-proxy)
- [systemdでサービスを管理する方法（start/stop/enable/status）](/posts/linux-systemd-service)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
