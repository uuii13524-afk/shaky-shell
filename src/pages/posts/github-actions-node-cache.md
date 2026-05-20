---
title: 'GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法'
date: '2026-05-20'
category: 'GitHub Actions'
---

## やりたかったこと

GitHub Actionsのビルドが毎回 `npm install` から始まって時間がかかっていた。
キャッシュを使うと2回目以降が大幅に速くなる。

## 環境

- GitHub Actions
- Node.js
- npm

## キャッシュなしの場合

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
  - run: npm install    # 毎回全パッケージをインストール（遅い）
  - run: npm run build
```

## キャッシュありの場合

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'      # これだけでキャッシュが有効になる
  - run: npm ci         # npm install より高速で確実
  - run: npm run build
```

## npm install と npm ci の違い

| | npm install | npm ci |
|--|--|--|
| 速度 | 普通 | 速い |
| package-lock.json | 更新することがある | 更新しない |
| 用途 | 開発環境 | CI/CD環境 |

## キャッシュが効いているか確認する

GitHub Actions の実行ログで以下が表示されればキャッシュが使われている。

```
Cache restored successfully
```

初回は以下が表示される。

```
Cache not found for input keys
```

## ハマったポイント

- `cache: 'npm'` を設定するだけで自動的にキャッシュされる
- `package-lock.json` が変わるとキャッシュが無効になる
- キャッシュは7日間保持される

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [npmとyarnの違いと使い分け](/posts/npm-vs-yarn)
