---
title: 'How to Use the sed Command for Text Substitution and Editing in Linux'
date: '2026-05-27'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'sed', 'テキスト処理', 'コマンドライン']
en_tags: ['Linux', 'sed', 'text processing', 'command line']
description: 'Learn how to use the sed command to substitute strings, delete lines, and extract text in Linux. Practical examples included.'
---
## What I Wanted to Do
I needed to bulk-replace strings in config files and extract specific lines from log files.
I could search with grep just fine, but sed always tripped me up when it came to actual substitutions.

## Basic Syntax

```bash
sed 's/old/new/g' filename
```

- `s` stands for substitute
- `g` is global — replaces all occurrences on each line
- Without `g`, only the first match per line is replaced

## Common Operations

### Substituting Strings

```bash
# Replace 'foo' with 'bar' and print to stdout
sed 's/foo/bar/g' config.txt

# Edit the file in-place with -i
sed -i 's/foo/bar/g' config.txt

# macOS requires an empty string after -i
sed -i '' 's/foo/bar/g' config.txt
```

### Creating a Backup While Editing In-Place

```bash
# Saves original as config.txt.bak before overwriting
sed -i.bak 's/foo/bar/g' config.txt
```

### Deleting Lines

```bash
# Delete line 3
sed '3d' file.txt

# Delete all blank lines
sed '/^$/d' file.txt

# Delete comment lines starting with #
sed '/^#/d' file.txt
```

### Printing Specific Lines

```bash
# Print lines 5 through 10
sed -n '5,10p' file.txt

# Print lines matching "error"
sed -n '/error/p' file.txt
```

### Inserting Lines

```bash
# Append a line after line 3
sed '3a\inserted text here' file.txt

# Insert a line before line 3
sed '3i\inserted text here' file.txt
```

### Multiple Substitutions at Once

```bash
# Use -e to chain multiple expressions
sed -e 's/foo/bar/g' -e 's/old/new/g' file.txt
```

### Replacing Strings That Contain Slashes

When the pattern includes `/` (e.g. file paths or URLs), swap the delimiter.

```bash
# Use | as delimiter instead
sed 's|/old/path|/new/path|g' config.txt
```

## Common Pitfalls

- Editing in-place with `-i` is irreversible — always use `.bak` to keep a backup
- `-i` behaves differently on macOS vs Linux; macOS requires `sed -i ''`
- Regex metacharacters (`.` `*` `[` `]`) need to be escaped with a backslash
- Forgetting the `g` flag means only the first match per line gets replaced
- By default sed writes to stdout, not back to the file — use `-i` to modify in-place

## Related Articles
- [How to Search Files with grep and find in Linux](/posts/linux-grep-find)
- [Basic Linux Commands: ls, cd, mkdir, rm](/posts/linux-basic-commands)
- [How to Monitor Logs in Real Time with tail -f](/posts/linux-tail-log)
- [Linux File Permissions: chmod and chown Guide](/posts/linux-file-permissions)
- [How to Use the curl Command](/posts/linux-curl-command)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
