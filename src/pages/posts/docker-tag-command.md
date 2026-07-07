---
title: 'docker tag コマンドの使い方｜イメージにタグを付けてレジストリにpushする方法'
date: '2026-07-07'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Docker', 'docker tag', 'イメージ管理']
description: 'docker tagコマンドでイメージに別名やバージョンタグを付ける方法。Docker Hubやプライベートレジストリへpushする際の命名規則、latestタグの注意点、よくあるエラーを解説。'
---

## ひとことで言うと

```bash
# イメージにタグを付ける
docker tag <元イメージ名>:<タグ> <新しいイメージ名>:<タグ>

# 例: レジストリ用にタグ付けしてpush
docker tag myapp:latest myuser/myapp:1.0.0
docker push myuser/myapp:1.0.0
```

---

## やりたかったこと / 現象

ローカルでビルドしたイメージをDocker HubやプライベートレジストリにPushしようとしたら、`denied: requested access to the resource is denied` と言われてしまった——多くの人がここで `docker tag` の存在に気づきます。

Dockerはイメージ名（正確には「リポジトリ名」）を見てpush先を判断するため、ローカルでビルドした `myapp:latest` のような名前のままでは、レジストリのユーザー名やリポジトリパスが含まれておらずpushできません。`docker tag` を使ってレジストリ向けの名前を付け直す必要があります。

---

## 環境

- Docker: 20.10以降で動作確認
- OS: Linux / macOS / Windows（WSL2）

---

## 解決策

### 1. 基本構文

```bash
docker tag <SOURCE_IMAGE>[:TAG] <TARGET_IMAGE>[:TAG]
```

`docker tag` はイメージを複製するのではなく、既存のイメージID に対して新しい名前（参照）を追加するだけです。ディスク容量は増えません。

### 2. Docker Hub にpushするためのタグ付け

```bash
# 書式: <Docker Hubのユーザー名>/<リポジトリ名>:<タグ>
docker tag myapp:latest myuser/myapp:1.0.0

# pushする
docker push myuser/myapp:1.0.0
```

### 3. プライベートレジストリにタグ付けする場合

```bash
# 書式: <レジストリのホスト名>/<リポジトリ名>:<タグ>
docker tag myapp:latest registry.example.com/myteam/myapp:1.0.0

docker push registry.example.com/myteam/myapp:1.0.0
```

ホスト名を含めることで、Dockerはどのレジストリにpushすべきかを判断します。

### 4. 複数のタグを同じイメージに付ける

```bash
docker tag myapp:latest myuser/myapp:1.0.0
docker tag myapp:latest myuser/myapp:latest
```

バージョン番号のタグと `latest` タグの両方を同じイメージに付けておくと、利用者はバージョン固定と最新版のどちらも選べるようになります。

### 5. イメージIDから直接タグ付けする

```bash
docker images
# IMAGE ID を確認してから
docker tag a1b2c3d4e5f6 myuser/myapp:1.0.0
```

元イメージの名前がわからない場合や `<none>` になっている場合でも、IMAGE ID を指定してタグを付けられます。

### 6. 付けたタグを確認する

```bash
docker images myuser/myapp
```

同じIMAGE IDに対して複数のタグが付いていても、実体のディスク使用量は共有されるため増えません。

---

## よくあるエラーと対処

### `denied: requested access to the resource is denied`

タグにユーザー名・レジストリ名が含まれていないか、ログインしていないことが原因です。

```bash
docker login
docker tag myapp:latest myuser/myapp:1.0.0
docker push myuser/myapp:1.0.0
```

### `Error response from daemon: No such image`

タグ付け元のイメージ名やタグが間違っています。`docker images` で正確な名前とタグを確認してください。

```bash
docker images
```

### `latest` タグを更新したつもりが古いイメージのままpullされる

`latest` は「最新版」を意味する特別な仕組みではなく、単なる文字列のタグです。pull元のキャッシュが残っていると古いイメージのままになることがあるため、`docker pull` 時に明示的にタグを指定するか、`docker pull --no-cache` 相当の対策（イメージの再取得）が必要です。

### タグ名に使える文字のエラー

タグ名には英数字・ピリオド・アンダースコア・ハイフンのみ使用可能です。大文字を含むリポジトリ名はDocker Hubで許可されないため、すべて小文字にしてください。

---

## よくある質問

**Q: `docker tag` はイメージをコピーしますか？**
いいえ。実体は複製されず、同じイメージIDに対する新しい名前（参照）が追加されるだけです。ディスク使用量は増えません。

**Q: タグを付けずに `docker push` するとどうなりますか？**
タグを省略すると自動的に `latest` として扱われます。意図しないタグ上書きを避けるため、明示的にバージョンタグを指定することをおすすめします。

**Q: 間違えて付けたタグを削除するには？**
`docker rmi myuser/myapp:1.0.0` でタグ（参照）だけを削除できます。元イメージ自体は他のタグが残っていれば削除されません。

**Q: バージョン番号はどう付けるのが一般的ですか？**
セマンティックバージョニング（`1.0.0` のような形式）が一般的です。加えて `latest` や `stable` などのエイリアスタグを併用するケースも多いです。

**Q: `docker tag` と `docker commit` の違いは？**
`docker tag` は既存イメージに別名を付けるだけですが、`docker commit` はコンテナの現在の状態から新しいイメージを作成します。用途が異なります。

---

## 関連記事

- [docker ps コマンドの使い方](/posts/docker-ps-command)
- [docker build でイメージをビルドする方法](/posts/docker-build-image)
- [docker image のクリーンアップ方法](/posts/docker-image-cleanup)

## おすすめのVPS／ドメイン／スクール

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
