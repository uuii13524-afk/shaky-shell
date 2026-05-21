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

# カテゴリ別タグマップ（日本語・英語）
tag_map = {
    'Docker':          (['Docker', 'コンテナ', '開発'],        ['Docker', 'Container', 'DevOps']),
    'Git':             (['Git', 'GitHub', 'バージョン管理'],   ['Git', 'GitHub', 'VersionControl']),
    'Linux':           (['Linux', 'コマンド', '開発'],         ['Linux', 'LinuxCommands', 'DevTips']),
    'nginx':           (['nginx', 'サーバー', 'インフラ'],     ['nginx', 'WebServer', 'DevOps']),
    'Cloudflare':      (['Cloudflare', 'CDN', 'インフラ'],     ['Cloudflare', 'CDN', 'DevOps']),
    'Astro':           (['Astro', '静的サイト', 'Web開発'],    ['Astro', 'StaticSite', 'WebDev']),
    'GitHub Actions':  (['GitHubActions', 'CI', '自動化'],     ['GitHubActions', 'CI', 'Automation']),
    'Node.js':         (['Nodejs', 'npm', 'JavaScript'],       ['Nodejs', 'npm', 'JavaScript']),
    'Windows':         (['Windows', '開発環境'],               ['Windows', 'DevEnvironment']),
    'SEO':             (['SEO', 'ウェブ'],                     ['SEO', 'WebDev']),
}

def make_facets(text, tags):
    facets = []
    encoded = text.encode('utf-8')
    for tag in tags:
        hashtag = '#' + tag
        encoded_tag = hashtag.encode('utf-8')
        start = 0
        while True:
            idx = encoded.find(encoded_tag, start)
            if idx < 0:
                break
            facets.append({
                "index": {"byteStart": idx, "byteEnd": idx + len(encoded_tag)},
                "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag}]
            })
            start = idx + 1
    return facets

for filepath in new_files:
    ja_title = ''
    category = ''
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('title:'):
                ja_title = line.replace('title:', '').strip().strip("'\"")
            if line.startswith('category:'):
                category = line.replace('category:', '').strip().strip("'\"")

    slug = os.path.basename(filepath).replace('.md', '')
    ja_url = f'https://errsolved.com/posts/{slug}'
    en_url = f'https://errsolved.com/en/{slug}'

    # 英語記事が存在するか確認
    en_filepath = f'src/pages/en/{slug}.md'
    en_title = ''
    has_en = os.path.exists(en_filepath)
    if has_en:
        with open(en_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('title:'):
                    en_title = line.replace('title:', '').strip().strip("'\"")
                    break

    ja_tags, en_tags = tag_map.get(category, (['開発', 'エラー解決'], ['DevTips', 'ErrorFix']))
    ja_hashtags = ' '.join(['#' + t for t in ja_tags])
    en_hashtags = ' '.join(['#' + t for t in en_tags])

    if has_en and en_title:
        text = f'新記事 / New article\n\n🇯🇵 {ja_title}\n{ja_url}\n\n🇬🇧 {en_title}\n{en_url}\n\n{ja_hashtags}\n{en_hashtags}'
    else:
        text = f'新記事: {ja_title}\n{ja_url}\n\n{ja_hashtags}'

    all_tags = ja_tags + (en_tags if has_en else [])
    facets = make_facets(text, all_tags)

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
    print(f'Posted: {ja_title}')
