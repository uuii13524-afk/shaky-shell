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

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
