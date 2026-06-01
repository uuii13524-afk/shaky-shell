---
title: 'How to Use xargs to Batch Process Files and Input in Linux'
date: '2026-05-30'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'xargs', 'コマンド', 'シェル', 'bash']
en_tags: ['Linux', 'xargs', 'command', 'shell', 'bash']
description: 'A practical guide to the xargs command in Linux. Learn how to combine it with find and grep to delete or process files in bulk.'
---
## What I Wanted to Do
I wanted to search for files with `find` and then delete or process all of them at once.
Typing `find . -name "*.log" | rm` didn't work at all — that's when I found out about `xargs`.

## Basic xargs Usage

### Pass stdin as arguments to a command
```bash
echo "file1.txt file2.txt file3.txt" | xargs ls -l
```
xargs takes stdin and passes each item as arguments to the specified command.

### Delete files found by find in bulk
```bash
find . -name "*.log" | xargs rm
```
xargs converts find's output into arguments for `rm`.

### Handle filenames with spaces (-0 option)
```bash
find . -name "*.txt" -print0 | xargs -0 rm
```
Combine `-print0` with `-0` to safely handle filenames that contain spaces or newlines.

### Limit arguments per command run (-n)
```bash
echo "a b c d e" | xargs -n 2 echo
```
```
a b
c d
e
```
`-n 2` passes two arguments at a time.

### Specify argument position (-I)
```bash
ls *.txt | xargs -I{} cp {} /backup/{}
```
`-I{}` lets you place the argument anywhere in the command using `{}`. Handy for copying files into a backup directory.

### Run commands in parallel (-P)
```bash
find . -name "*.gz" | xargs -P 4 -I{} gzip -d {}
```
`-P 4` runs 4 processes in parallel — a big speedup when processing lots of files.

## Common Gotchas
- Piping directly into `rm` doesn't work — you need `xargs` in between
- Always use `-print0 | xargs -0` when filenames may contain spaces or newlines
- When using `-I{}`, include the full path around `{}` as needed
- `xargs` also fixes the "Argument list too long" error when you have too many files
- There's no `--dry-run` flag — substitute `echo` first to preview the commands before running for real

## Related Articles
- [How to Search Files with grep and find on Linux](/en/linux-grep-find)
- [How to Use the sed Command for Text Substitution and Editing in Linux](/en/linux-sed-command)
- [How to Extract and Process Text with the awk Command](/en/linux-awk-command)
- [Linux Basic Commands Cheatsheet (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [How to Sync and Backup Files with rsync](/en/linux-rsync)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
