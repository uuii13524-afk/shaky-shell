---
title: 'How to Fix Cloudflare Pages Disconnected from GitHub (All Error Messages)'
date: '2026-05-01'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Fix every Cloudflare Pages GitHub disconnection error — from suspended installations to deleted repos. Step-by-step solutions for all 6 warning messages.'
---

## Quick Answer

Go to **Cloudflare Dashboard → Pages → your project → Settings → Git repository → Manage** and reinstall the GitHub integration. This resolves most disconnection issues in under 2 minutes.

---

## Symptoms

Git push does not trigger a deployment on Cloudflare Pages. One of the following warning banners appears in the **Deployments** tab:

- `This project is disconnected from your Git account, this may cause deployments to fail.`
- `Cloudflare Pages is not properly installed on your Git account, this may cause deployments to fail.`
- `The Cloudflare Pages installation has been suspended, this may cause deployments to fail.`
- `The project is linked to a repository that no longer exists, this may cause deployments to fail.`
- `The repository cannot be accessed, this may cause deployments to fail.`
- `There is an internal issue with your Cloudflare Pages Git installation.`

---

## Fix by Error Message

### "This project is disconnected from your Git account"

The most common error. The OAuth token between Cloudflare and GitHub has expired or been revoked.

**Steps:**

1. Open your project in the Cloudflare dashboard
2. Go to **Settings → Git repository → Manage**
3. Click **Uninstall** to remove the current GitHub app installation
4. Click **Install** again and re-authorize Cloudflare Pages on GitHub
5. Push an empty commit to verify the connection:

```bash
git commit --allow-empty -m "reconnect cloudflare"
git push
```

---

### "The Cloudflare Pages installation has been suspended"

Someone manually suspended the Cloudflare Pages app in GitHub settings.

**Steps:**

1. Open GitHub installation settings:
   - Personal account: `https://github.com/settings/installations`
   - Organization: `https://github.com/organizations/YOUR_ORG/settings/installations`
2. Find **Cloudflare Pages** and click **Configure**
3. Scroll to the bottom and click **Unsuspend**
4. Return to Cloudflare dashboard and push a new commit

---

### "The repository cannot be accessed"

Cloudflare Pages no longer has read access to the specific repository — usually because the GitHub App's repository scope was changed.

**Steps:**

1. Go to GitHub installation settings (same URLs as above)
2. Click **Configure** on Cloudflare Pages
3. Under **Repository access**, switch to **All repositories** or manually add the missing repo
4. Save and redeploy

---

### "The project is linked to a repository that no longer exists"

The GitHub repository was deleted or transferred to another account.

**If deleted:** Create a new Cloudflare Pages project pointing to a new repository.

**If transferred:**
- Option A: Transfer the repository back to the original account
- Option B: Delete the current Pages project and create a new one pointing to the new repository location

---

### "There is an internal issue with your Cloudflare Pages Git installation"

An internal Cloudflare error. Uninstall and reinstall the GitHub app first. If that does not work, [contact Cloudflare support](https://support.cloudflare.com/).

---

### GitHub/GitLab is having an incident

No action needed on your end. Monitor [GitHub Status](https://www.githubstatus.com/) or [GitLab Status](https://status.gitlab.com/) and retry once the incident is resolved.

---

## Environment

- Cloudflare Pages
- GitHub (also applies to GitLab)
- Any frontend framework (Astro, Next.js, React, etc.)

---

## How to Force a Deployment Without Code Changes

If you need to trigger a build immediately after reconnecting:

```bash
git commit --allow-empty -m "force deploy"
git push
```

Or use the Cloudflare dashboard: **Deployments → Create deployment → Deploy without code changes**.

---

## Prevention

| Scenario | Prevention |
|---|---|
| Token expiry | Check the Deployments tab after any GitHub permission change |
| Suspended installation | Avoid touching GitHub App settings unless necessary |
| Deleted repo | Always disconnect Cloudflare Pages before deleting a repo |

If a deployment is not reflected, always check the **Deployments tab logs** first before assuming a GitHub disconnect. For log reading tips, see [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log).

---

## FAQ

**Q: Why does Cloudflare Pages disconnect from GitHub?**
The most common causes are token expiry, manually revoking app permissions in GitHub, or suspending the Cloudflare Pages GitHub App installation.

**Q: How do I reconnect Cloudflare Pages to GitHub?**
Go to Cloudflare Dashboard → your Pages project → Settings → Git repository → Manage → Uninstall, then reinstall and re-authorize.

**Q: My git push still doesn't trigger a deployment after reconnecting.**
Push an empty commit (`git commit --allow-empty -m "test" && git push`) to force a deployment check. If that fails, check that your branch name matches the production branch in Settings.

**Q: Does this also apply to GitLab?**
Yes. The reconnection steps are the same — go to GitLab installation settings at `https://gitlab.com/-/profile/applications` instead.

---

## Related Articles

- [Cloudflare Pages GitHub Auto-Deploy Not Working: How to Fix It](/en/cloudflare-pages-deploy-not-working)
- [How to Read Cloudflare Pages Build Logs and Fix Errors](/en/cloudflare-pages-build-log)
- [How to Deploy Astro to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [Full Steps to Set an Xserver Domain as a Cloudflare Pages Custom Domain](/en/xserver-cloudflare-full-setup)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
