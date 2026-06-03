---
title: 'How to Set Up Rate Limiting in nginx'
date: '2026-06-03'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'レート制限', 'rate limiting', 'セキュリティ', 'DDoS対策']
en_tags: ['nginx', 'rate limiting', 'security', 'DDoS protection', 'web server']
description: 'How to configure nginx rate limiting using limit_req_zone and limit_req directives to protect against brute force attacks and excessive requests.'
---
## What I Wanted to Do
I needed to limit the number of requests to specific URLs in nginx.
Set this up to block brute force attacks on API endpoints and stop excessive requests from hitting the backend.

## Setting Up limit_req_zone

Add this to the `http` block in nginx.conf or a file under `/etc/nginx/conf.d/`.

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
}
```

- `$binary_remote_addr`: Uses the client IP address as the key
- `zone=mylimit:10m`: Zone name and shared memory size (10MB handles around 160,000 IPs)
- `rate=10r/s`: Allow up to 10 requests per second

Use `r/m` to limit by the minute instead:

```nginx
limit_req_zone $binary_remote_addr zone=loginlimit:10m rate=5r/m;
```

## Applying limit_req to an Endpoint

Apply the limit in a `server` or `location` block.

```nginx
server {
    location /api/ {
        limit_req zone=mylimit burst=20 nodelay;
        proxy_pass http://localhost:3000;
    }
}
```

- `burst=20`: Temporarily allows up to 20 requests in a burst
- `nodelay`: Process burst requests without delay — return an error immediately when exceeded

Without `nodelay`, excess requests are queued and responses are delayed rather than rejected.

## Stricter Limits for the Login Page

For brute force protection, keep the burst value small.

```nginx
location /login {
    limit_req zone=loginlimit burst=5;
    proxy_pass http://localhost:3000;
}
```

## Changing the Response Code from 503 to 429

The default is 503 (Service Unavailable), but 429 (Too Many Requests) is the correct HTTP status for rate limiting.

```nginx
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
    limit_req_status 429;
}
```

## Applying the Config

```bash
# Check syntax
sudo nginx -t

# Reload without downtime
sudo systemctl reload nginx
```

## Gotchas
- `limit_req_zone` must be in the `http` block — putting it in `server` or `location` causes an error
- Without `burst`, legitimate users can easily get blocked — tune the value based on your traffic
- Requests that hit the rate limit are logged to `/var/log/nginx/error.log`
- If clients are behind NAT or a proxy, you may need `$http_x_forwarded_for` instead of `$remote_addr`
- Use `reload` not `restart` — restart briefly stops the service

## Related Posts
- [nginx Basic Config File](/posts/nginx-basic-config)
- [nginx location Directives](/posts/nginx-location-directives)
- [nginx Reverse Proxy Setup](/posts/nginx-reverse-proxy)
- [Linux UFW Firewall Basics](/posts/linux-firewall-ufw)
- [nginx SSL with Let's Encrypt (certbot)](/posts/nginx-ssl-certbot)

## Recommended Cloud Hosting

Looking for reliable cloud infrastructure? Check out these developer-friendly services.

- <a href="https://www.awin1.com/cread.php?awinmid=88911&awinaffid=2909773&ued=https%3A%2F%2Fwww.cherryservers.com" target="_blank" rel="sponsored">Cherry Servers</a> - High-performance VPS and dedicated servers
- <a href="https://www.awin1.com/cread.php?awinmid=89935&awinaffid=2909773&ued=https%3A%2F%2Fwww.cloudways.com" target="_blank" rel="sponsored">Cloudways</a> - Managed cloud hosting for developers
