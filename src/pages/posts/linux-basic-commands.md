---
title: 'Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ'
date: '2026-05-10'
category: 'Linux'
---

## ファイル・フォルダの確認

```bash
ls          # 一覧
ls -la      # 詳細（隠しファイル含む）
pwd         # 現在のフォルダ
```

## フォルダの移動

```bash
cd /home/user    # 絶対パス
cd ..            # 1つ上
cd ~             # ホーム
```

## 作成・削除

```bash
mkdir newfolder      # フォルダ作成
touch newfile.txt    # ファイル作成
rm file.txt          # ファイル削除
rm -rf folder/       # フォルダを強制削除
```

## ファイルの中身を確認

```bash
cat file.txt         # 全内容
less file.txt        # スクロール表示（qで終了）
tail -f logfile.log  # リアルタイム表示
```

## ハマったポイント

- `rm -rf` は元に戻せない
- Linuxはファイル名の大文字小文字を区別する

## 関連記事

- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Linuxでpermission deniedエラーが出た時の対処法](/posts/linux-permission-denied)
- [Linuxでファイルを検索するgrep・findコマンドの使い方](/posts/linux-grep-find)
- [Linuxでログをリアルタイム監視するtail -fの使い方](/posts/linux-tail-log)
