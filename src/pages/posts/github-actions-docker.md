---
title: 'GitHub ActionsでDockerイメージをビルドしてDocker Hubにプッシュする方法'
date: '2026-06-05'
category: 'GitHub Actions'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['GitHub Actions', 'Docker', 'CI/CD', 'Docker Hub', '自動化']
en_tags: ['GitHub Actions', 'Docker', 'CI/CD', 'Docker Hub', 'automation']
description: 'GitHub ActionsでDockerイメージを自動ビルドしてDocker Hubにプッシュする方法。SecretsへのDocker認証情報の登録手順も含めて解説。'
---

## やりたかったこと

コードをpushするたびに自動でDockerイメージをビルドしてDocker Hubにプッシュしたかった。
毎回手動でビルドするのが面倒になってきて、GitHub Actionsで自動化してみた。

## Docker Hubの認証情報をSecretsに登録する

まずDocker Hubのアクセストークンを取得する。
Docker Hub → Account Settings → Security → New Access Token で作成できる。

GitHubのリポジトリの Settings → Secrets and variables → Actions に以下を登録する：

- `DOCKERHUB_USERNAME`：Docker HubのユーザーID
- `DOCKERHUB_TOKEN`：取得したアクセストークン

パスワードではなく必ずAccess Tokenを使う。

## ワークフローファイルを作成する

```bash
mkdir -p .github/workflows
```

`.github/workflows/docker-push.yml` を作成する：

```yaml
name: Docker Build and Push

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
```

## タグにgitのSHAを使う

`latest` だけだとどのコードのイメージかわからなくなる。
commitのSHAも一緒にタグとしてつけておくと追跡しやすい：

```yaml
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
```

## プルリクでビルドだけ確認したい

mainにマージする前にビルドが通るか確認したいことがある。
`push: false` にしておけばDocker Hubへのプッシュなしでビルドだけ実行できる：

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
```

## ハマったポイント

- Docker HubのパスワードではなくAccess Tokenを使わないと認証エラーになる
- `docker/build-push-action` はDockerfileがリポジトリルートにある前提。別の場所にある場合は `context` や `file` オプションで指定する
- `tags` にユーザー名を直書きするとSecretsを変えた時に壊れる。Secretsから読むようにしておく
- GitHub Actionsの無料枠はパブリックリポジトリは無制限、プライベートは月2000分まで

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [Dockerfileの基本的な書き方](/posts/docker-dockerfile-basics)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)
- [Dockerの基本コマンドまとめ（run/stop/rm/ps）](/posts/docker-basic-commands)

## おすすめのVPS／ドメイン／スクール

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
