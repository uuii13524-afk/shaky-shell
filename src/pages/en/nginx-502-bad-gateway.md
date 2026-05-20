---
title: 'nginx 502 Bad Gateway: Causes and How to Fix It'
date: '2026-05-20'
category: 'nginx'
---

## Symptoms

```
502 Bad Gateway
nginx/1.xx.x
```

This error means nginx received an invalid response from the upstream server.

## Cause 1: Backend Service Is Not Running

The most common cause. nginx is trying to forward requests but nothing is listening.

### Check

```bash
systemctl status your-app
docker ps
```

### Fix

```bash
systemctl start your-app
docker start container-name
```

## Cause 2: Wrong Port in nginx Config

```nginx
# Wrong
proxy_pass http://localhost:3001;

# Correct
proxy_pass http://localhost:3000;
```

## Cause 3: Wrong Hostname in Docker Environment

In docker-compose, services cannot reach each other via `localhost`. Use the service name instead.

```nginx
# Wrong
proxy_pass http://localhost:3000;

# Correct (use the service name from docker-compose.yml)
proxy_pass http://app:3000;
```

## Check the Error Log

```bash
tail -f /var/log/nginx/error.log
```

## Key Points

- In Docker, always use service names instead of `localhost` for inter-container communication
- The backend not running is the most common cause
- Always run `nginx -t` before reloading config

## Related Articles

- [nginx Basic Config File Explained](/posts/nginx-basic-config)
- [How to Use docker-compose](/posts/docker-compose-basic)
- [Docker Port Already in Use Error](/posts/docker-port-already-in-use)
