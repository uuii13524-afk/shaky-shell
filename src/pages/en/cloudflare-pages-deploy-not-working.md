---
title: 'Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It'
date: '2026-05-20'
category: 'Cloudflare'
---

## Symptoms

Git push does not trigger a new deployment on Cloudflare Pages.
No new entries appear in the Deployments tab.
You may also see this warning message:

```
This project is disconnected from your Git account.
This may cause deployments to fail.
```

## Environment

- Cloudflare Pages
- GitHub
- Astro

## Cause 1: Cloudflare Lost Connection to GitHub

### How to Check

Go to Cloudflare Dashboard → Your Project → Settings → Git repository.
If there is a warning next to the "Manage" button, the connection is broken.

### Fix

1. Click "Manage" under Git repository
2. Re-authenticate your GitHub account
3. Force a new deployment by pushing an empty commit

```
git commit --allow-empty -m "force deploy"
git push
```

## Cause 2: Old Commit Being Deployed

If the build log shows something like this, an old commit is being used instead of the latest one:

```
HEAD is now at 3218655 first commit
```

### Fix

Push an empty commit to trigger a fresh deployment:

```
git commit --allow-empty -m "force deploy"
git push
```

## Cause 3: Build Error

Open the build log from the Deployments tab and look for lines starting with `[ERROR]` or `Failed`.

## Tips

- An empty commit push is the most reliable way to force a redeployment
- Always check the build log first when a deployment does not appear
- Use `git log --oneline` to verify your latest commit was pushed correctly

## Prevention Checklist

```
1. Check if a new deployment appears in the Deployments tab
2. Look for errors in the build log
3. Verify the GitHub connection status in Settings
4. Push an empty commit to force redeployment
```

## Related Articles

- [Cloudflare Pages Disconnected from GitHub Account](/posts/cloudflare-github-disconnect)
- [How to Read Cloudflare Pages Build Logs](/posts/cloudflare-pages-build-log)
- [How to Deploy Astro to Cloudflare Pages](/posts/astro-cloudflare-deploy)
