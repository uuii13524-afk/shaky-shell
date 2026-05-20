---
title: 'GitHub Actionsで自動デプロイする基本的な設定方法'
date: '2026-05-10'
category: 'GitHub Actions'
---

## 基本的な仕組み

```
GitHubにpush → GitHub Actionsが起動 → YAMLファイルを実行
```

## 基本的なワークフロー

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
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install
      - run: npm run build
```

## ハマったポイント

- `.github/workflows/` のフォルダ名は正確に
- YAMLはインデントが重要（スペース2つ）
- Actionsタブでログを確認できる

## 関連記事

- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [GitHub Actionsでスケジュール実行を設定する方法](/posts/github-actions-schedule)
