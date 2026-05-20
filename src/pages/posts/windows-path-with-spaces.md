---
title: 'Windowsのターミナルでパスにスペースがある時の対処法'
date: '2026-05-08'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
---

## 症状

```
cd C:\Users\acia\My Documents\project
# エラー：'Documents\project' は認識されません
```

## 解決方法

ダブルクォートで囲む。

```
cd "C:\Users\acia\My Documents\project"
```

## 予防策

開発用フォルダはスペースなしで作る。

```
C:\Users\ユーザー名\projects\プロジェクト名
```

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
