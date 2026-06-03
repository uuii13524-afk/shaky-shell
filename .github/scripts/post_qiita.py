import os
import re
import json
import subprocess
import urllib.request
import urllib.error

QIITA_TOKEN = os.environ.get('QIITA_TOKEN', '')

CATEGORY_TAGS = {
    'Git': ['Git', 'GitHub', 'バージョン管理', 'プログラミング', 'エラー解決'],
    'Linux': ['Linux', 'Ubuntu', 'コマンド', 'プログラミング', 'エラー解決'],
    'Docker': ['Docker', 'コンテナ', 'DevOps', 'プログラミング', 'エラー解決'],
    'Node.js': ['Node.js', 'JavaScript', 'npm', 'プログラミング', 'エラー解決'],
    'Cloudflare': ['Cloudflare', 'CDN', 'インフラ', 'プログラミング', 'エラー解決'],
    'Astro': ['Astro', 'フロントエンド', 'JavaScript', 'プログラミング', 'エラー解決'],
}

def parse_frontmatter(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    info = {'title': '', 'category': '', 'date': '', 'layout': ''}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
            for line in fm.splitlines():
                for key in info:
                    if line.startswith(f'{key}:'):
                        info[key] = line.split(':', 1)[1].strip().strip('"\'')
            return info, body
    return info, content

def clean_body(body):
    body = re.sub(r'<a[^>]*a8\.net[^>]*>.*?</a>', '', body, flags=re.DOTALL)
    body = re.sub(r'<img[^>]*a8\.net[^>]*>', '', body)
    body = re.sub(r'\(/posts/([^)]+)\)', r'(https://errsolved.com/posts/\1/)', body)
    body = re.sub(r'\(/en/([^)]+)\)', r'(https://errsolved.com/en/\1/)', body)
    return body.strip()

def post_to_qiita(title, body, tags, slug):
    original_url = f'https://errsolved.com/posts/{slug}/'
    footer = f'\n\n---\n\n> この記事は [errsolved.com]({original_url}) にも掲載しています。'
    full_body = body + footer

    qiita_tags = [{'name': t} for t in tags[:5]]

    payload = json.dumps({
        'title': title,
        'body': full_body,
        'tags': qiita_tags,
        'private': False,
        'tweet': False,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://qiita.com/api/v2/items',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {QIITA_TOKEN}',
            'User-Agent': 'errsolved-auto-poster/1.0 (https://errsolved.com)',
        }
    )
    try:
        res = urllib.request.urlopen(req)
        result = json.loads(res.read())
        print(f'Posted to Qiita: {result["url"]}')
        return result['url']
    except urllib.error.HTTPError as e:
        body_resp = e.read().decode()
        print(f'HTTPError: {e.code} {e.reason}')
        print(f'Response: {body_resp}')
        raise

result = subprocess.run(
    ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1', 'HEAD', '--', 'src/pages/posts/*.md'],
    capture_output=True, text=True
)
new_files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]

if not new_files:
    print('No new files')
    exit(0)

for filepath in new_files:
    info, body = parse_frontmatter(filepath)
    if not info['title']:
        print(f'Skipped (no title): {filepath}')
        continue

    slug = os.path.basename(filepath).replace('.md', '')
    clean = clean_body(body)
    tags = CATEGORY_TAGS.get(info['category'], ['プログラミング', 'Linux', 'エラー解決'])

    print(f'Posting: {info["title"]}')
    post_to_qiita(info['title'], clean, tags, slug)