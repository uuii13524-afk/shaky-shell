---
title: 'Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ'
date: '2026-05-20'
category: 'Linux'
---

## やりたかったこと

Linuxのターミナルで基本的な操作ができるようになりたかった。
最低限これだけ知っていれば日常的な作業はできる。

## 環境

- Linux（Ubuntu / Debian）
- Mac
- WSL2（Windows）

## ファイル・フォルダの確認

### ls：ファイル一覧を表示

```bash
ls          # 現在のフォルダの一覧
ls -la      # 詳細表示（隠しファイル含む）
ls -lh      # ファイルサイズを見やすく表示
ls /var/log # 指定フォルダの一覧
```

### pwd：現在のフォルダを表示

```bash
pwd
# 例：/home/user/projects
```

## フォルダの移動

### cd：フォルダを移動

```bash
cd /home/user       # 絶対パスで移動
cd projects         # 相対パスで移動
cd ..               # 1つ上のフォルダに移動
cd ~                # ホームフォルダに移動
cd -                # 直前のフォルダに戻る
```

## ファイル・フォルダの作成

### mkdir：フォルダを作成

```bash
mkdir newfolder           # フォルダを作成
mkdir -p a/b/c            # 階層ごと作成
```

### touch：ファイルを作成

```bash
touch newfile.txt         # 空ファイルを作成
```

## ファイル・フォルダの削除

### rm：ファイルを削除

```bash
rm file.txt               # ファイルを削除
rm -r folder/             # フォルダを中身ごと削除
rm -rf folder/            # 確認なしで強制削除（注意）
```

## ファイルのコピー・移動

### cp：コピー

```bash
cp file.txt backup.txt    # ファイルをコピー
cp -r folder/ backup/     # フォルダをコピー
```

### mv：移動・名前変更

```bash
mv file.txt /tmp/         # ファイルを移動
mv oldname.txt newname.txt # 名前を変更
```

## ファイルの中身を確認

```bash
cat file.txt              # 全内容を表示
less file.txt             # スクロールして表示（qで終了）
head -n 10 file.txt       # 先頭10行を表示
tail -n 10 file.txt       # 末尾10行を表示
tail -f logfile.log       # リアルタイムで末尾を表示
```

## ハマったポイント

- `rm -rf` は元に戻せない。使う前に必ず確認する
- Linuxはファイル名の大文字小文字を区別する
- スペースを含むファイル名はダブルクォートで囲む
- `Tab` キーでファイル名を補完できる

## 関連記事

- [WindowsにDockerをインストールして動かすまでの手順](/posts/docker-install-windows)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Gitで.gitignoreを設定してファイルを管理対象から外す方法](/posts/git-gitignore-setup)
- [npmのキャッシュをクリアして問題を解決する方法](/posts/npm-cache-clear)
