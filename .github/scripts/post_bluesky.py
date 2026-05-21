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

# Post each article
for filepath in new_files:
    title = ''
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('title:'):
                title = line.replace('title:', '').strip().strip("'\"")
                break

    slug = os.path.basename(filepath).replace('.md', '')
    url = f'https://errsolved.com/posts/{slug}'
    text = f'新記事: {title}\n{url}\n#開発 #エラー解決'

    post_data = json.dumps({
        'repo': did,
        'collection': 'app.bsky.feed.post',
        'record': {
            'text': text,
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
