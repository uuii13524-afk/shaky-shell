import os
import json
import re
import subprocess
import urllib.request

QIITA_TOKEN = os.environ['QIITA_TOKEN']

CATEGORY_TAGS = {
    'Docker':         ['Docker', 'コンテナ', 'Linux'],
    'Git':            ['Git', 'GitHub', 'バージョン管理'],
    'Linux':          ['Linux', 'コマンド', 'シェル'],
    'nginx':          ['nginx', 'Linux', 'インフラ'],
    'Cloudflare':     ['Cloudflare', 'CDN', 'DNS'],
    'Astro':          ['Astro', '静的サイトジェネレーター', 'Web'],
    'GitHub Actions': ['GitHubActions', 'CI/CD', '自動化'],
    'Node.js':        ['Node.js', 'npm', 'JavaScript'],
    'Windows':        ['Windows', '開発環境', 'Git'],
    'SEO':            ['SEO', 'Web', 'マーケティング'],
}

def parse_frontmatter(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    data = {'title': '', 'category': '', 'description': ''}
    body = content
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm = content[3:end]
            for line in fm.splitlines():
                if line.startswith('title:'):
                    data['title'] = line[6:].strip().strip('"\'')
                elif line.startswith('category:'):
                    data['category'] = line[9:].strip().strip('"\'')
                elif line.startswith('description:'):
                    data['description'] = line[12:].strip().strip('"\'')
            body = content[end+3:].strip()
    return data, body

def clean_body(body):
    # おすすめVPS/ドメイン/スクールセクションごと削除
    body = re.sub(r'## おすすめの.*$', '', body, flags=re.DOTALL)
    # 念のためA8.netのHTMLタグも除去
    body = re.sub(r'<a href="https://px\.a8\.net/.*?</a>', '', body)
    body = re.sub(r'<img[^>]*a8\.net[^>]*>', '', body)
    # 内部リンクを絶対URLに変換
    body = re.sub(r'\(/posts/([^)]+)\)', r'(https://errsolved.com/posts/\1/)', body)
    body = re.sub(r'\(/en/([^)]+)\)', r'(https://errsolved.com/en/\1/)', body)
    return body.strip()

def post_to_qiita(title, body, tags, slug):
    original_url = f'https://errsolved.com/posts/{slug}/'
    footer = f'\n\n---\n\n> この記事は [errsolved.com]({original_url}) にも掲載しています。'
    full_body = body + footer

    qiita_tags = [{'name': t} for t in tags[:5]]  # Qiitaは最大5タグ

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
        }
    )
    try:
        res = urllib.request.urlopen(req)
        result = json.loads(res.read())
        print(f'Posted to Qiita: {result["url"]}')
        return result['url']
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'HTTPError: {e.code} {e.reason}')
        print(f'Response: {body}')
        raise

# 新規追加されたmdファイルを検出
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
