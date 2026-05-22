---
title: "How to Set Up a Free SSL Certificate on nginx with certbot (Let's Encrypt)"
date: '2026-05-22'
category: 'nginx'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['nginx', 'SSL', 'certbot', 'HTTPS', "Let's Encrypt"]
en_tags: ['nginx', 'SSL', 'certbot', 'HTTPS', "Let's Encrypt"]
---

## What I Wanted to Do

I wanted to set up an SSL certificate on nginx running on a VPS so it could be accessed over HTTPS.
Let's Encrypt certificates are free and can be obtained easily with certbot.

## Installing certbot

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

## Obtaining an SSL Certificate

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

It runs interactively — just enter your email address and choose to redirect HTTP to HTTPS.

```
Enter email address: your@email.com
(A)gree/(C)ancel: A
(Y)es/(N)o: N
Select the appropriate number [1-2]: 2
```

## nginx Config Gets Updated Automatically

certbot automatically rewrites the nginx configuration file.

```nginx
server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        root /var/www/html;
        index index.html;
    }
}

server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}
```

## Automatic Certificate Renewal

Let's Encrypt certificates expire after 90 days. certbot handles automatic renewal via a systemd timer.

```bash
# Test auto-renewal
sudo certbot renew --dry-run
```

```bash
# Check the timer status
sudo systemctl status certbot.timer
```

## Common Commands

```bash
# List certificates
sudo certbot certificates

# Manually renew certificates
sudo certbot renew

# Delete a specific certificate
sudo certbot delete --cert-name example.com

# Test nginx config syntax
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## Gotchas

- Certificate retrieval fails if port 80 is closed — open it with ufw first
- When using Cloudflare, set the cloud icon to grey (DNS only) before running certbot
- Specify both `www.` and non-`www.` with `-d`, otherwise one won't have HTTPS
- If `server_name` isn't set correctly in nginx, certbot won't recognize the site
- DNS for the domain must point to the VPS IP, otherwise the challenge will fail

## Related Articles

- [nginx 502 Bad Gateway: Causes and How to Fix It](/en/nginx-502-bad-gateway)
- [Linux Firewall Setup with ufw](/en/linux-firewall-ufw)
- [Linux Basic Commands](/en/linux-basic-commands)
- [Linux File Permissions Explained](/en/linux-file-permissions)

## Recommended VPS Services

If you want to build a production environment on a VPS, these services are recommended.

- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">Sakura VPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">
- <a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMO Cloud ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">
