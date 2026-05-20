---
title: 'GitHub Actionsでスケジュール実行（定期実行）を設定する方法'
date: '2026-05-19'
category: 'GitHub Actions'
---

## 基本的な設定

```yaml
on:
  schedule:
    - cron: '0 9 * * *'    # 毎日9時（UTC）
```

## よく使うcron設定例

```
0 9 * * *       # 毎日9時（UTC）
0 0 * * 1       # 毎週月曜日0時
0 9 1 * *       # 毎月1日9時
*/30 * * * *    # 30分ごと
```

## JSTに変換する

GitHubのcronはUTCなので9時間の差がある。

```
JSTの9時 = UTCの0時 → cron: '0 0 * * *'
```

## 手動実行も可能にする

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
```

## ハマったポイント

- cronはUTCなのでJSTと9時間ずれる
- リポジトリにアクティビティがないと無効化されることがある

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
