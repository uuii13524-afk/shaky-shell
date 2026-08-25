---
title: 'Fix "error: gpg failed to sign the data" on git commit'
date: '2026-08-25'
category: 'Git'
layout: '../../layouts/PostLayoutEn.astro'
description: 'git commit fails with "error: gpg failed to sign the data" in a fresh tmux or SSH session. Here is why a stale GPG_TTY causes this, and how resetting GPG_TTY and restarting gpg-agent fixes it.'
en_tags: ['Git', 'GPG', 'commit signing']
---

## What I Was Trying to Do

I sign all my commits with GPG and have `commit.gpgsign = true` set in `~/.gitconfig`. One day, after opening a new tmux pane on a VPS I'd SSH'd into, I tried to commit as usual and it failed.

```bash
git commit -m "fix: update dependencies"
```

```text
error: gpg failed to sign the data
fatal: failed to write commit object
```

Retrying the exact same commit gave the exact same error every time. A different SSH session on the same box had signed commits just fine minutes earlier, so I didn't think the repo or the GPG key itself was broken.

```bash
git commit -m "fix: update dependencies"
```

```text
error: gpg failed to sign the data
fatal: failed to write commit object
```

## Environment

- OS: Ubuntu 24.04.4 LTS
- Git: 2.51.0
- GnuPG: 2.4.4
- pinentry program: pinentry-curses
- Connection: SSH into a VPS, then `tmux new -s work` to open a fresh session
- GPG key: an existing local signing key already set as `user.signingkey`

## What I Tried

Git's error message alone wasn't enough to tell what was wrong, so I isolated the problem by calling GPG directly, without Git in the picture.

```bash
echo "test" | gpg --clearsign
```

```text
gpg: signing failed: Inappropriate ioctl for device
gpg: [stdin]: clear-sign failed: Inappropriate ioctl for device
```

So this wasn't a Git problem at all — GPG itself was failing because pinentry couldn't launch. "Inappropriate ioctl for device" is the message pinentry throws when it tries to open a prompt on a terminal (tty) it can't actually reach.

Next I checked which terminal GPG currently believed it should use for the passphrase prompt.

```bash
echo $GPG_TTY
```

```text

```

Empty. I had `export GPG_TTY=$(tty)` in `~/.bashrc` from setting this up before, so I checked that it was still there.

```bash
grep GPG_TTY ~/.bashrc
```

```text
export GPG_TTY=$(tty)
```

The line was there. Just to be sure, I checked what tty this pane actually was.

```bash
tty
```

```text
/dev/pts/3
```

So the config existed, but `GPG_TTY` wasn't set in the current shell. That meant either `.bashrc` hadn't been sourced correctly when this tmux pane started, or something had overwritten the value afterward.

## Why This Happens

When GPG needs a passphrase to sign something, pinentry tries to open its prompt on "whatever terminal you're currently using." GPG figures out which terminal that is from the `GPG_TTY` environment variable. If that variable isn't set correctly for the shell that's actually running, pinentry has nowhere to draw the prompt and fails with `Inappropriate ioctl for device`.

In my case, the `export GPG_TTY=$(tty)` line in `.bashrc` was correct, but the timing of shell initialization when `tmux new` opens a fresh pane, combined with `gpg-agent` still holding onto state from a previous session (a different tty), left `GPG_TTY` pointing at something other than this pane's `/dev/pts/3`. On top of that, `gpg-agent` runs as a long-lived background process, so it kept trying to service the new pane's signing request using stale session information from before. Nothing was wrong with the key or the Git config — the only thing out of date was which terminal pinentry thought it should talk to.

## Solution

### 1. Explicitly reset GPG_TTY in the current shell

```bash
export GPG_TTY=$(tty)
```

### 2. Confirm it's set correctly

```bash
echo $GPG_TTY
```

```text
/dev/pts/3
```

This now matched the tty of the pane I was actually working in.

### 3. Restart gpg-agent to drop stale session state

```bash
gpgconf --kill gpg-agent
```

`gpgconf --kill` shuts the agent down cleanly; a fresh instance starts automatically the next time GPG needs it.

### 4. Re-test GPG signing on its own

```bash
echo "test" | gpg --clearsign
```

```text
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512
test
-----BEGIN PGP SIGNATURE-----
...
-----END PGP SIGNATURE-----
```

The pinentry-curses passphrase prompt showed up correctly in the terminal this time, and signing succeeded.

### 5. Retry the commit

```bash
git commit -m "fix: update dependencies"
```

```text
[main a1c2e3f] fix: update dependencies
 1 file changed, 3 insertions(+), 1 deletion(-)
```

It committed without error.

### 6. A more permanent fix for the same pane setup

To avoid hitting this again every time I open a new tmux pane, I moved the `export GPG_TTY=$(tty)` line in `.bashrc` to somewhere it's guaranteed to run on shell startup, and started looking into a tmux hook along the lines of `set-hook -g pane-focus-in 'run-shell "tmux setenv GPG_TTY $(tty)"'` so the value gets refreshed whenever focus moves between panes.

## Verify It Works

```bash
git log --show-signature -1
```

```text
gpg: Signature made Tue 25 Aug 2026 10:14:02 AM UTC
gpg: using RSA key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
gpg: Good signature from "Acia <acia@example.com>" [ultimate]
commit a1c2e3f4b5d6...
Author: Acia <acia@example.com>
Date:   Tue Aug 25 10:14:02 2026 +0000

    fix: update dependencies
```

`gpg: Good signature` confirms the commit is properly signed.

## Gotchas

- Having `GPG_TTY` set in `.bashrc` doesn't guarantee it's correct in every shell you open. New tmux panes or stacked SSH sessions can end up with a stale or empty value even when the config line is right there. If the setting "should be working" but isn't, compare `echo $GPG_TTY` against the actual output of `tty` before assuming anything else is broken.
- `gpg-agent` stays running in the background and can carry state over from a previous session. When a passphrase-related error shows up for no obvious reason, resetting the agent with `gpgconf --kill gpg-agent` is a faster way to isolate the problem than second-guessing the key or Git config.
- Git's `error: gpg failed to sign the data` doesn't say much on its own. Testing GPG directly with something like `echo test | gpg --clearsign`, outside of Git entirely, narrows down the actual failure much faster than trying to debug through `git commit`.

## FAQ

**Q: Is there a way to avoid typing `export GPG_TTY=$(tty)` by hand every time?**
Putting it in your shell's startup file (`.bashrc` or `.zshrc`) normally handles this automatically. In environments that reuse multiple pseudo-terminals, like tmux or screen, the value can drift when you switch panes, so a tmux hook that re-exports it on focus change is the more reliable setup.

**Q: Does `gpgconf --kill gpg-agent` wipe out a cached passphrase?**
Yes. You'll be prompted for it again the next time you sign something, but the key itself isn't touched, so it's safe to run.

**Q: Is there a way to commit without signing, just to get unblocked?**
`git commit --no-gpg-sign` skips signing for that one commit. If the repository requires signed commits, though, you'll eventually need to re-sign it anyway, so fixing the root cause is usually faster in the end.

## Related Articles

- [How to Undo a Git Commit](/en/git-commit-undo)
- [Basic git remote Operations](/en/git-remote-operations)
- [Adding an SSH Key to GitHub](/en/ssh-key-github)
- [Setting Environment Variables on Linux](/en/linux-env-variables)
