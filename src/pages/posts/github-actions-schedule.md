---
title: 'GitHub Actionsでスケジュール実行（定期実行）を設定する方法'
date: '2026-05-20'
category: 'GitHub Actions'
---

## やりたかったこと

GitHub Actionsを毎日決まった時間に自動実行したかった。
cronの設定でスケジュール実行できる。

## 環境

- GitHub Actions

## 基本的な設定

```yaml
name: Daily Task

on:
  schedule:
    - cron: '0 9 * * *'    # 毎日9時（UTC）に実行

jobs:
  run-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: タスクを実行
        run: echo "定期実行されました"
```

## cron式の書き方

```
分 時 日 月 曜日
*  *  *  *  *
```

### よく使う設定例

```
0 9 * * *       # 毎日9時（UTC）
0 0 * * *       # 毎日0時（UTC）
0 9 * * 1       # 毎週月曜日9時
0 9 1 * *       # 毎月1日9時
*/30 * * * *    # 30分ごと
```

### JSTに変換する場合

GitHubのcronはUTCなのでJSTとは9時間の差がある。

```
JSTの9時 = UTCの0時 → cron: '0 0 * * *'
JSTの18時 = UTCの9時 → cron: '0 9 * * *'
```

## pushとスケジュール両方で実行する

```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'
```

## 手動実行も可能にする

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:    # 手動実行を有効にする
```

## ハマったポイント

- cronはUTCなのでJSTと9時間ずれる
- スケジュール実行はリポジトリにアクティビティがないと無効化されることがある
- 無料枠の実行時間制限に注意
- `workflow_dispatch` を追加すると手動でもテスト実行できる

## 関連記事

- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)
- [GitHub ActionsでSecretsを使って秘密情報を管理する方法](/posts/github-actions-secrets)
- [GitHub ActionsでNode.jsのキャッシュを使ってビルドを高速化する方法](/posts/github-actions-node-cache)
- [GitHubで初めてリポジトリを作ってpushする手順](/posts/github-first-push)
