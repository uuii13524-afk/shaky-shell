---
title: 'Windowsで環境変数を設定・確認する方法'
date: '2026-05-20'
category: 'Windows'
---

## やりたかったこと

WindowsでPATHなどの環境変数を設定したかった。
コマンドが認識されない場合は環境変数の設定が必要なことが多い。

## 環境

- Windows 10 / 11

## GUIで設定する方法

1. Windowsの検索で「環境変数」を検索
2. 「システム環境変数の編集」をクリック
3. 「環境変数」ボタンをクリック
4. 「ユーザー環境変数」または「システム環境変数」の「Path」を選択
5. 「編集」→「新規」でパスを追加
6. OKで閉じる
7. ターミナルを再起動

## コマンドで確認する方法

### PowerShell

```powershell
$env:PATH                          # PATH を確認
$env:PATH -split ";"               # 見やすく表示
[Environment]::GetEnvironmentVariable("PATH", "User")  # ユーザー環境変数
```

### コマンドプロンプト

```cmd
echo %PATH%                        # PATH を確認
set                                # 全環境変数を表示
set PATH                           # PATH だけ表示
```

## コマンドで一時的に設定する方法

セッション中のみ有効（ターミナルを閉じると消える）。

### PowerShell

```powershell
$env:MY_KEY = "my_value"
```

### コマンドプロンプト

```cmd
set MY_KEY=my_value
```

## ハマったポイント

- 環境変数を変更したらターミナルを再起動しないと反映されない
- ユーザー環境変数はそのユーザーのみ有効
- システム環境変数は全ユーザーに有効（管理者権限が必要）
- `PATH` にセミコロン `;` 区切りで複数のパスを追加できる

## よくある環境変数

```
PATH        # コマンドの検索パス
JAVA_HOME   # Javaのインストールパス
NODE_PATH   # Node.jsのモジュールパス
PYTHON_HOME # Pythonのインストールパス
```

## 関連記事

- [Windowsでnpmコマンドが動かない時の対処法](/posts/windows-npm-not-working)
- [WindowsにGitをインストールして初期設定する方法](/posts/windows-git-install)
- [WindowsでWSL2をインストールする方法](/posts/wsl2-install-windows)
- [Windows Terminalをインストールして使いやすくする方法](/posts/windows-terminal-setup)
