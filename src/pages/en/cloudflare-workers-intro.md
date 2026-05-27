---
title: 'Cloudflare Workers Introduction: Building Serverless Functions'
date: '2026-05-21'
category: 'Cloudflare'
layout: '../../layouts/PostLayoutEn.astro'
ja_tags: ['Cloudflare', 'Cloudflare Workers', 'サーバーレス', 'Wrangler']
en_tags: ['Cloudflare', 'Cloudflare Workers', 'serverless', 'Wrangler']
description: 'A hands-on intro to Cloudflare Workers: set up Wrangler, write your first serverless function, test locally, and deploy to the edge.'
---
## What Are Cloudflare Workers?

- Serverless runtime running on Cloudflare's global edge network
- No cold starts (nearly instant execution)
- Free tier: up to 100,000 requests per day
- Uses Web standard APIs (not Node.js)

## Setup and Deploy

### 1. Install Wrangler

```bash
npm install -g wrangler
wrangler --version
```

### 2. Log in to Cloudflare

```bash
wrangler login
```

### 3. Create a Project

```bash
npm create cloudflare@latest my-worker
cd my-worker
```

### 4. Write the Worker (src/index.js)

```javascript
export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === '/api/hello') {
      return new Response(JSON.stringify({ message: 'Hello from Worker!' }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

### 5. Test Locally

```bash
wrangler dev
```

Open http://localhost:8787 to verify.

### 6. Deploy

```bash
wrangler deploy
```

## Common Use Cases

### Redirect Handling

```javascript
export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/old-page') {
      return Response.redirect('https://example.com/new-page', 301);
    }
    return fetch(request);
  },
};
```

### Add CORS Headers

```javascript
export default {
  async fetch(request) {
    const response = await fetch(request);
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');
    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
```

## Common Pitfalls

- Workers use Web standard APIs, not Node.js built-ins
- Use `wrangler dev` for local testing before deploying
- Use `wrangler secret put MY_KEY` to store secrets securely

## Related Posts

- [How to Deploy an Astro Site to Cloudflare Pages](/en/astro-cloudflare-deploy)
- [How to Set Environment Variables in Cloudflare Pages](/en/cloudflare-pages-env-variables)
- [How to Set Up Redirect Rules in Cloudflare](/en/cloudflare-redirect-rules)
- [GitHub Actions: Basic Auto-Deploy Setup](/en/github-actions-basic)

## Recommended Services

- <a href="https://www.awin1.com/cread.php?awinmid=6288&awinaffid=2909773&ued=https%3A%2F%2Fwww.fiverr.com" target="_blank" rel="sponsored">Fiverr</a> - Find freelance developers and tech experts
