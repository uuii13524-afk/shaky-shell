---
title: 'Fix: Astro 6 Build Fails with "Could not resolve" from a One-Level-Off layout Path'
date: '2026-09-20'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'astro build fails with "Could not resolve" when a Markdown post''s frontmatter layout path is one directory level too shallow. Here is how the relative path depth works and how to catch the mistake before it reaches production.'
ja_tags: ['Astro', 'build error', 'Could not resolve']
en_tags: ['Astro', 'build error', 'Could not resolve']
---

## What I Was Trying to Do

This site (errsolved.com) manages every post as an Astro Markdown page, and new posts are usually created by copying an existing file and rewriting its frontmatter. As usual, I created a new `.md` file under `src/pages/posts/`, copied the frontmatter from an existing post, edited it, and ran the build.

```bash
npm run build
```

Normally this builds a few hundred pages straight through, but this time the log stopped partway and ended with an error:

```text
00:04:06 [types] Generated 148ms
00:04:06 [build] output: "static"
00:04:06 [build] mode: "static"
00:04:06 [build] directory: /home/user/shaky-shell/dist/
00:04:06 [build] Collecting build info...
00:04:06 [build] ✓ Completed in 228ms.
00:04:06 [build] Building static entrypoints...
00:04:11 [ERROR] [vite] ✗ Build failed in 4.87s
Could not resolve "../layouts/PostLayout.astro" from "src/pages/posts/zzz-test-layout-error.md"
file: /home/user/shaky-shell/src/pages/posts/zzz-test-layout-error.md
  Stack trace:
    at getRollupError (file:///home/user/shaky-shell/node_modules/rollup/dist/es/shared/parseAst.js:406:41)
    at ModuleLoader.handleInvalidResolvedId (file:///home/user/shaky-shell/node_modules/rollup/dist/es/shared/node-entry.js:22127:24)
```

The `file:` line pointed straight at the file I had just been editing. The other 127 posts were building fine, so the problem was clearly something in the new file.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: v6.3.5 (installed from `package.json`'s `astro: ^6.3.5`)
- Build command: `npm run build` (runs `astro build && npx pagefind --site dist`)
- Post layout: `src/pages/posts/<slug>.md` for Japanese, `src/pages/en/<slug>.md` for English, with shared layouts at `src/layouts/PostLayout.astro` and `src/layouts/PostLayoutEn.astro`

## What I Tried

At first I focused on the string `Could not resolve "../layouts/PostLayout.astro"` and assumed the layout file itself was broken, so I opened `src/layouts/PostLayout.astro` to check it. It was there and loading fine for every other post, so the problem had to be in how the new post's frontmatter referenced it, not in the layout file itself.

Looking at the new post's frontmatter, it had this:

```yaml
---
title: 'test'
date: '2026-09-20'
category: 'Astro'
layout: '../layouts/PostLayout.astro'
description: 'test'
ja_tags: ['Astro']
en_tags: ['Astro']
---
```

The `layout` value was `../layouts/PostLayout.astro`. Checking an existing post for comparison:

```bash
grep "^layout:" src/pages/posts/docker-permission-denied.md
```

```text
layout: '../../layouts/PostLayout.astro'
```

The existing post had two `../` segments, not one. Only side by side did it become obvious that when I'd copy-pasted the frontmatter by hand, I'd accidentally dropped one `../` along the way.

## Why This Happens

Astro resolves a Markdown page's `layout` frontmatter as a path relative to that Markdown file's own location. Posts on this site live at `src/pages/posts/<slug>.md`, and the layout lives at `src/layouts/PostLayout.astro`. Counting directories one at a time:

- One `../` from `src/pages/posts/<slug>.md` lands at `src/pages/`
- A second `../../` is needed to reach `src/`
- From there, `layouts/PostLayout.astro` resolves to `src/layouts/PostLayout.astro`

So getting from `src/pages/posts/` to `src/layouts/` requires going up two levels, and the correct relative path is `../../layouts/PostLayout.astro`. With only one `../`, Vite tried to resolve `src/pages/layouts/PostLayout.astro` instead, which doesn't exist. Since the target path is missing, Rollup (the bundler Astro uses internally) fails the build with `Could not resolve`.

What makes this easy to miss is that the error doesn't show up at the syntax-checking stage. The frontmatter's YAML is perfectly valid, so a type check can pass without issue. The failure only surfaces when Vite actually tries to build that specific page and resolve the `layout` import — which in practice means you only find out by running the full `npm run build`.

## Solution

### 1. Find the file from the `file:` line

```text
file: /home/user/shaky-shell/src/pages/posts/zzz-test-layout-error.md
```

Astro's build errors always include the absolute path of the offending file, so start there.

### 2. Check that file's `layout` frontmatter

```bash
grep "^layout:" src/pages/posts/zzz-test-layout-error.md
```

```text
layout: '../layouts/PostLayout.astro'
```

### 3. Copy the relative path from a known-good post

Rather than counting directory levels by hand, I copied the `layout` line straight from an existing post at the same depth.

```bash
grep "^layout:" src/pages/posts/docker-permission-denied.md
```

```text
layout: '../../layouts/PostLayout.astro'
```

### 4. Fix the path

```yaml
layout: '../../layouts/PostLayout.astro'
```

### 5. Rebuild

```bash
npm run build
```

```text
00:04:22   ├─ /posts/zzz-test-layout-error/index.html (+2ms) 
00:04:22   ├─ /privacy/index.html (+1ms) 
00:04:22   ├─ /rss.xml (+30ms) 
00:04:22   ├─ /index.html (+6ms) 
00:04:22 ✓ Completed in 748ms.

00:04:22 [build] ✓ Completed in 6.35s.
00:04:22 [@astrojs/sitemap] `sitemap-index.xml` created at `dist`
00:04:22 [build] 268 page(s) built in 6.51s
00:04:22 [build] Complete!
```

The error was gone and every page, including the fixed one, built through to the end.

## Verification

I confirmed the post's `index.html` was generated under `dist/posts/` and ran `npm run preview` to check the layout (header, category label, language switcher links) rendered correctly.

```bash
ls dist/posts/ | grep zzz-test-layout-error
```

```text
zzz-test-layout-error
```

The directory was there, output as a directory containing `index.html`, consistent with this site's `trailingSlash: 'always'` and `build: { format: 'directory' }` config.

## Summary

- A Markdown page's `layout` frontmatter is resolved relative to that file's own location. Getting from `src/pages/posts/<slug>.md` to `src/layouts/` takes two levels up (`../../`).
- Dropping a single `../` points to a path that doesn't exist, and `astro build` fails with Rollup's `Could not resolve` — even though the YAML itself is syntactically valid, so nothing looks wrong at a glance.
- Copying the `layout` line from an existing post at the same directory depth is safer than counting levels by hand. When generating Japanese and English posts in bulk, this kind of path mistake won't surface until the final `npm run build`, so running a local build before every `git push` catches it before it reaches production.

## FAQ

**Q: Wouldn't `astro dev` catch this too?**
Yes, but only if you actually open that specific page in the dev server. On a site with well over a hundred posts, it's far more reliable to run a full `npm run build` than to click through every page one by one.

**Q: Is there a way to avoid specifying `layout` per file?**
Astro's content collections can centralize the layout via a schema, but this site uses plain Markdown pages under `src/pages/`, which require a `layout` in each file's frontmatter. The simplest mitigation is always starting a new post from a copy of an existing one at the same directory depth and only editing the content fields.

**Q: Does the English version (`src/pages/en/`) need the same number of `../`?**
Yes. `src/pages/en/<slug>.md` sits at the same depth as `src/pages/posts/<slug>.md` — one level under `src/pages/` — so its `layout` also needs two `../` segments, e.g. `../../layouts/PostLayoutEn.astro`.

## Related Articles

- [How to Add a New Page in Astro](/en/astro-add-page)
- [Styling Markdown Content in Astro](/en/astro-markdown-styles)
- [Setting Up SEO Meta Tags in Astro](/en/astro-seo-meta-tags)
- [How to Check Cloudflare Pages Build Logs](/en/cloudflare-pages-build-log)
