---
title: 'npmのキャッシュをクリアして問題を解決する方法'
date: '2026-05-20'
category: 'Node.js'
---

## 症状

npmでパッケージをインストールしても動かない。
以前のバージョンが残っていておかしな動作をしている。
インストールが途中で止まる。

## 環境

- Node.js
- npm

## キャッシュのクリア方法

### 基本のキャッシュクリア

```
npm cache clean --force
```

### キャッシュの状態を確認

```
npm cache verify
```

キャッシュの整合性チェックと不要なファイルの削除を行う。

### キャッシュの場所を確認

```
npm config get cache
```

## パッケージ関連の問題をリセットする方法

キャッシュクリアだけで解決しない場合は以下を試す。

### node_modulesを削除して再インストール

```
# node_modulesを削除
rm -rf node_modules

# package-lock.jsonを削除
rm package-lock.json

# 再インストール
npm install
```

Windowsの場合。

```
rmdir /s /q node_modules
del package-lock.json
npm install
```

### npxのキャッシュをクリア

```
npx clear-npx-cache
```

## ハマったポイント

- `--force` なしでは警告が出てキャッシュがクリアされない場合がある
- `node_modules` を削除して再インストールするのが最も確実な方法
- `package-lock.json` も一緒に削除すると依存関係がリセットされる
- キャッシュクリア後はインストールに時間がかかる

## いつキャッシュクリアするか

- パッケージのインストールが失敗する
- バージョンを変えても古い動作をしている
- 原因不明のエラーが出る
- 長期間使っていなかったプロジェクトを再開する時
