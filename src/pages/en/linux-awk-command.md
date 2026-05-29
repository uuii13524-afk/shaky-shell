---
title: 'How to Extract and Process Text with the awk Command'
date: '2026-05-29'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'awk', 'コマンドライン', 'テキスト処理']
en_tags: ['Linux', 'awk', 'command line', 'text processing']
description: 'Learn how to use the Linux awk command to extract columns, filter rows, and aggregate data. Real log analysis examples included.'
---
## What I Wanted to Do
I needed to pull out specific columns from log files and aggregate only the rows matching certain conditions.
grep handles line-level filtering well, sed is great for substitutions, but awk turned out to be the right tool when I needed to work column by column.

## Basic awk Syntax

```bash
awk 'condition { action }' filename
```

If no condition is specified, the action runs on every line.

### Extract Specific Columns

Print only the 1st and 3rd columns of a space-delimited file.

```bash
awk '{ print $1, $3 }' access.log
```

`$1` is the first column, `$2` is the second, and `$NF` is the last column.

### Specify a Field Delimiter

Use `-F` to set a custom delimiter, like a comma for CSV files.

```bash
awk -F',' '{ print $2 }' data.csv
```

Extract just the usernames from `/etc/passwd` using a colon delimiter.

```bash
awk -F':' '{ print $1 }' /etc/passwd
```

### Filter Rows by Condition

Print only lines where the third column is 500 or more.

```bash
awk '$3 >= 500 { print $0 }' access.log
```

Process only lines that contain a specific string.

```bash
awk '/ERROR/ { print $0 }' app.log
```

### Count Lines and Calculate Totals

Count the number of lines in a file (same as `wc -l`).

```bash
awk 'END { print NR }' file.txt
```

Sum the values in the third column.

```bash
awk '{ sum += $3 } END { print sum }' access.log
```

### BEGIN and END Blocks

`BEGIN` runs before reading the file; `END` runs after all lines are processed.

```bash
awk 'BEGIN { print "=== start ===" } { print $1 } END { print "=== end ===" }' file.txt
```

### Combine with grep

A real-world example: extract the IP addresses behind 5xx errors from an nginx access log.

```bash
grep ' 5[0-9][0-9] ' access.log | awk '{ print $1 }' | sort | uniq -c | sort -rn | head -20
```

### Use Variables

You can declare and use variables inside awk.

```bash
awk '{ count[$1]++ } END { for (ip in count) print count[ip], ip }' access.log | sort -rn | head -10
```

This pattern is handy for counting accesses per IP address.

## Common Pitfalls
- `$0` is the whole line; column numbers start at `$1`, not `$0` — there is no zero index
- The default delimiter is any whitespace; multiple spaces in a row count as one
- Always wrap the `-F` delimiter argument in single quotes: `-F','`
- `print $1 $2` concatenates without a separator; `print $1, $2` adds a space between them — the comma matters
- For processing large log files, awk starts faster than Python and is often all you need

## Related Articles
- [How to Replace Text with the sed Command](/en/linux-sed-command)
- [How to Search Files with grep and find](/en/linux-grep-find)
- [How to Monitor Logs in Real Time with tail -f](/en/linux-tail-log)
- [Linux Basic Commands (ls/cd/mkdir/rm)](/en/linux-basic-commands)
- [How to Check nginx Access and Error Logs](/en/nginx-access-log)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
