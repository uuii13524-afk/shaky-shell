#!/usr/bin/env python3
"""
Bluesky自動投稿スクリプト
- 新規Markdownファイルを検出してBlueskyに投稿
- URLをリンクfacetとして登録（タップでリンクを開けるように）
- ハッシュタグfacet対応
- @sasukkun.bsky.social のフォロー促進文を追加
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ---- 設定 ----
HANDLE = os.environ['BLUESKY_HANDLE']
PASSWORD = os.environ['BLUESKY_PASSWORD']
FOLLOW_HANDLE = '@sasukkun.bsky.social'

# ---- 認証 ----
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

# ---- フロントマター解析 ----
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
        'JavaScript': (['JavaScript', 'フロントエンド'], ['JavaScript', 'WebDev']),
        'TypeScript': (['TypeScript', 'フロントエンド'], ['TypeScript', 'WebDev']),
        'Python':     (['Python', 'プログラミング'],    ['Python', 'Programming']),
        'React':      (['React', 'フロントエンド'],     ['React', 'WebDev']),
        'CSS':        (['CSS', 'フロントエンド'],        ['CSS', 'WebDev']),
        'Node':       (['Node', 'バックエンド'],         ['NodeJS', 'Backend']),
        'Git':        (['Git', '開発'],                  ['Git', 'DevTips']),
        'SEO':        (['SEO', 'ウェブ'],                ['SEO', 'WebDev']),
    }
    ja, en = tag_map.get(data['category'], (['開発', 'エラー解決'], ['DevTips', 'ErrorFix']))
    data['ja_tags'] = ja
    data['en_tags'] = en

    return data

# ---- facet生成: ハッシュタグ ----
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

# ---- facet生成: URLリンク ----
def make_link_facets(text, urls):
    """URLをタップ可能なリンクfacetに変換する"""
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

# ---- facet生成: メンション ----
def make_mention_facets(text, mentions):
    """@handleをメンションfacetに変換する（DID解決が必要）"""
    facets = []
    encoded = text.encode('utf-8')
    for handle, mention_did in mentions:
        at_handle = handle  # 例: '@sasukkun.bsky.social'
        encoded_handle = at_handle.encode('utf-8')
        start = 0
        while True:
            idx = encoded.find(encoded_handle, start)
            if idx < 0:
                break
            facets.append({
                "index": {"byteStart": idx, "byteEnd": idx + len(encoded_handle)},
                "features": [{"$type": "app.bsky.richtext.facet#mention", "did": mention_did}]
            })
            start = idx + 1
    return facets

# ---- DID解決 ----
def resolve_did(handle):
    """ハンドルからDIDを取得"""
    clean_handle = handle.lstrip('@')
    url = f'https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={urllib.parse.quote(clean_handle)}'
    try:
        res = urllib.request.urlopen(url)
        data = json.loads(res.read())
        return data.get('did', '')
    except Exception:
        return ''

# ---- 新規ファイル取得 (git diff) ----
import subprocess

result = subprocess.run(
    ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD', '--', 'src/pages/*.md'],
    capture_output=True, text=True
)
new_files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]

if not new_files:
    print('新規ファイルなし')
    exit(0)

# フォローアカウントのDIDを事前解決
follow_did = resolve_did(FOLLOW_HANDLE)

# ---- 投稿 ----
for filepath in new_files:
    info = parse_frontmatter(filepath)
    slug = os.path.basename(filepath).replace('.md', '')
    ja_url = f'https://errsolved.com/posts/{slug}'
    en_url = f'https://errsolved.com/en/{slug}'

    # 英語記事が存在するか確認
    en_filepath = f'src/pages/en/{slug}.md'
    en_info = None
    if os.path.exists(en_filepath):
        en_info = parse_frontmatter(en_filepath)

    ja_hashtags = ' '.join(['#' + t for t in info['ja_tags']])
    en_hashtags = ' '.join(['#' + t for t in info['en_tags']])

    # フォロー促進文（日英両対応）
    follow_cta_ja = f'💡 エラー解決のTipsを定期投稿中！\nよかったら {FOLLOW_HANDLE} をフォローしてね🙏'
    follow_cta_en = f'💡 Posting dev tips & error fixes regularly!\nFollow {FOLLOW_HANDLE} for more 🙏'

    if en_info and en_info['title']:
        follow_cta = f'\n\n{follow_cta_ja}\n{follow_cta_en}'
        text = (
            f"新記事 / New article\n\n"
            f"🇯🇵 {info['title']}\n{ja_url}\n\n"
            f"🇬🇧 {en_info['title']}\n{en_url}\n\n"
            f"{ja_hashtags}\n{en_hashtags}"
            f"{follow_cta}"
        )
        urls = [ja_url, en_url]
    else:
        follow_cta = f'\n\n{follow_cta_ja}'
        text = (
            f"新記事: {info['title']}\n{ja_url}\n\n"
            f"{ja_hashtags}"
            f"{follow_cta}"
        )
        urls = [ja_url]

    # facets結合: リンク + タグ + メンション
    all_tags = info['ja_tags'] + (info['en_tags'] if en_info else [])
    facets = (
        make_link_facets(text, urls)
        + make_tag_facets(text, all_tags)
        + (make_mention_facets(text, [(FOLLOW_HANDLE, follow_did)]) if follow_did else [])
    )

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
    print(f'Posted: {info["title"]}')
