---
title: 'docker tag Command Guide: Tagging Images and Pushing to a Registry'
date: '2026-07-07'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['Docker', 'docker tag', 'image management']
description: 'Learn how to use docker tag to rename images and add version tags before pushing to Docker Hub or a private registry, including naming rules and common errors.'
---

## Quick Answer

```bash
# Tag an image
docker tag <source-image>:<tag> <new-image-name>:<tag>

# Example: tag for a registry and push
docker tag myapp:latest myuser/myapp:1.0.0
docker push myuser/myapp:1.0.0
```

---

## What You're Trying to Do

You built an image locally and tried to push it to Docker Hub or a private registry, only to get `denied: requested access to the resource is denied`. This is usually the moment people discover `docker tag`.

Docker decides where to push based on the image's repository name. A locally built image like `myapp:latest` doesn't include a registry username or repository path, so it can't be pushed as-is. You need `docker tag` to give it a name the registry recognizes.

---

## Environment

- Docker: verified on 20.10 and later
- OS: Linux / macOS / Windows (WSL2)

---

## Solution

### 1. Basic Syntax

```bash
docker tag <SOURCE_IMAGE>[:TAG] <TARGET_IMAGE>[:TAG]
```

`docker tag` doesn't duplicate the image — it just adds a new name (reference) pointing to the same underlying image ID. It doesn't use any extra disk space.

### 2. Tagging for Docker Hub

```bash
# Format: <docker-hub-username>/<repository>:<tag>
docker tag myapp:latest myuser/myapp:1.0.0

# Push it
docker push myuser/myapp:1.0.0
```

### 3. Tagging for a Private Registry

```bash
# Format: <registry-hostname>/<repository>:<tag>
docker tag myapp:latest registry.example.com/myteam/myapp:1.0.0

docker push registry.example.com/myteam/myapp:1.0.0
```

Including the hostname tells Docker which registry to push to.

### 4. Adding Multiple Tags to the Same Image

```bash
docker tag myapp:latest myuser/myapp:1.0.0
docker tag myapp:latest myuser/myapp:latest
```

Tagging both a version number and `latest` lets consumers pin a specific version or always pull the newest one.

### 5. Tagging Directly From an Image ID

```bash
docker images
# Note the IMAGE ID, then:
docker tag a1b2c3d4e5f6 myuser/myapp:1.0.0
```

This works even if the source image has no name or shows as `<none>` — just reference it by IMAGE ID.

### 6. Verifying the Tags You Added

```bash
docker images myuser/myapp
```

Multiple tags pointing at the same IMAGE ID share the same underlying data, so disk usage doesn't grow.

---

## Common Errors

### `denied: requested access to the resource is denied`

This usually means the tag doesn't include your username or registry, or you aren't logged in.

```bash
docker login
docker tag myapp:latest myuser/myapp:1.0.0
docker push myuser/myapp:1.0.0
```

### `Error response from daemon: No such image`

The source image name or tag is wrong. Check the exact name and tag with:

```bash
docker images
```

### You Updated `latest` But an Old Image Still Gets Pulled

`latest` isn't a special "newest version" marker — it's just a regular string tag. If a cached copy exists locally, a pull can still resolve to the older image. Pull explicitly by digest or version tag, or remove the stale local image first.

### Invalid Characters in the Tag Name

Tag names can only contain letters, digits, periods, underscores, and hyphens. Repository names must also be lowercase — Docker Hub rejects uppercase characters.

---

## FAQ

**Q: Does `docker tag` copy the image?**
No. It doesn't duplicate the underlying data — it just adds a new name (reference) pointing to the same image ID, so disk usage doesn't increase.

**Q: What happens if I run `docker push` without a tag?**
Omitting the tag defaults to `latest`. To avoid accidentally overwriting the wrong tag, it's best to specify a version explicitly.

**Q: How do I remove a tag I added by mistake?**
Run `docker rmi myuser/myapp:1.0.0` to remove just that tag (reference). The underlying image stays as long as other tags still point to it.

**Q: What's a common convention for version numbers?**
Semantic versioning (e.g. `1.0.0`) is the most common approach, often combined with alias tags like `latest` or `stable`.

**Q: What's the difference between `docker tag` and `docker commit`?**
`docker tag` just adds an alias to an existing image. `docker commit` creates a brand-new image from a running container's current state. They serve different purposes.

---

## Related Articles

- [docker ps Command Guide](/en/docker-ps-command)
- [How to Build an Image With docker build](/en/docker-build-image)
- [Cleaning Up Docker Images](/en/docker-image-cleanup)

## Recommended VPS / Hosting

Build your production environment on a reliable VPS:
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
