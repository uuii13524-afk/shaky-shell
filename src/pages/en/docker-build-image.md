---
title: 'docker build Command Guide: Build Docker Images from a Dockerfile'
date: '2026-06-27'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
en_tags: ['docker build', 'Dockerfile', 'Docker image', 'docker']
description: 'Learn how to use docker build to create images from a Dockerfile. Covers tagging, build context, caching, build args, and multi-stage builds.'
---

## Quick Answer

```bash
# Build an image from the Dockerfile in the current directory
docker build -t myapp:latest .

# Specify a Dockerfile path explicitly
docker build -t myapp:latest -f ./docker/Dockerfile .
```

---

## What You're Trying to Do

You've written a Dockerfile and now want to build a Docker image from it. The `docker build` command is what you need — it reads your Dockerfile and produces an image you can run as a container.

This guide covers everything from the basics to advanced techniques like multi-stage builds and cache control.

---

## Environment

- Docker Engine 24.x or later
- OS: Ubuntu 22.04 / macOS / Windows (WSL2)

---

## Solution

### Basic Build

Start with a simple Dockerfile:

```dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
```

Run the build command:

```bash
# The trailing dot (.) sets the build context to the current directory
docker build -t myapp:latest .
```

### Tagging Images

```bash
# Name and tag with -t
docker build -t myapp:1.0.0 .

# Apply multiple tags in one build
docker build -t myapp:latest -t myapp:1.0.0 .

# Full registry path
docker build -t ghcr.io/yourname/myapp:latest .
```

### Specifying a Custom Dockerfile Path

```bash
# -f points to the Dockerfile
docker build -t myapp:latest -f ./docker/Dockerfile .

# Use a different directory as build context
docker build -t myapp:latest -f Dockerfile /path/to/context
```

### Passing Build Arguments

```dockerfile
# Define ARG in Dockerfile
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV
```

```bash
# Inject a value at build time with --build-arg
docker build --build-arg NODE_ENV=development -t myapp:dev .
```

### Disabling the Cache for a Clean Build

```bash
# --no-cache rebuilds every layer from scratch
docker build --no-cache -t myapp:latest .
```

### Multi-Stage Builds for Smaller Images

```dockerfile
# Dockerfile (multi-stage)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```bash
# Build normally — only the final stage becomes the image
docker build -t myapp:slim .

# Stop at a specific stage
docker build --target builder -t myapp:builder .
```

### Verifying the Built Image

```bash
# List images
docker images

# Inspect image metadata
docker inspect myapp:latest

# Check image size
docker images myapp
```

---

## Common Errors

### `COPY failed: file not found`

```
COPY failed: COPY instruction failed: failed to copy './src': 
no such file or directory
```

**Cause**: The file doesn't exist in the build context, or is excluded by `.dockerignore`.

**Fix**:
```bash
# Check what's in the build context
ls -la

# Review your .dockerignore
cat .dockerignore
```

### `failed to read dockerfile`

```
failed to solve with frontend dockerfile.v0: 
failed to read dockerfile: open Dockerfile: no such file or directory
```

**Cause**: No `Dockerfile` found in the current directory.

**Fix**:
```bash
ls Dockerfile

# Or point to it explicitly
docker build -f ./path/to/Dockerfile -t myapp .
```

### `pull access denied`

```
pull access denied for baseimage, repository does not exist 
or may require 'docker login'
```

**Cause**: The base image name is wrong, or you need to authenticate to a private registry.

**Fix**:
```bash
docker login

# Verify the image name
docker pull node:20-alpine
```

### `no space left on device`

**Cause**: Build cache and accumulated images are filling the disk.

**Fix**:
```bash
# Remove unused build cache
docker builder prune

# Remove all unused images and containers
docker system prune -a
```

---

## FAQ

**Q: What does the dot (.) at the end of `docker build` mean?**
It sets the build context — the directory Docker sends to the daemon. Only files within that directory can be referenced by `COPY` or `ADD` instructions.

**Q: How do I speed up slow builds caused by a large build context?**
Create a `.dockerignore` file to exclude unnecessary files. Ignoring `node_modules`, `.git`, and `dist` typically gives the biggest speedup.

```
# .dockerignore
node_modules
.git
dist
*.log
.env
```

**Q: What happens if I skip the `-t` flag?**
The image gets a `<none>` tag. You can add a tag later with `docker tag`, but it's better practice to always use `-t` upfront.

**Q: Why use multi-stage builds?**
They keep build-time tools (compilers, dev dependencies) out of the final image, dramatically reducing its size and attack surface.

**Q: What's the difference between `docker build` and `docker buildx build`?**
`docker buildx` uses BuildKit and supports multi-platform builds (AMD64/ARM64), advanced caching, and more. For most projects `docker build` is sufficient.

**Q: How can I maximize cache hits during builds?**
Put rarely-changing layers first (e.g., `COPY package*.json` then `RUN npm install`) and frequently-changing source code last. Docker only invalidates cache from the first changed layer downward.

---

## Related Articles

- [docker exec: Enter a Running Container](/en/docker-exec-bash)
- [docker logs: View Container Logs](/en/docker-logs)
- [Dockerfile Basics: Writing Your First Dockerfile](/en/docker-dockerfile-basics)
- [docker-compose Basics](/en/docker-compose-basic)
- [How to Delete Docker Images and Containers](/en/docker-delete-image-container)

## Recommended VPS / Hosting

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
