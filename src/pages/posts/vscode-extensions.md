---
title: 'VSCodeのおすすめ拡張機能10選（開発効率化）'
date: '2026-05-21'
category: 'Windows'
layout: '../../layouts/PostLayout.astro'
---

## やりたかったこと

VSCodeの拡張機能を使って開発効率を上げたかった。
特に使用頻度が高いものをまとめる。

## 環境

- Visual Studio Code

## おすすめ拡張機能

### 1. GitLens

Gitの履歴をVSCode上で確認できる。
誰がいつどの行を変更したか一目でわかる。

```
拡張機能ID：eamodio.gitlens
```

### 2. Prettier

コードを自動フォーマットする。
保存時に自動整形されるように設定すると便利。

```
拡張機能ID：esbenp.prettier-vscode
```

### 3. ESLint

JavaScriptのコードチェック。
バグになりやすいコードを事前に検出する。

```
拡張機能ID：dbaeumer.vscode-eslint
```

### 4. Docker

DockerfileやDocker Composeの補完・構文チェック。

```
拡張機能ID：ms-azuretools.vscode-docker
```

### 5. Remote - SSH

VPSにSSH接続してVSCodeで直接編集できる。

```
拡張機能ID：ms-vscode-remote.remote-ssh
```

### 6. GitHub Copilot

AIによるコード補完。有料だが生産性が大幅に向上する。

```
拡張機能ID：GitHub.copilot
```

### 7. indent-rainbow

インデントをカラフルに表示して見やすくする。

```
拡張機能ID：oderwat.indent-rainbow
```

### 8. Auto Rename Tag

HTMLのタグを変更すると対応するタグも自動で変わる。

```
拡張機能ID：formulahendry.auto-rename-tag
```

### 9. Path Intellisense

ファイルパスの補完。`./` と入力するとファイル候補が出る。

```
拡張機能ID：christian-kohler.path-intellisense
```

### 10. Japanese Language Pack

VSCodeのUIを日本語化する。

```
拡張機能ID：MS-CEINTL.vscode-language-pack-ja
```

## 拡張機能のインストール方法

1. VSCodeを開く
2. 左サイドバーの拡張機能アイコン（四角が4つ）をクリック
3. 拡張機能IDを検索
4. 「インストール」をクリック

## ハマったポイント

- 拡張機能を入れすぎるとVSCodeが重くなる
- Prettierを使う場合はESLintと設定を合わせる必要がある
- Remote - SSHは開発効率が大幅に上がるのでVPSを使う人には必須

## 関連記事

- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [SSHキーを生成してGitHubに登録する方法](/posts/ssh-key-github)
- [VPSにDockerをインストールして本番環境を構築する方法](/posts/vps-docker-setup)
- [GitHub Actionsで自動デプロイする基本的な設定方法](/posts/github-actions-basic)

## おすすめのVPS

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
