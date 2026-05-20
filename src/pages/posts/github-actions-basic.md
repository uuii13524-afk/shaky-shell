---
title: 'GitHub Actionsで自動デプロイする基本的な設定方法'
date: '2026-05-20'
category: 'GitHub Actions'
---

## やりたかったこと

GitHubにpushしたら自動でデプロイが走るようにしたかった。
GitHub Actionsを使うとpushをトリガーに様々な処理を自動化できる。

## 環境

- GitHub
- GitHub Actions

## 基本的な仕組み

```
GitHubにpush
↓
GitHub Actionsが起動
↓
.github/workflows/ 内のYAMLファイルを実行
↓
ビルド・テスト・デプロイなどを自動実行
```

## 手順

### 1. ワークフローファイルを作成

プロジェクトルートに以下のフォルダとファイルを作成する。

```
.github/
  workflows/
    deploy.yml
```

### 2. 基本的なワークフローの書き方

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: リポジトリをチェックアウト
        uses: actions/checkout@v4

      - name: Node.jsをセットアップ
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: 依存関係をインストール
        run: npm install

      - name: ビルド
        run: npm run build
```

### 3. GitHubにpushして確認

```
git add .
git commit -m "add github actions"
git push
```

GitHubのリポジトリページ→「Actions」タブで実行状況を確認できる。

## よく使うトリガー

```yaml
# mainブランチへのpush時
on:
  push:
    branches: [main]

# プルリクエスト作成時
on:
  pull_request:
    branches: [main]

# 手動実行
on:
  workflow_dispatch:
```

## ハマったポイント

- `.github/workflows/` のフォルダ名は正確に書く（大文字小文字に注意）
- YAMLはインデントが重要。スペース2つでインデントする
- Actionsタブでログを確認するとエラーの原因がわかる
- シークレット情報は Settings→Secrets に登録して `${{ secrets.変数名 }}` で参照する

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [Cloudflare PagesのGitHub自動デプロイが動かない時の対処法](/posts/cloudflare-pages-deploy-not-working)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [GitのブランチをCLIで作成・切り替える基本コマンド](/posts/git-branch-basics)
