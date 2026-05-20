---
title: 'GitHub ActionsでSecretsを使って秘密情報を管理する方法'
date: '2026-05-13'
category: 'GitHub Actions'
---

## Secretsの設定手順

1. GitHubリポジトリ→「Settings」→「Secrets and variables」→「Actions」
2. 「New repository secret」→Name・Secretを入力

## ワークフローから参照する

```yaml
steps:
  - name: デプロイ
    env:
      API_KEY: ${{ secrets.API_KEY }}
    run: echo "APIキーを使った処理"
```

## ハマったポイント

- Secretsの値はログにマスクされる
- 一度登録すると値を確認できない（上書きのみ）
- フォークされたリポジトリからのPRではSecretsは使えない

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [Cloudflare Pagesで環境変数を設定する方法](/posts/cloudflare-pages-env-variables)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
