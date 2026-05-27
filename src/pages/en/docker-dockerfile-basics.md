---
title: 'Dockerfile Basics: FROM, RUN, COPY, CMD, EXPOSE'
date: '2026-05-18'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'Learn the basic Dockerfile instructions: FROM, RUN, COPY, CMD, and EXPOSE. Includes a build walkthrough and practical example.'
---

## Basic Dockerfile Structure

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "server.js"]
```

## .dockerignore File

```
node_modules
dist
.env
.git
*.log
```

## Build and Run the Image

```bash
docker build -t myapp .
docker run -d -p 3000:3000 myapp
```

## Key Points

- Separating `COPY package*.json ./` and `RUN npm ci` into two steps enables layer caching
- Without `.dockerignore`, `node_modules` gets copied and the image becomes huge

If you want to auto-deploy the image built from a Dockerfile via CI/CD, combining it with [GitHub Actions: How to Set Up Basic Auto-Deploy](/en/github-actions-basic) will greatly improve efficiency.

## Related Articles

- [Docker Basic Commands Cheatsheet](/en/docker-basic-commands)
- [How to Use docker-compose](/en/docker-compose-basic)
- [How to Persist Data with Docker Volumes](/en/docker-volume-basics)
- [How to Install Docker on Windows](/en/docker-install-windows)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
