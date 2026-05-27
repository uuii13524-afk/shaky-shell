---
title: 'Basic curl Command Usage for API Testing'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to send HTTP requests with the curl command. Covers GET, POST, headers, authentication, and file download options.'
---

## What I Wanted to Do

I wanted to send HTTP requests from the command line.
With curl, you can test APIs and download files.

## Environment

- Linux / Mac / Windows (Git Bash)

## Basic Usage

### GET request

```bash
curl https://example.com
curl -s https://example.com    # Hide progress output
curl -o output.html https://example.com  # Save to a file
```

### POST request

```bash
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Checking headers

```bash
curl -I https://example.com    # Show headers only
curl -v https://example.com    # Verbose output
```

### Authenticated request

```bash
curl -H "Authorization: Bearer your_token" https://api.example.com
```

## Commonly Used API Testing Options

```bash
-X GET/POST/PUT/DELETE   # Specify HTTP method
-H "Header-Name: value"  # Add a header
-d "data"                # Request body
-o filename              # Save response to a file
-s                       # Silent mode
-v                       # Verbose output
-L                       # Follow redirects
```

## Common Pitfalls

- Single quotes don't work in the Windows Command Prompt. Use Git Bash instead
- Combining `-s` and `-o` saves to a file without showing progress
- To pretty-print JSON output, pipe to `| python3 -m json.tool`

Once you've confirmed an API returns the correct response, combining it with [How to Search Files with grep and find on Linux](/en/linux-grep-find) to filter results through a pipe is a useful technique to know.

## Related Articles

- [Essential Linux Commands (ls/cd/mkdir/rm) Cheat Sheet](/en/linux-basic-commands)
- [How to Search Files with grep and find on Linux](/en/linux-grep-find)
- [Basic Setup for Automatic Deployment with GitHub Actions](/en/github-actions-basic)
- [How to Set Environment Variables in Cloudflare Pages](/en/cloudflare-pages-env-variables)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
