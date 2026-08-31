---
title: 'Fix: Astro Build Fails with "bad indentation of a mapping entry" from an Unquoted Colon in Frontmatter'
date: '2026-08-31'
category: 'Astro'
layout: '../../layouts/PostLayoutEn.astro'
description: 'An unquoted colon inside a frontmatter value on an Astro Markdown page breaks the YAML parser with "bad indentation of a mapping entry" and fails the whole build. Here is the cause and the one-line fix.'
en_tags: ['Astro', 'YAML', 'frontmatter', 'build error']
---

## What I Was Trying to Do

This blog itself runs on Astro, and every post is a Markdown file under `src/pages/posts/*.md` with a YAML frontmatter block for `title`, `description`, and so on. While drafting a new post, I tried to put an error message directly into the `description` field.

```yaml
---
title: 'Docker: permission denied エラーの対処法'
date: '2026-08-31'
category: 'Docker'
layout: '../../layouts/PostLayout.astro'
description: Test description. Contains a colon: this is what breaks it.
ja_tags: ['Docker']
en_tags: ['Docker']
---
```

I left that `description` value unquoted and ran `npm run build`, and the build failed.

```text
00:11:33 [build] Building static entrypoints...
00:11:41 [ERROR] [vite] ✗ Build failed in 7.99s
[astro:markdown] Could not load /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md (imported by src/pages/rss.xml.js): bad indentation of a mapping entry
file: /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md:5:30
  Location:
    /home/user/errsolved/src/pages/posts/astro-frontmatter-colon-yaml-error.md:5:30
  Stack trace:
    at generateError (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:1289:10)
    at readBlockMapping (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2278:7)
    at readDocument (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2721:3)
    at load$1 (file:///home/user/errsolved/node_modules/js-yaml/dist/js-yaml.mjs:2810:19)
    at safeParseFrontmatter (file:///home/user/errsolved/node_modules/astro/dist/content/utils.js:328:12)
```

One broken post took the entire site build down with it. The `file:` line pointed straight at the exact line and column (`:5:30`), so finding the file wasn't the hard part — understanding *why* a colon in a sentence would break YAML was. My first instinct was to blame the `ja_tags` array syntax and start fiddling with quote styles there instead.

## Environment

- OS: Ubuntu 24.04 LTS
- Node.js: v22.22.2
- npm: 10.9.7
- Astro: 6.3.5 (checked with `npx astro --version`)
- Build command: `npm run build` (runs `astro build && npx pagefind --site dist`)
- Posts are plain Markdown with frontmatter, not Content Collections (`.mdx` with a Zod schema)

## What I Tried

I first suspected the `ja_tags: ['Docker']` array syntax and tried switching between single and double quotes there — no change.

Then I actually read the line number the error gave me. Line 5 was the `description` field.

```yaml
description: Test description. Contains a colon: this is what breaks it.
```

I noticed the mid-sentence colon at this point, but assumed it was harmless punctuation and moved on to check other things first.

As a test, I shortened the value to remove everything after the colon and rebuilt.

```yaml
description: Test description.
```

```text
00:15:02 [build] 267 page(s) built in 10.9s
00:15:02 [build] Complete!
```

The build passed. That confirmed the colon was the actual cause, so I went looking for a fix that didn't require deleting it.

## Root Cause

In YAML, a `key: value` line whose value is left unquoted (a "plain scalar") gets broken the moment a `:` followed by a space or newline appears inside it — the parser treats that as the start of a new mapping entry.

My line, `description: Test description. Contains a colon: this is what breaks it.`, gets parsed as an attempt at:

- The `description` key's value ending at `Test description. Contains a colon`
- Everything after that treated as the start of another mapping entry: `: this is what breaks it.`

But that second "entry" doesn't sit at a valid indentation level to be a key, so the parser reports it as an indentation problem in the block mapping — `bad indentation of a mapping entry`. The stack trace Astro printed backs this up: the exception is thrown inside `js-yaml`'s `readBlockMapping`, which is exactly the block-mapping parsing routine.

On the Astro side, `safeParseFrontmatter` in `astro/dist/content/utils.js` hands the content between the `---` fences to `js-yaml`. When that throws, loading that one file fails — and because `rss.xml.js` reads every post to build the feed, the failure propagates and takes the whole build down with it.

So the actual cause isn't "a colon in Japanese/English prose" per se — it's an unquoted YAML plain scalar containing a colon followed by whitespace or end-of-line. A full-width colon (：) wouldn't trigger this, since YAML doesn't treat it as a structural separator.

## How I Fixed It

### 1. Wrap the value in single quotes

```yaml
description: 'Test description. Contains a colon: this is what breaks it.'
```

A single-quoted YAML scalar isn't subject to the plain-scalar colon rule, so the colon can stay exactly where it is.

### 2. Rebuild and confirm

```bash
npx astro build
```

```text
00:11:58 [build] 267 page(s) built in 10.83s
00:11:58 [@astrojs/sitemap] `sitemap-index.xml` created at `dist`
00:11:58 [build] Complete!
```

Clean build, no errors.

### 3. Sweep the rest of the repo for the same pattern

Every `title` and `description` in this repo is already quoted by convention, so I checked whether any other file had accidentally dropped a quote the same way. A quick grep for unquoted lines containing a colon works as a mechanical check:

```bash
grep -nE "^(title|description): [^'\"].*:" src/pages/posts/*.md src/pages/en/*.md
```

Zero matches — this test file was the only offender.

## Verify It Works

I re-ran a full build to make sure the whole site, not just the one page, completes successfully.

```bash
npm run build
```

```text
[build] 267 page(s) built in 11.14s
[build] Complete!
```

I also confirmed the page's HTML was actually generated:

```bash
ls dist/posts/ | grep astro-frontmatter-colon-yaml-error
```

```text
astro-frontmatter-colon-yaml-error
```

And checked the rendered `<meta name="description">` to make sure the string wasn't truncated at the colon.

## Takeaways

- Astro's Markdown frontmatter is parsed as plain YAML, so an unquoted value containing a colon followed by a space or newline gets misread as the start of a new mapping entry, producing `bad indentation of a mapping entry` and failing the entire build.
- The fix is a one-liner: wrap any value that contains a colon in single (or double) quotes. Since this repo standardizes on single-quoted frontmatter values, dropping the quote on just one field is enough to break things.
- This isn't specific to `description` — it can happen on any frontmatter field. The `file:line:column` in the error message tells you exactly where to look; check that line for an unquoted colon first.

## FAQ

**Q: Does a full-width colon (：) trigger the same error?**
No. YAML only treats a half-width `:` (followed by a space or newline) as a structural separator. Using a full-width colon, or omitting the space right after the colon, avoids the error too, but it changes how the text reads — quoting the value is the safer fix.

**Q: Single quotes or double quotes?**
This repo already standardizes on single quotes, so I matched that. Both are valid YAML, but double-quoted strings handle backslash escaping differently from single-quoted ones, and mixing the two styles in one repo is its own source of subtle bugs. Pick one convention and stick to it.

**Q: Does this also happen with MDX / Content Collections?**
Yes. Even with a Zod schema defined for a collection, the frontmatter block still has to be parsed as YAML by the same `js-yaml` library first. If that parse fails, it fails before schema validation ever runs, and the error looks essentially the same.

## Related Articles

- [How to Style Markdown Content in Astro](/en/astro-markdown-styles)
- [How to Set Up SEO Meta Tags in Astro](/en/astro-seo-meta-tags)
- [How to Add a New Page in Astro](/en/astro-add-page)
- [Setting Up sitemap.xml and robots.txt with Astro + Cloudflare Pages](/en/astro-sitemap-robots)
