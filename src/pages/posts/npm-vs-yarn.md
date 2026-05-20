---
title: 'npmとyarnの違いと使い分け'
date: '2026-05-20'
category: 'Node.js'
---

## やりたかったこと

npmとyarnの違いがわからなかった。
どちらを使えばいいか判断できるようにまとめる。

## npmとyarnとは

どちらもNode.jsのパッケージマネージャー。
`package.json` に書かれた依存関係を管理する。

## コマンド比較

| 操作 | npm | yarn |
|------|-----|------|
| インストール | `npm install` | `yarn` |
| パッケージ追加 | `npm install パッケージ名` | `yarn add パッケージ名` |
| パッケージ削除 | `npm uninstall パッケージ名` | `yarn remove パッケージ名` |
| スクリプト実行 | `npm run スクリプト名` | `yarn スクリプト名` |
| グローバルインストール | `npm install -g パッケージ名` | `yarn global add パッケージ名` |
| キャッシュクリア | `npm cache clean --force` | `yarn cache clean` |

## どちらを使うべきか

### npmを使う場合

- Node.jsに標準で付属しているので追加インストール不要
- 特にこだわりがなければnpmで十分
- 最新のnpmはyarnと同等の速度になっている

### yarnを使う場合

- プロジェクトがyarnを指定している場合（`yarn.lock` がある）
- ワークスペース機能を使いたい場合

## 混在させない

npmとyarnを同じプロジェクトで混在させると問題が起きる。

```
# npmを使っているプロジェクト
package-lock.json が存在する → npm を使う

# yarnを使っているプロジェクト
yarn.lock が存在する → yarn を使う
```

## yarnのインストール方法

```
npm install -g yarn
yarn --version
```

## ハマったポイント

- `package-lock.json` と `yarn.lock` を両方コミットしない
- チームで開発する場合はどちらかに統一する
- Astroプロジェクトはnpmで作成した場合はnpmを使い続ける

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
- [Node.jsのバージョンをnvmで管理する方法](/posts/node-version-management-nvm)
- [AstroをCloudflare Pagesにデプロイする手順](/posts/astro-cloudflare-deploy)
