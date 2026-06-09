---
title: 'How to Parse and Filter JSON with the jq Command'
date: '2026-06-08'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Linux', 'jq', 'JSON', 'コマンド', 'bash']
en_tags: ['Linux', 'jq', 'JSON', 'command', 'bash']
description: 'Learn how to use jq to pretty-print JSON from curl responses and extract specific fields with filters. Practical examples included.'
---
## What I Was Trying to Do
I was hitting an API with curl and the JSON response came back as one giant unreadable line.
The server didn't have Python installed, so `python3 -m json.tool` wasn't an option — I had to figure out `jq`.

## Environment
- Ubuntu 22.04
- jq 1.6
- bash 5.1

## Installing jq

```bash
# Ubuntu / Debian
sudo apt install jq

# macOS
brew install jq
```

Verify installation:

```bash
jq --version
# jq-1.6
```

## Basic Usage

To pretty-print a curl response, pipe it through `jq '.'`:

```bash
curl -s https://api.example.com/users | jq '.'
```

To process a local file:

```bash
jq '.' response.json
```

## Common Filters

### Extract a specific key

```bash
# Extract "name" from {"name": "taro", "age": 30}
echo '{"name": "taro", "age": 30}' | jq '.name'
# "taro"

# Strip quotes with -r (raw output)
echo '{"name": "taro", "age": 30}' | jq -r '.name'
# taro
```

### Working with arrays

```bash
# Expand all elements
echo '[{"id":1},{"id":2}]' | jq '.[]'

# Get the first element
echo '[{"id":1},{"id":2}]' | jq '.[0]'

# Extract a specific key from every element
echo '[{"name":"taro"},{"name":"hanako"}]' | jq '[.[].name]'
```

### Nested keys

```bash
# {"user": {"profile": {"email": "test@example.com"}}}
echo '{"user":{"profile":{"email":"test@example.com"}}}' | jq '.user.profile.email'
# "test@example.com"
```

### Filter with select

```bash
# Return only elements where age >= 30
echo '[{"name":"taro","age":30},{"name":"hanako","age":25}]' | jq '[.[] | select(.age >= 30)]'
```

### Build a new object

```bash
echo '[{"name":"taro","age":30}]' | jq '.[] | {user: .name, years: .age}'
```

## What I Tried First

I first tried `grep` to pull out specific fields, but it fell apart the moment the JSON was multi-line — values on the next line just didn't match.

Then I attempted an `awk` approach, but awk really can't handle nested JSON cleanly. I also tried a `python3 -c "import json,sys;..."` one-liner, but writing it from scratch every time was tedious enough that I finally just installed `jq`.

## The Fix

Installing `jq` and piping curl output through it solved everything immediately.

```bash
curl -s https://api.example.com/users/1 | jq '.name'
```

I've been using it for all API debugging ever since. This fixed it.

## Key Takeaways

- `.name` returns the value with surrounding double quotes. Use the `-r` flag when you need raw string output (e.g., assigning to a shell variable)
- `.[]` expands every element of an array as separate outputs; `.[0]` returns only the first element — easy to mix these up early on
- String comparisons inside `select()` need `== "value"`, not `= "value"`. Spent a while wondering why `select(.status = "active")` threw an error
- Always wrap jq filters in single quotes in shell scripts. Without them, bash interprets `$` and `|` before jq ever sees them

## Related Articles
- [How to Use the curl Command](/en/linux-curl-command)
- [How to Extract and Process Text with awk](/en/linux-awk-command)
- [How to Search Files with grep and find in Linux](/en/linux-grep-find)
- [How to Replace Strings with the sed Command](/en/linux-sed-command)
- [Basic GitHub Actions Setup for Automated Deployment](/en/github-actions-basic)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
