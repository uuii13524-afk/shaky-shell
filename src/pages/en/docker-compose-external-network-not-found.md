---
title: 'Fix: docker compose up Fails with "network ... not found"'
date: '2026-09-27'
category: 'Docker'
layout: '../../layouts/PostLayoutEn.astro'
description: 'docker compose up fails with "network app_shared_net not found" after docker network prune deletes an external network. Here is the cause and the fix.'
en_tags: ['Docker', 'Docker Compose', 'network']
---

## What I Was Trying to Do

I had two separate Compose projects — the main app and a monitoring stack (Prometheus/Grafana) — that needed to talk to each other on the same Docker network. To make that work, I manually created a shared network up front and referenced it from both Compose files with `external: true`.

```bash
docker network create app_shared_net
```

```yaml
# app's docker-compose.yml
services:
  web:
    image: myapp:latest
    networks:
      - app_shared_net

networks:
  app_shared_net:
    external: true
```

One day disk space got tight, so I ran `docker network prune` to clean up unused Docker resources. At that moment the monitoring stack happened to be running, but the app itself had been stopped earlier with `docker compose down`.

```bash
docker network prune
```

```text
WARNING! This will remove all custom networks not used by at least one container.
Are you sure you want to continue? [y/N] y
Deleted Networks:
app_shared_net
```

After the cleanup finished, I tried to bring the app back up and it failed immediately.

```bash
docker compose up -d
```

```text
Error response from daemon: network app_shared_net not found
```

## Environment

- OS: Ubuntu 24.04 LTS
- Docker Engine: 27.1.1
- Docker Compose: v2.29.1 (Compose plugin, `docker compose` command)
- Project layout: two separate Compose stacks — the app (web) and monitoring (Prometheus/Grafana)
- Network: `app_shared_net`, a manually created external network referenced by both stacks with `external: true`

## What I Tried

My first guess was a typo in `docker-compose.yml`. I went over the `networks:` block's indentation and the network name several times, but the file was correct.

Next I tried tearing everything down and starting fresh, but `docker compose down` failed too.

```bash
docker compose down
```

```text
Network app_shared_net not found.
```

Since `down` was also assuming the network should already exist, I stopped suspecting the Compose file and started suspecting the network itself was gone.

```bash
docker network ls | grep app_shared_net
```

This returned nothing. That's when it clicked that the earlier `docker network prune` had removed it.

## Root Cause

`docker network prune` removes any custom network that has zero containers currently attached to it — unconditionally. In this case, `app_shared_net` was only being used by the monitoring stack's containers, and it turned out the monitoring stack had also been briefly stopped for an unrelated reason at the exact moment I ran the prune. With no containers attached, the network qualified as "unused" and was deleted.

On the Compose side, `external: true` means "this network already exists somewhere else — don't create it for me." `docker compose up` only checks whether the named network exists; it never creates one that's marked external. So once the manually created `app_shared_net` was gone, both `up` and `down` started failing immediately, since neither of them will create or manage an external network on your behalf.

## How I Fixed It

### 1. Confirm the network is actually gone

```bash
docker network ls | grep app_shared_net
```

No output. Confirmed `app_shared_net` no longer existed.

### 2. Recreate it with the same name

This setup used the default bridge driver with no custom subnet, so recreating it was straightforward.

```bash
docker network create app_shared_net
```

```text
b6f2a1c4e8d3f7a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3
```

If you're using a custom subnet or IPAM config, you need to have recorded that from `docker network inspect` before the network was deleted — otherwise you can't reproduce it exactly. My setup used the default config, so this wasn't an issue here.

### 3. Bring the app back up

```bash
docker compose up -d
```

```text
[+] Running 2/2
 ✔ Network app_shared_net  Created
 ✔ Container myapp-web-1   Started
```

Compose reports `Network app_shared_net Created`, but that's just Compose's own bookkeeping — the actual network object is the one I created manually in step 2, and the container simply attached to it.

### 4. Verify the monitoring stack is on the same network

```bash
docker network inspect app_shared_net --format '{{range .Containers}}{{.Name}} {{end}}'
```

```text
myapp-web-1 grafana-1 prometheus-1
```

Both the app and the monitoring containers were attached to the same network again.

### 5. Prevent this from happening again

Running `docker network prune` blindly will remove a shared external network any time every container using it happens to be stopped at the same moment — exactly what happened here. I made the network creation step idempotent in the deploy script instead of assuming it already exists.

```bash
docker network inspect app_shared_net >/dev/null 2>&1 || docker network create app_shared_net
```

Putting this one-liner at the top of the deploy script means it only creates the network if it's missing, and does nothing if it's already there. I also scoped down future prune runs instead of running them unconditionally.

```bash
docker network prune --filter "label!=keep"
```

Creating the external network with a `--label keep=true` tag lets this filter exclude it from future prunes.

## Verification

After recreating the network, I restarted both stacks and confirmed cross-container communication.

```bash
docker compose exec web curl -s http://prometheus:9090/-/healthy
```

```text
Prometheus Server is Healthy.
```

The app container could resolve `prometheus` by name and reach it over HTTP, confirming the network was fully restored.

## Summary

- `docker network prune` unconditionally removes any network with zero attached containers. A network shared across multiple Compose projects can get deleted as collateral damage if all of them happen to be stopped at the same time.
- A network marked `external: true` is never created by Compose. If it's missing, both `up` and `down` fail immediately — so when you hit this, check `docker network ls` for the actual network before assuming your Compose file has a typo.
- Recovery is as simple as `docker network create` with the same name, unless you used a custom subnet, in which case you need to have recorded the original config with `docker network inspect` beforehand. Making network creation idempotent (`inspect || create`) in your setup scripts prevents this from recurring.

## Related Posts

- [Docker Networking Basics: Create and Connect Containers](/en/docker-network-basics)
- [Fixing "Found orphan containers" in docker compose](/en/docker-compose-orphan-containers)
- [How to Stop and Remove Containers with docker compose down](/en/docker-compose-down)
- [Cleaning Up Unused Docker Resources with docker system prune](/en/docker-system-prune)
