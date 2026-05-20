---
title: 'GitHub ActionsでSecretsを使って秘密情報を管理する方法'
date: '2026-05-20'
category: 'GitHub Actions'
---

## やりたかったこと

GitHub ActionsのワークフローでAPIキーなどの秘密情報を安全に使いたかった。
コードに直接書くのは危険なのでSecretsを使う。

## 環境

- GitHub Actions

## Secretsの設定手順

### 1. GitHubでSecretsを登録

1. GitHubのリポジトリページを開く
2. 「Settings」→「Secrets and variables」→「Actions」
3. 「New repository secret」をクリック
4. Nameに変数名、Secretに値を入力して「Add secret」

### 2. ワークフローから参照する

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: デプロイ
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          echo "APIキーを使った処理"
```

## よく使うSecrets活用パターン

### Cloudflare PagesへのデプロイにAPIトークンを使う

```yaml
- name: Cloudflareにデプロイ
  uses: cloudflare/pages-action@v1
  with:
    apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    projectName: my-project
    directory: dist
```

## ハマったポイント

- Secretsの値はログに表示されないようにマスクされる
- Secretsは一度登録すると値を確認できない（上書きのみ可能）
- フォークされたリポジトリからのPRではSecretsは使えない
- 変数名は大文字とアンダースコアで書くのが慣例

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
