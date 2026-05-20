---
title: 'Linux Basic Commands Cheatsheet (ls/cd/mkdir/rm)'
date: '2026-05-10'
category: 'Linux'
---

## View Files and Directories

```bash
ls              # List files
ls -la          # Detailed list including hidden files
pwd             # Show current directory
```

## Navigate Directories

```bash
cd /home/user   # Absolute path
cd projects     # Relative path
cd ..           # Go up one level
cd ~            # Go to home directory
cd -            # Go back to previous directory
```

## Create Files and Directories

```bash
mkdir newfolder         # Create directory
mkdir -p a/b/c          # Create nested directories
touch newfile.txt       # Create empty file
```

## Delete Files and Directories

```bash
rm file.txt             # Delete file
rm -r folder/           # Delete directory recursively
rm -rf folder/          # Force delete without confirmation
```

## Copy and Move

```bash
cp file.txt backup.txt  # Copy file
cp -r folder/ backup/   # Copy directory
mv file.txt /tmp/       # Move file
mv old.txt new.txt      # Rename file
```

## View File Contents

```bash
cat file.txt            # Print all content
less file.txt           # Scroll through content (q to quit)
tail -f logfile.log     # Follow log in real time
head -n 10 file.txt     # Show first 10 lines
```

## Key Points

- `rm -rf` is irreversible — always double-check before running
- Linux filenames are case-sensitive
- Use `Tab` for auto-completion
- Wrap filenames with spaces in double quotes: `"my file.txt"`

## Related Articles

- [Linux Permission Denied Error Fix](/en/linux-permission-denied)
- [How to Install Docker on Windows](/en/docker-install-windows)
- [How to Install WSL2 on Windows](/posts/wsl2-install-windows)
