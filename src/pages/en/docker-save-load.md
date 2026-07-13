---
title: 'docker save / load Command Guide: Exporting and Importing Images as Files'
date: '2026-07-13'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker save', 'docker load', 'image migration']
description: 'Learn how to export a Docker image to a tar file with docker save and import it with docker load, moving images between hosts without a registry.'
---

## Quick Answer

```bash
# Export an image to a tar file
docker save -o myimage.tar myimage:latest

# Load an image from a tar file
docker load -i myimage.tar
```

---

## What You're Trying to Do

You need to move a Docker image into an offline, air-gapped environment, or copy it to another server without going through Docker Hub or a private registry. That's exactly what `docker save` and `docker load` are for.

`docker push`/`docker pull` move images through a registry. `docker save`/`docker load` move them as a plain tar file instead — handy for closed networks, staging environments, or anywhere a registry isn't available or desirable.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. Export an Image to a tar File (docker save)

```bash
docker save -o myimage.tar myimage:latest
```

You can also stream to stdout and compress with `gzip`:

```bash
docker save myimage:latest | gzip > myimage.tar.gz
```

Multiple images can be bundled into a single tar file:

```bash
docker save -o images.tar myimage:latest another-image:v1
```

### 2. Transfer the File to Another Machine

```bash
scp myimage.tar user@remote-host:/tmp/
```

A USB drive or other physical media works just as well.

### 3. Load the Image from the tar File (docker load)

```bash
docker load -i myimage.tar
```

Compressed files can be loaded directly:

```bash
docker load -i myimage.tar.gz
```

You can also load from stdin:

```bash
cat myimage.tar | docker load
```

### 4. Verify the Loaded Image

```bash
docker images
```

The tag from `docker save` is preserved, so you can run it right away with the original name, e.g. `docker run myimage:latest`.

### 5. Exporting a Running Container's Filesystem (docker export)

If you only need a running container's filesystem — not the full image — use `docker export` instead.

```bash
docker export <container-name> -o container.tar
```

Load a tar file created by `docker export` with `docker import`, but note that layer history and metadata like `CMD`/`ENTRYPOINT` are not preserved.

```bash
docker import container.tar myimage:imported
```

---

## Common Errors

### `open myimage.tar: no such file or directory`

The path passed to `docker load -i` is wrong, or it's pointing somewhere other than where `docker save` wrote the file.

```bash
ls -la myimage.tar
docker load -i ./myimage.tar
```

### `Error processing tar file(exit status 1): unexpected EOF`

The transfer was interrupted and the tar file is corrupted. Re-transfer with `scp` or `rsync`, and compare file size or `sha256sum` before and after.

```bash
sha256sum myimage.tar
```

### `docker images` Shows Nothing After `docker load`

`docker load` may have run against a different Docker daemon (a different context or remote host). Check the active context.

```bash
docker context ls
docker context use default
```

### `no space left on device`

The destination has run out of disk space while extracting the tar file. Check usage with `docker system df` and clean up unused images/containers.

```bash
docker system df
docker system prune
```

---

## FAQ

**Q: What's the difference between `docker save` and `docker export`?**
`docker save` exports the full image, including its layer structure and metadata (`CMD`/`ENTRYPOINT`, environment variables, etc.). `docker export` flattens a running container's filesystem into a single layer with no metadata. Use `docker save` when you want to migrate the image as-is.

**Q: How do I reduce the tar file size?**
Compress it with `docker save myimage | gzip > myimage.tar.gz`. Trimming unnecessary layers with a multi-stage build also shrinks the underlying image size.

**Q: Can I change the tag when running `docker load`?**
`docker load` has no option to rename the tag. Re-tag it afterward with `docker tag`.

```bash
docker tag myimage:latest myimage:v2
```

**Q: Which is better, a registry or save/load?**
For ongoing image distribution, a registry (Docker Hub, ECR, GCR, etc.) with `push`/`pull` is easier to manage. For offline environments or one-off transfers, `save`/`load` is the quicker option.

**Q: If I bundle multiple images into one tar, can I load them individually?**
`docker load` always loads every image in the tar file at once. If you need to load images individually, run `docker save` separately for each one.

---

## Related Articles

- [docker inspect Command Guide](/en/docker-inspect-command)
- [Tagging Docker Images with docker tag](/en/docker-tag-command)
- [Cleaning Up Unused Docker Images](/en/docker-image-cleanup)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
