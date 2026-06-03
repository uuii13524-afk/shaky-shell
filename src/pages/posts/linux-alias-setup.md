---
title: 'Linuxでエイリアスを設定して作業を効率化する方法（.bashrc/.zshrc）'
date: '2026-06-02'
category: 'Linux'
layout: '../../layouts/PostLayout.astro'
ja_tags: ['Linux', 'bash', 'zsh', 'エイリアス', 'シェル設定']
en_tags: ['Linux', 'bash', 'zsh', 'alias', 'shell configuration']
description: 'Linuxで.bashrcや.zshrcにエイリアスを設定してコマンドを短縮する方法。Git・Docker・Linuxの実用例から関数定義まで丁寧に解説。'
---
## やりたかったこと
`git status` や `docker-compose up -d` を毎回フルで打つのが面倒になってきた。
`.bashrc` か `.zshrc` にエイリアスを書くだけで短縮コマンドとして使えるようになった。

## aliasの基本的な書き方
`.bashrc`（bashの場合）または `.zshrc`（zshの場合）にalias定義を追加する。

```bash
# ~/.bashrc または ~/.zshrc に追記
alias gs='git status'
alias gp='git push'
alias ll='ls -la'
alias dc='docker-compose'
```

追記したら反映させる：

```bash
source ~/.bashrc
# または
source ~/.zshrc
```

## よく使うエイリアスの例

### Gitのショートカット
```bash
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph'
alias gd='git diff'
```

### Dockerのショートカット
```bash
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dps='docker ps -a'
alias drm='docker rm $(docker ps -aq)'
```

### Linuxコマンドの便利設定
```bash
alias ll='ls -la'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias mkdir='mkdir -pv'
```

## 関数として登録する
複数のコマンドを組み合わせたい場合は関数にする。

```bash
# ディレクトリを作成してすぐ移動する
mkcd() {
  mkdir -p "$1" && cd "$1"
}

# git add + commit + push をまとめて実行
gacp() {
  git add .
  git commit -m "$1"
  git push
}
```

関数は `alias` と同様に `.bashrc` / `.zshrc` に書けばOK。

## 現在設定されているaliasを確認する
```bash
# 全一覧を表示
alias

# 特定のaliasだけ確認
alias gs
```

## ハマったポイント
- `source ~/.bashrc` を実行しないと新しいターミナルを開くまで反映されない
- bashを使っているのに `.zshrc` を編集していた（`echo $SHELL` で確認する）
- エイリアス名が既存コマンドと被ると上書きされるので注意（`which dc` などで確認）
- `alias gc='git commit -m'` は後ろに引数を付ける形なので `gc "message"` と使う
- サーバーのログインシェルが `/bin/sh` の場合、`.bashrc` が自動で読み込まれないことがある

## 関連記事
- [Linuxの基本コマンド（ls/cd/mkdir/rm）まとめ](/posts/linux-basic-commands)
- [LinuxのSSH接続の基本（VPSに接続する方法）](/posts/linux-ssh-basics)
- [~/.ssh/configでSSH接続を効率化する方法](/posts/ssh-config-file)
- [LinuxでCronジョブを設定して定期実行する方法](/posts/linux-cron-setup)
- [Linuxでプロセスを確認・終了する方法（ps/kill）](/posts/linux-process-management)

## おすすめのVPS／ドメイン／スクール
VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
