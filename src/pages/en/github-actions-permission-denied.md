---
title: 'How to Fix "Permission denied" on git push in GitHub Actions'
date: '2026-07-15'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub Actions', 'git push', 'Permission denied', 'GITHUB_TOKEN']
en_tags: ['GitHub Actions', 'git push', 'permission denied', 'GITHUB_TOKEN']
---

## What I Was Trying to Do

I'd wired up a workflow that runs `prettier --write` on every push to `main` and commits the formatted diff straight back into the repo. Nothing fancy — I'd run the exact same command sequence locally a dozen times without issue, so I expected the workflow to just format, commit, and push.

The formatting step ran fine, but the job failed right at the final `git push`, with this in the Actions log:

```text
remote: Permission to my-org/my-repo.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/my-org/my-repo/': The requested URL returned error: 403
```

`git push` worked fine from my own machine against the same repo, so this was clearly something specific to how Actions authenticates — but whether it was a git config issue or a token scope issue wasn't obvious at first.

## Environment

- GitHub Actions, `ubuntu-latest` runner
- `actions/checkout@v4`
- Trigger: `push` on `main`
- Auth: the default auto-generated `${{ secrets.GITHUB_TOKEN }}` (no PAT configured)
- Repository created after GitHub's 2023 default-permissions change (workflow permissions default to read-only)

## What I Tried

First I dropped `git remote -v` in right before the push step to sanity-check the remote URL. It printed `https://github.com/my-org/my-repo.git` — correct, so the URL wasn't the problem. That pointed at credentials rather than configuration.

Next I assumed the bot's identity wasn't set correctly and added:

```yaml
- name: Configure git
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
```

Same 403 on the next run. At that point it clicked that `user.name`/`user.email` only control commit authorship — they have nothing to do with the credentials used to authenticate the push. So I moved on to the token itself.

I generated a personal access token, saved it as `secrets.PAT`, and figured that alone would fix it. It didn't — I'd forgotten to actually pass it to `actions/checkout`'s `token:` input. Without that, the checkout step still caches the default `GITHUB_TOKEN`'s (read-only) credentials for every git command that follows, so the push kept failing with the identical error even though a working token existed in secrets.

## Why This Happens

The `GITHUB_TOKEN` that Actions generates for a run has its write access controlled in two places at once, and both have to agree.

The first is the repository-wide default under **Settings → Actions → General → Workflow permissions**. Any repository created after GitHub's February 2023 change defaults to "Read repository contents permission" — read-only — unless someone flips it manually.

The second is the `permissions:` key inside the workflow YAML itself, settable per job or per workflow. Critically, this key can only *narrow or restore* permissions within whatever the repository-wide default allows — if the repo-wide setting is read-only, or an organization policy blocks YAML from overriding it, then `permissions: contents: write` in your YAML is silently ineffective.

On top of that, `actions/checkout` caches the token's credentials into local git config (`http.https://github.com/.extraheader`) at checkout time. Whatever permission that token had *at that moment* is what every later git command uses — so raising permissions after checkout already ran doesn't retroactively fix anything.

## The Fix

Start by declaring write access explicitly at the job level:

```yaml
jobs:
  format:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: npx prettier --write .
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --cached --quiet || git commit -m "chore: auto format"
          git push
```

Scoping `permissions:` to the job (rather than the whole workflow) means only this job gets write access; every other job in the file stays read-only by default, which is the safer default when only one job actually needs to push.

Then check the repository-side setting. In the GitHub web UI, go to the repo's **Settings → Actions → General**, and look at the "Workflow permissions" section:

```text
Workflow permissions
  ( ) Read repository contents permission
  (•) Read and write permissions
```

If it's set to read-only, switch it to "Read and write permissions." That's what actually lets the `permissions: contents: write` line in your YAML take effect at all.

With both pieces in place — the YAML permission and the repo-level setting — a successful run's log looks like this:

```text
To https://github.com/my-org/my-repo.git
   a1b2c3d..e4f5g6h  main -> main
```

Once you see the commit-range line instead of a 403, the push went through. The reason both fixes were necessary is that the effective permission is an AND of the two settings — fixing only one still leaves you with a read-only token.

## Where I Got Stuck

- Fixing `git config user.name`/`user.email` didn't help at all — that's commit authorship, a completely separate concern from push authentication.
- I created `secrets.PAT` but never wired it into `actions/checkout`'s `token:` input, so every subsequent git command kept using the cached, read-only default token instead.
- I added `permissions: contents: write` to the YAML and assumed that alone would fix it, but the repository's "Workflow permissions" setting was still read-only, so the 403 kept showing up despite the YAML change — I burned a few pointless commits before realizing both settings need to agree.
- Testing the same workflow under a `pull_request` trigger from a fork still failed with 403 even with `permissions: contents: write` set. That's a separate, non-overridable restriction — forked-PR runs always get a read-only `GITHUB_TOKEN` regardless of what the YAML says.

## FAQ

**Why doesn't `permissions: contents: write` fix this on a `pull_request` workflow triggered from a fork?**
For security reasons, workflows triggered by pull requests from forks always receive a read-only `GITHUB_TOKEN`, and the `permissions:` key cannot override that. If the workflow genuinely needs to push, split the write step into a separate workflow triggered by `workflow_run` (or use `pull_request_target` carefully, understanding its security implications), rather than trying to grant write access directly on the fork-triggered workflow.

**When should I use a personal access token instead of the default `GITHUB_TOKEN`?**
For a simple push-back into the same repo, the default `GITHUB_TOKEN` is enough once permissions are configured correctly. You need a PAT (or a GitHub App token) when pushing to a different repository, when an organization policy blocks bots from pushing directly, or when you need the push to re-trigger other workflows — pushes made with the default `GITHUB_TOKEN` intentionally don't trigger downstream workflow runs, which trips people up more than the permission issue itself.

**Should `permissions:` go at the workflow level or the job level?**
Scope it to the job whenever only some jobs need write access — that keeps the rest of the workflow at the safer read-only default. Only set it at the workflow's top level if every job genuinely needs the same elevated permission.

## Related Articles

- [GitHub Actions Basics](/en/github-actions-basic)
- [Using Secrets in GitHub Actions](/en/github-actions-secrets)
- [Using Docker in GitHub Actions](/en/github-actions-docker)
- [Git Remote Operations Cheat Sheet](/en/git-remote-operations)
- [How to Add an SSH Key to GitHub](/en/ssh-key-github)
