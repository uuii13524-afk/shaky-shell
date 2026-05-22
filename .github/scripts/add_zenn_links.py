import os

ZENN_BLOCK = """
## より詳しく学びたい方へ

この記事の内容をさらに深掘りした実践ガイドをZennで公開しています。

[VPS・GitHub Actions・Cloudflare 実践構築ガイド](https://zenn.dev/errnotes/books/6ec5fb4840cea2)
"""

TARGET_FILES = [
    'src/pages/posts/vps-docker-setup.md',
    'src/pages/posts/docker-compose-basic.md',
    'src/pages/posts/docker-network-basics.md',
    'src/pages/posts/docker-basic-commands.md',
    'src/pages/posts/github-actions-basic.md',
    'src/pages/posts/github-actions-schedule.md',
    'src/pages/posts/github-actions-secrets.md',
    'src/pages/posts/github-actions-node-cache.md',
    'src/pages/posts/astro-cloudflare-deploy.md',
    'src/pages/posts/cloudflare-pages-deploy-not-working.md',
    'src/pages/posts/xserver-cloudflare-full-setup.md',
]

updated = 0
skipped = 0

for filepath in TARGET_FILES:
    if not os.path.exists(filepath):
        print(f'Not found: {filepath}')
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'zenn.dev/errnotes' in content:
        skipped += 1
        continue

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.rstrip() + ZENN_BLOCK)

    updated += 1
    print(f'Updated: {filepath}')

print(f'\n完了: {updated}本更新, {skipped}本スキップ')
