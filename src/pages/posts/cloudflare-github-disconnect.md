---
title: 'Cloudflare PagesがGitHubと切断された時の対処法'
date: '2026-05-20'
category: 'Cloudflare'
---

## 症状

git pushしてもCloudflare Pagesに反映されない。ダッシュボードに以下のメッセージが表示される。

This project is disconnected from your Git account.
This may cause deployments to fail.

## 環境

- Cloudflare Pages
- GitHub
- Astro

## 試したこと

- git pushしたが反映されなかった
- Deploymentsタブを確認したが新しいデプロイが来なかった

## 原因

CloudflareとGitHubの接続が切れていた。

## 解決方法

1. Cloudflareダッシュボードで該当プロジェクトを開く
2. Settings → Git repositoryのManageをクリック
3. GitHubアカウントを再認証
4. 以下のコマンドで空のコミットをpushして強制デプロイ

git commit --allow-empty -m "force deploy"
git push

## 再発防止

デプロイが反映されない時はまずDeploymentsタブのログを確認する。