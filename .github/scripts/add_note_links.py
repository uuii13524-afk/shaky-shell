import os

NOTE_VPS = 'https://note.com/err_notes/n/n48e3c5e016c9'
NOTE_GITHUB = 'https://note.com/err_notes/n/n97ec6ef08c2e'
NOTE_CLOUDFLARE = 'https://note.com/err_notes/n/nc26c99513ca9'

# 記事ごとのnoteリンク設定
TARGETS = {
    'vps-docker-setup': NOTE_VPS,
    'docker-compose-basic': NOTE_VPS,
    'docker-network-basics': NOTE_VPS,
    'docker-basic-commands': NOTE_VPS,
    'github-actions-basic': NOTE_GITHUB,
    'github-actions-schedule': NOTE_GITHUB,
    'github-actions-secrets': NOTE_GITHUB,
    'github-actions-node-cache': NOTE_GITHUB,
    'astro-cloudflare-deploy': NOTE_CLOUDFLARE,
    'cloudflare-pages-deploy-not-working': NOTE_CLOUDFLARE,
    'xserver-cloudflare-full-setup': NOTE_CLOUDFLARE,
}

posts_dir = 'src/pages/posts'
updated = 0
skipped = 0

for slug, note_url in TARGETS.items():
    filepath = os.path.join(posts_dir, slug + '.md')
    if not os.path.exists(filepath):
        print(f'Not found: {filepath}')
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'note.com/err_notes' in content:
        skipped += 1
        continue

    note_block = f'\n\n## noteでも読めます\n\nより詳しい解説をnoteで公開しています。\n\n[詳細記事を読む（note）]({note_url})\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.rstrip() + note_block)

    updated += 1
    print(f'Updated: {slug}')

print(f'\n完了: {updated}本更新, {skipped}本スキップ')
