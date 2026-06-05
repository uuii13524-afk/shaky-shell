---
title: 'How to Build and Push Docker Images to Docker Hub with GitHub Actions'
date: '2026-06-05'
category: 'GitHub Actions'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['GitHub Actions', 'Docker', 'CI/CD', 'Docker Hub', '自動化']
en_tags: ['GitHub Actions', 'Docker', 'CI/CD', 'Docker Hub', 'automation']
description: 'Learn how to automate Docker image builds and push to Docker Hub with GitHub Actions. Covers Docker Hub access tokens, Secrets setup, and PR-only build checks.'
---

## What I Wanted to Do

I wanted to automatically build and push a Docker image to Docker Hub every time I pushed code to main.
Manually running builds every time got old fast, so I set up GitHub Actions to handle it.

## Register Docker Hub Credentials as Secrets

First, create an access token from Docker Hub: Account Settings → Security → New Access Token.

In your GitHub repository, go to Settings → Secrets and variables → Actions and add:

- `DOCKERHUB_USERNAME`: your Docker Hub username
- `DOCKERHUB_TOKEN`: the access token you just created

Always use an Access Token, not your password.

## Create the Workflow File

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/docker-push.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
```

## Tag Images with the Git SHA

Using only `latest` makes it hard to trace which commit produced a given image.
Add the commit SHA as an extra tag so every image is traceable:

```yaml
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}
```

## Build-Only Check on Pull Requests

Before merging into main, it's handy to verify the build passes without actually pushing the image.
Set `push: false` for pull request events:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name == 'push' }}
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-app:latest
```

## Things That Tripped Me Up

- Using your Docker Hub password instead of an Access Token causes an authentication error
- `docker/build-push-action` expects the Dockerfile in the repo root. Use `context` or `file` to point elsewhere
- Hardcoding your username in `tags` will break if you update Secrets. Always read it from Secrets
- GitHub Actions free tier: unlimited minutes for public repos, 2,000 minutes/month for private repos

## Related Articles

- [GitHub Actions: How to Set Up Basic Auto-Deploy](/en/github-actions-basic)
- [Managing Secrets in GitHub Actions](/en/github-actions-secrets)
- [Dockerfile Basics: FROM, RUN, COPY, CMD, EXPOSE](/en/docker-dockerfile-basics)
- [Set Up Docker on a VPS (Ubuntu)](/en/vps-docker-setup)
- [Docker Basic Commands Cheatsheet (run/stop/rm/ps)](/en/docker-basic-commands)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
