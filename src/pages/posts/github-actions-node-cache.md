---
title: 'GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法'
date: '2026-05-15'
category: 'GitHub Actions'
---

## キャッシュありの設定

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'      # これだけでキャッシュが有効
  - run: npm ci
  - run: npm run build
```

## npm install と npm ci の違い

| | npm install | npm ci |
|--|--|--|
| 速度 | 普通 | 速い |
| package-lock.json | 更新することがある | 更新しない |
| 用途 | 開発環境 | CI/CD環境 |

## ハマったポイント

- `cache: 'npm'` を設定するだけで自動的にキャッシュされる
- `package-lock.json` が変わるとキャッシュが無効になる

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
