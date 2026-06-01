---
title: 'How to Schedule Cron Jobs on Linux for Automated Task Execution'
date: '2026-05-21'
category: 'Linux'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn how to configure cron jobs with crontab on Linux to run scripts automatically. Covers cron expression syntax and log checking.'
---

## What I Wanted to Do

I wanted to run scripts automatically on a schedule on Linux.
With cron, you can set commands to execute automatically at specified times.

## Environment

- Linux (Ubuntu / Debian)
- WSL2

## Cron Basics

### Editing crontab

```bash
crontab -e    # Edit the current user's crontab
crontab -l    # Display current settings
crontab -r    # Delete crontab
```

### Cron expression syntax

```
minute hour day month weekday command
*      *    *   *     *
```

### Common configuration examples

```bash
# Backup every day at 2 AM
0 2 * * * /home/user/backup.sh

# Run every Monday at 9 AM
0 9 * * 1 /home/user/weekly.sh

# Run at minute 0 of every hour
0 * * * * /home/user/hourly.sh

# Run every 5 minutes
*/5 * * * * /home/user/check.sh

# Run on the 1st of every month at midnight
0 0 1 * * /home/user/monthly.sh
```

## Real Configuration Example

```bash
crontab -e
```

When the editor opens, add the following:

```
# Delete log files daily
0 3 * * * find /var/log/myapp -name "*.log" -mtime +7 -delete

# Run script every minute and log the output
* * * * * /home/user/script.sh >> /var/log/cron.log 2>&1
```

## Checking Cron Logs

```bash
grep CRON /var/log/syslog
tail -f /var/log/cron.log
```

## Common Pitfalls

- Specify commands with their full path in cron (e.g. `/usr/bin/python3`)
- Environment variables are not inherited in cron
- Adding `2>&1` also captures error output in logs
- `*/5` means "every multiple of 5 minutes"

To check cron logs in real time, use [How to Monitor Logs in Real Time with tail -f on Linux](/en/linux-tail-log).

## Related Articles

- [Essential Linux Commands (ls/cd/mkdir/rm) Cheat Sheet](/en/linux-basic-commands)
- [How to Monitor Logs in Real Time with tail -f on Linux](/en/linux-tail-log)
- [How to Set Up Scheduled Execution with GitHub Actions](/en/github-actions-schedule)
- [How to Fix Permission Denied Errors on Linux](/en/linux-permission-denied)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
