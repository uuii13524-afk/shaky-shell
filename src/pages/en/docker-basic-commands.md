---
title: 'Docker Basic Commands Cheatsheet (run/stop/rm/ps)'
date: '2026-05-12'
category: 'Docker'
---

## Container Operations

```bash
docker run -d -p 8080:80 --name myapp nginx   # Start container
docker ps                                      # List running containers
docker ps -a                                   # List all containers
docker stop myapp                              # Stop container
docker start myapp                             # Start stopped container
docker rm myapp                                # Remove container
docker rm -f myapp                             # Force remove
docker exec -it myapp bash                     # Enter container shell
docker logs -f myapp                           # Follow logs
```

## Image Operations

```bash
docker images                    # List images
docker pull nginx                # Pull image
docker rmi image-id              # Remove image
docker build -t myapp .          # Build from Dockerfile
```

## Cleanup

```bash
docker system prune              # Remove unused resources
docker system prune -a           # Remove everything unused
```

## Key Points

- Without `-d`, the container runs in the foreground and blocks your terminal
- Port format is `-p host-port:container-port`
- You only need the first few characters of a container ID
- `docker ps` only shows running containers — use `docker ps -a` for all

## Related Articles

- [How to Install Docker on Windows](/en/docker-install-windows)
- [nginx 502 Bad Gateway Fix](/en/nginx-502-bad-gateway)
- [GitHub Actions Auto-Deploy Setup](/en/github-actions-basic)
