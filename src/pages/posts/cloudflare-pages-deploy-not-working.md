---
title: 'Cloudflare PagesのGitHub自動デプロイが動かない時の対処法'
date: '2026-05-20'
category: 'Cloudflare'
---

## 症状

git pushしてもCloudflare Pagesに変更が反映されない。
Deploymentsタブに新しいデプロイが来ない。
以下のメッセージが表示されることがある。

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## 環境

- Cloudflare Pages
- GitHub
- Astro

## 原因1：CloudflareとGitHubの接続が切れている

### 確認方法

Cloudflareダッシュボード→プロジェクト→「Settings」→「Git repository」を確認。
「Manage」ボタンの横に警告が出ていれば接続が切れている。

### 解決方法

1. 「Git repository」の「Manage」をクリック
2. GitHubアカウントを再認証する
3. 以下のコマンドで空のコミットをpushして強制デプロイ

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因2：古いコミットがデプロイされている

### 確認方法

Deploymentsタブのログに以下のような表示がある場合、最新のコミットではなく古いコミットが使われている。

```
HEAD is now at 3218655 first commit
```

git logで最新のコミットハッシュを確認する。

```
git log --oneline
```

### 解決方法

空のコミットをpushして再デプロイを強制する。

```
git commit --allow-empty -m "force deploy"
git push
```

## 原因3：ビルドエラーが発生している

### 確認方法

Deploymentsタブ→該当デプロイ→「View build logs」でエラー内容を確認する。

### よくあるエラー

**Astro.glob is not a functionエラー**

Astro 5以降では `Astro.glob()` が使えなくなった。
`import.meta.glob()` に書き換える必要がある。

## ハマったポイント

- 接続が切れていてもSettings画面では正常に見えることがある
- 空のコミットpushが最も確実な強制デプロイ方法
- ビルドログを最初に確認する習慣をつけると原因特定が早い

## 予防策

デプロイが反映されない時は以下の順番で確認する。

```
1. Deploymentsタブにデプロイが来ているか確認
2. ビルドログにエラーがないか確認
3. GitHubとの接続状態を確認
4. 空のコミットpushで強制デプロイ
```
