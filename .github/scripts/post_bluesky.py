import subprocess
import os
import json
import urllib.request
from datetime import datetime, timezone

handle = os.environ['BLUESKY_HANDLE']
password = os.environ['BLUESKY_PASSWORD']

# Get new files
result = subprocess.run(
    ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD', '--', 'src/pages/posts/*.md'],
    capture_output=True, text=True
)
new_files = result.stdout.strip().split('\n')
new_files = [f for f in new_files if f.endswith('.md')]

if not new_files:
    print("No new articles")
    exit(0)

# Get session
data = json.dumps({"identifier": handle, "password": password}).encode()
req = urllib.request.Request(
    'https://bsky.social/xrpc/com.atproto.server.createSession',
    data=data,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as res:
    session = json.load(res)

token = session['accessJwt']
did = session['did']

def make_facets(text, tags):
    """ハッシュタグのfacetsを生成する"""
    facets = []
    encoded = text.encode('utf-8')
    for tag in tags:
        hashtag = '#' + tag
        encoded_tag = hashtag.encode('utf-8')
        idx = encoded.find(encoded_tag)
        if idx >= 0:
            facets.append({
                "index": {
                    "byteStart": idx,
                    "byteEnd": idx + len(encoded_tag)
                },
                "features": [{
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag": tag
                }]
            })
    return facets

# Post each article
for filepath in new_files:
    title = ''
    category = ''
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('title:'):
                title = line.replace('title:', '').strip().strip("'\"")
            if line.startswith('category:'):
                category = line.replace('category:', '').strip().strip("'\"")

    slug = os.path.basename(filepath).replace('.md', '')
    url = f'https://errsolved.com/posts/{slug}'

    # カテゴリに応じたタグ
    tag_map = {
        'Docker': ['Docker', 'コンテナ', '開発'],
        'Git': ['Git', 'GitHub', 'バージョン管理'],
        'Linux': ['Linux', 'コマンド', '開発'],
        'nginx': ['nginx', 'サーバー', 'インフラ'],
        'Cloudflare': ['Cloudflare', 'CDN', 'インフラ'],
        'Astro': ['Astro', '静的サイト', 'フロントエンド'],
        'GitHub Actions': ['GitHubActions', 'CI', 'CD'],
        'Node.js': ['Nodejs', 'npm', 'JavaScript'],
        'Windows': ['Windows', '開発環境'],
        'SEO': ['SEO', 'ウェブ'],
    }
    tags = tag_map.get(category, ['開発', 'エラー解決'])

    hashtags = ' '.join(['#' + t for t in tags])
    text = f'新記事: {title}\n{url}\n{hashtags}'

    facets = make_facets(text, tags)

    post_data = json.dumps({
        'repo': did,
        'collection': 'app.bsky.feed.post',
        'record': {
            '$type': 'app.bsky.feed.post',
            'text': text,
            'facets': facets,
            'createdAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    }).encode()

    req = urllib.request.Request(
        'https://bsky.social/xrpc/com.atproto.repo.createRecord',
        data=post_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    urllib.request.urlopen(req)
    print(f'Posted: {title}')
