---
title: 'Windowsのターミナルでパスにスペースがある時の対処法'
date: '2026-05-20'
category: 'Windows'
---

## 症状

```
cd C:\Users\acia\My Documents\project
# エラー：'Documents\project' は認識されません
```

## 環境

- Windows 10 / 11
- コマンドプロンプト / PowerShell

## 解決方法

### 方法1：ダブルクォートで囲む

```
cd "C:\Users\acia\My Documents\project"
```

最もシンプルな解決方法。

### 方法2：スペースなしのフォルダ名にする

```
C:\Users\acia\My_Documents\project
```

根本的な解決策。

## ハマったポイント

- スペースを含むパスは必ずダブルクォートで囲む
- 開発用フォルダは最初からスペースなしで作るのがベスト

## 予防策

```
C:\Users\ユーザー名\projects\プロジェクト名
```

スペースの代わりにハイフン `-` やアンダースコア `_` を使う。

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
