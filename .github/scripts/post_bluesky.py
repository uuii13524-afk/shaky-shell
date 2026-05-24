import os
import json
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime, timezone

HANDLE = os.environ['BLUESKY_HANDLE']
PASSWORD = os.environ['BLUESKY_PASSWORD']
FOLLOW_HANDLE = '@sasukkun.bsky.social'

def login(handle, password):
    data = json.dumps({'identifier': handle, 'password': password}).encode()
    req = urllib.request.Request(
        'https://bsky.social/xrpc/com.atproto.server.createSession',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    session = json.loads(res.read())
    return session['accessJwt'], session['did']

token, did = login(HANDLE, PASSWORD)

def parse_frontmatter(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    data = {'title': '', 'category': '', 'ja_tags': [], 'en_tags': []}
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm = content[3:end]
            for line in fm.splitlines():
                if line.startswith('title:'):
                    data['title'] = line[6:].strip().strip('"\'')
                elif line.startswith('category:'):
                    data['category'] = line[9:].strip().strip('"\'')
    tag_map = {
        'Docker':         (['Docker', 'コンテナ', '開発'],       ['Docker', 'Container', 'DevOps']),
        'Git':            (['Git', 'GitHub', 'バージョン管理'],  ['Git', 'GitHub', 'DevTips']),
        'Linux':          (['Linux', 'コマンド', '開発'],        ['Linux', 'Commands', 'DevTips']),
        'nginx':          (['nginx', 'サーバー', 'インフラ'],    ['nginx', 'WebServer', 'DevOps']),
        'Cloudflare':     (['Cloudflare', 'CDN', 'インフラ'],    ['Cloudflare', 'CDN', 'DevOps']),
        'Astro':          (['Astro', '静的サイト', 'Web開発'],   ['Astro', 'StaticSite', 'WebDev']),
        'GitHub Actions': (['GitHubActions', 'CI', '自動化'],    ['GitHubActions', 'CI', 'Automation']),
        'Node.js':        (['Nodejs', 'npm', 'JavaScript'],      ['Nodejs', 'npm', 'JavaScript']),
        'Windows':        (['Windows', '開発環境'],              ['Windows', 'DevEnvironment']),
        'SEO':            (['SEO', 'ウェブ'],                    ['SEO', 'WebDev']),
    }
    ja, en = tag_map.get(data['category'], (['開発', 'エラー解決'], ['DevTips', 'ErrorFix']))
    data['ja_tags'] = ja
    data['en_tags'] = en
    return data

def byte_len(text):
    return len(text.encode('utf-8'))

def make_tag_facets(text, tags):
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

def make_link_facets(text, urls):
    facets = []
    encoded = text.encode('utf-8')
    for url in urls:
        encoded_url = url.encode('utf-8')
        start = 0
        while True:
            idx = encoded.find(encoded_url, start)
            if idx < 0:
                break
            facets.append({
                "index": {"byteStart": idx, "byteEnd": idx + len(encoded_url)},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}]
            })
            start = idx + 1
    return facets

def resolve_did(handle):
    clean_handle = handle.lstrip('@')
    url = f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={urllib.parse.quote(clean_handle)}'
    try:
        res = urllib.request.urlopen(url)
        data = json.loads(res.read())
        return data.get('did', '')
    except Exception:
        return ''

result = subprocess.run(
    ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD', '--', 'src/pages/posts/*.md'],
    capture_output=True, text=True
)
new_files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]

if not new_files:
    print('No new files')
    exit(0)

follow_did = resolve_did(FOLLOW_HANDLE)

for filepath in new_files:
    info = parse_frontmatter(filepath)
    slug = os.path.basename(filepath).replace('.md', '')
    ja_url = f'https://errsolved.com/posts/{slug}'
    en_url = f'https://errsolved.com/en/{slug}'

    en_filepath = f'src/pages/en/{slug}.md'
    en_info = None
    if os.path.exists(en_filepath):
        en_info = parse_frontmatter(en_filepath)

    ja_hashtags = ' '.join(['#' + t for t in info['ja_tags']])
    en_hashtags = ' '.join(['#' + t for t in info['en_tags']])

    follow_cta_ja = f'Tips定期投稿中! {FOLLOW_HANDLE} をフォローしてね'
    follow_cta_en = f'Follow {FOLLOW_HANDLE} for dev tips!'

    # フルバージョン（CTA付き）
    if en_info and en_info['title']:
        text_full = (
            f"New article\n\n"
            f"{info['title']}\n{ja_url}\n\n"
            f"{en_info['title']}\n{en_url}\n\n"
            f"{ja_hashtags}\n{en_hashtags}\n\n"
            f"{follow_cta_ja}\n{follow_cta_en}"
        )
        text_short = (
            f"New article\n\n"
            f"{info['title']}\n{ja_url}\n\n"
            f"{en_info['title']}\n{en_url}\n\n"
            f"{ja_hashtags}\n{en_hashtags}"
        )
        urls = [ja_url, en_url]
    else:
        text_full = (
            f"{info['title']}\n{ja_url}\n\n"
            f"{ja_hashtags}\n\n"
            f"{follow_cta_ja}"
        )
        text_short = (
            f"{info['title']}\n{ja_url}\n\n"
            f"{ja_hashtags}"
        )
        urls = [ja_url]

    # Blueskyは300バイト制限
    if byte_len(text_full) <= 300:
        text = text_full
    else:
        text = text_short

    print(f'Text bytes: {byte_len(text)} / 300')
    print(f'Text: {text}')

    all_tags = info['ja_tags'] + (info['en_tags'] if en_info else [])
    facets = make_link_facets(text, urls) + make_tag_facets(text, all_tags)

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
    try:
        urllib.request.urlopen(req)
        print(f'Posted: {info["title"]}')
    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code} {e.reason}')
        print(f'Response body: {e.read().decode()}')
        raise
