---
title: 'How to Check nginx Access Logs and Error Logs'
date: '2026-05-28'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'ログ', 'Linux', 'サーバー管理', 'トラブルシューティング']
en_tags: ['nginx', 'access log', 'error log', 'Linux', 'server management']
description: 'A guide to finding and reading nginx access and error logs on Linux. Covers log locations, tail/grep for real-time monitoring, and log format explained.'
---
## What I Wanted to Do
I wanted to verify that nginx was working correctly and find out why pages weren't loading despite getting requests.
Tracking down the log files helped me identify the root cause quickly.

## Log File Locations
nginx logs are typically stored here:

```bash
/var/log/nginx/access.log   # Access log
/var/log/nginx/error.log    # Error log
```

You can also confirm the paths from the config file:

```bash
grep log /etc/nginx/nginx.conf
```

## Checking the Access Log
### Monitor in real time

```bash
tail -f /var/log/nginx/access.log
```

### Show the last 100 lines

```bash
tail -n 100 /var/log/nginx/access.log
```

### Filter by a specific IP address

```bash
grep "192.168.1.1" /var/log/nginx/access.log
```

### Extract 404 errors only

```bash
grep " 404 " /var/log/nginx/access.log
```

### Count the most-accessed URLs

```bash
awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

## Checking the Error Log
### Monitor errors in real time

```bash
tail -f /var/log/nginx/error.log
```

### Show only error-level entries

```bash
grep "\[error\]" /var/log/nginx/error.log
```

Log severity levels:

| Level  | Meaning                        |
|--------|--------------------------------|
| notice | Normal operation notices       |
| warn   | Warnings (non-critical)        |
| error  | Errors (needs attention)       |
| crit   | Critical errors                |

## Reading the Access Log Format
The default access log looks like this:

```
192.168.1.1 - - [28/May/2026:10:00:00 +0900] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
```

Fields from left to right:
- Client IP address
- Remote user (usually `-`)
- Authenticated user (usually `-`)
- Request timestamp
- Request line
- HTTP status code
- Response size in bytes
- Referer
- User-Agent

## Checking Log Rotation

```bash
ls -la /var/log/nginx/
```

Old logs are kept as `access.log.1` or compressed as `access.log.2.gz`.
logrotate is usually configured by default with nginx.

## Common Pitfalls
- If the log file is empty, nginx may not be running or the path may be wrong
- Always check `systemctl status nginx` first — it saves time before digging into logs
- Add `sudo` if you get a `Permission denied` error reading the log files
- On high-traffic servers, always use `tail -n` to limit output or the terminal can freeze
- `connect() failed` in the error log usually means the backend behind a reverse proxy is down

## Related Articles
- [nginx Basic Configuration File Guide](/en/nginx-basic-config)
- [nginx 502 Bad Gateway: Causes and How to Fix It](/en/nginx-502-bad-gateway)
- [nginx Reverse Proxy Setup: Expose a Node.js App on Port 80/443](/en/nginx-reverse-proxy)
- [Monitor Linux Logs in Real Time with tail -f](/en/linux-tail-log)
- [How to Search Files with grep and find on Linux](/en/linux-grep-find)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
