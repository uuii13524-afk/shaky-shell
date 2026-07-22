---
title: 'How to Fix npm EACCES Permission Denied Error'
date: '2026-07-22'
category: 'Node.js'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Node.js', 'npm', 'EACCES', '権限エラー']
en_tags: ['Node.js', 'npm', 'EACCES', 'permission denied']
---

## What I Was Trying to Do

I'd just spun up a fresh Ubuntu droplet and installed Node.js through the NodeSource setup script, the same way I always do. The next step was pulling in `pm2` globally so I could keep a small API process alive, so I ran `npm install -g pm2`. Instead of the usual install log, npm refused to even start and dumped a permission error.

```text
npm error code EACCES
npm error syscall mkdir
npm error path /usr/lib/node_modules/pm2
npm error errno -13
npm error Error: EACCES: permission denied, mkdir '/usr/lib/node_modules/pm2'
npm error [Error: EACCES: permission denied, mkdir '/usr/lib/node_modules/pm2'] {
npm error   errno: -13,
npm error   code: 'EACCES',
npm error   syscall: 'mkdir',
npm error   path: '/usr/lib/node_modules/pm2'
npm error }
npm error
npm error The operation was rejected by your operating system.
npm error It's possible that the file was already in use (by a text editor or antivirus),
npm error or that you lack permissions to access it.
npm error
npm error If you believe this might be a permission issue, please double-check the
npm error permissions of the file and its containing directories, or try running
npm error the command again as root/Administrator.
npm error A complete log of this run can be found in: /home/user/.npm/_logs/2026-07-22T02_14_08_211Z-debug-0.log
```

The exact same command worked fine on my local machine, so at first I had no idea why the server was rejecting it.

## Environment

- OS: Ubuntu 22.04.4 LTS (DigitalOcean droplet)
- Node.js: v20.11.1 (installed via the NodeSource setup_20.x script through apt)
- npm: 10.2.4
- Logged in as: deploy (has sudo access, not root itself)

## What I Tried

Looking at the `mkdir '/usr/lib/node_modules/pm2'` line in the error, I assumed I just needed to loosen the permissions on that directory, so I tried forcing it open with `chmod`.

```bash
chmod -R 777 /usr/lib/node_modules
```

```text
chmod: changing permissions of '/usr/lib/node_modules': Operation not permitted
```

Even `chmod` itself got rejected with `Operation not permitted`. The directory is owned by root, and the `deploy` user doesn't have permission to change its permissions either, let alone write into it. I knew prefixing the command with `sudo` would work, but running `sudo npm install -g` for every single global package felt like an accident waiting to happen, so I looked into what was actually causing this.

## Why This Happens

When Node.js is installed through the NodeSource setup script or a distro package manager like apt, npm's global install location (its `prefix`) defaults to a system directory — `/usr/lib/node_modules`, with executables landing in `/usr/bin`. That directory belongs to root by design, since it's meant for OS-level packages, so a regular user hits `EACCES` the moment npm tries to create a file there.

Running the command with `sudo` makes the error go away, but it does so by writing as root, not by fixing anything. The underlying issue — that the global install location sits outside what your regular user account can write to — is still there.

## Solution

### 1. Check the current prefix

```bash
npm config get prefix
```

```text
/usr
```

Anything under `/usr` is system-administrator territory, which is exactly why a normal user account can't write there.

### 2. Point npm at a directory you actually own

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
```

`npm config set prefix` changes where future global installs land, pointing it at a folder inside your home directory instead. Since you own that folder, no `sudo` is required to write to it.

### 3. Add the new global bin directory to PATH

```bash
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

```text
(no output — sourcing succeeds silently and the change takes effect immediately)
```

Executables like the `pm2` CLI get installed into `~/.npm-global/bin`. Without adding that directory to `PATH`, the package installs fine but the shell still can't find the command.

### 4. Reinstall without sudo

```bash
npm install -g pm2
```

```text
added 39 packages in 4s

7 packages are looking for funding
  run `npm fund` for details
```

```bash
which pm2
```

```text
/home/deploy/.npm-global/bin/pm2
```

The install completed without `sudo`, and `which pm2` confirms it resolved to `~/.npm-global/bin/pm2`. From here on, `npm install -g` only ever writes inside your home directory, so `EACCES` doesn't come back.

## Gotchas

- Trying `chmod -R 777` to force the issue open just got rejected with `Operation not permitted` — a directory owned by root can't have its permissions changed by a regular user, not even to read them into a more permissive state.
- `sudo npm install -g` looked like a fix at first, but every subsequent global install started prompting for the sudo password again, which broke a deploy script I was trying to automate. sudo is a workaround, not a fix — changing the prefix is what actually solves it.
- Right after running `npm config set prefix`, I tried `pm2 --version` immediately and got `command not found`. The config change takes effect right away, but the shell's `PATH` doesn't update until you `source ~/.bashrc` or open a new terminal.
- Packages I'd previously installed with `sudo npm install -g` (under the old `/usr/lib/node_modules` prefix) stopped showing up in `npm list -g` after switching prefixes. Global packages installed under the old and new prefixes live in separate locations, so anything from before the switch needs to be reinstalled.

## FAQ

**Q: Is it fine to just keep using `sudo npm install -g`?**
It works, but root-owned files pile up over time, and the same `EACCES` error tends to resurface later when you try to update or uninstall something as a regular user. Many CI environments don't allow `sudo` at all either, so switching the prefix or moving to nvm is the safer long-term fix.

**Q: Does this happen with nvm too?**
Generally no. nvm installs each Node.js version entirely under your home directory (`~/.nvm/versions/node/...`), so the global install location is already something your user account owns from the start. If you're setting up a new server, installing Node through nvm instead of apt avoids this problem altogether.

```bash
nvm install 20
nvm use 20
npm install -g pm2
```

**Q: What happens to my existing global packages after changing the prefix?**
Nothing moves automatically. Run `npm list -g --depth=0` before switching to note what's installed under the old prefix, then reinstall those same packages with the same command once the new prefix is active.

```bash
npm list -g --depth=0
```

## Related Articles

- [How to Clear the npm Cache to Fix Install Problems](/en/npm-cache-clear)
- [Managing Node.js Versions with nvm](/en/node-version-management-nvm)
- [Getting More Out of package.json Scripts](/en/npm-package-json-scripts)
- [How to Fix Permission Denied Errors on Linux](/en/linux-permission-denied)
- [npm vs yarn: Command Differences and When to Use Each](/en/npm-vs-yarn)
