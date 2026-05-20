---
title: 'Cloudflare Pagesのビルドログの見方とエラーの対処法'
date: '2026-05-20'
category: 'Cloudflare'
---

## やりたかったこと

Cloudflare Pagesのデプロイが失敗した時にビルドログを読んで原因を特定したかった。

## 環境

- Cloudflare Pages

## ビルドログの開き方

1. Cloudflareダッシュボードにログイン
2. 「Workers & Pages」をクリック
3. 対象プロジェクトをクリック
4. 「Deployments」タブを開く
5. 対象のデプロイをクリック
6. 「View build logs」をクリック

## ビルドログの見方

ログは上から順番に実行される。エラーが発生した行に注目する。

### 成功時のログの流れ

```
Cloning repository...          # GitHubからコードを取得
Installing project dependencies # npm installの実行
Executing user command          # npm run buildの実行
Uploading...                    # ファイルのアップロード
Success: Your site was deployed # デプロイ完了
```

### エラーが出た時の確認ポイント

エラーは `[ERROR]` や `Failed` で始まる行を探す。

```
[ERROR] TypeError: ...         # コードのエラー
Failed: build command exited   # ビルドコマンドの失敗
Error while executing          # 実行エラー
```

## よくあるエラーと対処法

### エラー1：Astro.glob is not a function

```
TypeError: Astro2.glob is not a function
```

**原因：** Astro 5以降で `Astro.glob()` が廃止された。

**対処法：** `import.meta.glob()` に書き換える。

### エラー2：Cannot find module

```
Error: Cannot find module '@astrojs/sitemap'
```

**原因：** パッケージがインストールされていない。

**対処法：**
```
npm install @astrojs/sitemap
```

### エラー3：古いコミットがデプロイされている

ログに以下が表示される場合。

```
HEAD is now at 3218655 first commit
```

**原因：** GitHubとの接続が切れて古いコミットが使われている。

**対処法：**
```
git commit --allow-empty -m "force deploy"
git push
```

## ハマったポイント

- エラーの行だけ見ても分からない場合はその前後の行も確認する
- ビルドログは時系列順なので上から読む
- `Failed` が出た行の直前にエラーの原因が書いてある場合が多い
- ログが流れてしまう場合はブラウザの検索（Ctrl+F）で「ERROR」を検索する
