import os

# VPS系リンク
CONOHA = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">'
XSERVER_VPS = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">'
SAKURA = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">'
GMO = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">'

# ドメイン系リンク
ONAMAE = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">'
MUUMUU = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">'
VALUE_DOMAIN = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" rel="nofollow">Value-Domain</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3WJ5+B72HBM+1JUK+I3D2Q" alt="">'
XSERVER_DOMAIN = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" rel="nofollow">XServerドメイン</a><img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4B3WJ5+BFEJSI+CO4+15ORS2" alt="">'
STAR_DOMAIN = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" rel="nofollow">スタードメイン</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3WJ5+BDM8Z6+1WTI+C0B9U" alt="">'

VPS_BLOCK = f'''

## おすすめのVPS

VPSを使って本番環境を構築するなら、以下のサービスがおすすめです。

- {CONOHA}
- {XSERVER_VPS}
- {SAKURA}
- {GMO}
'''

DOMAIN_BLOCK = f'''

## ドメイン取得はこちら

Cloudflareと組み合わせるドメインの取得に。

- {ONAMAE}
- {MUUMUU}
- {VALUE_DOMAIN}
- {XSERVER_DOMAIN}
- {STAR_DOMAIN}
'''

DEFAULT_BLOCK = f'''

## おすすめのVPS

- {CONOHA}
- {XSERVER_VPS}
- {SAKURA}
'''

VPS_KEYWORDS = ['docker', 'linux', 'nginx', 'vps', 'ssh', 'wsl', 'github-actions']
DOMAIN_KEYWORDS = ['cloudflare', 'xserver', 'domain', 'astro-cloudflare', 'astro-sitemap']

def get_block(filename):
    slug = filename.replace('.md', '')
    for kw in DOMAIN_KEYWORDS:
        if kw in slug:
            return DOMAIN_BLOCK
    for kw in VPS_KEYWORDS:
        if kw in slug:
            return VPS_BLOCK
    return DEFAULT_BLOCK

posts_dir = 'src/pages/posts'
updated = 0
skipped = 0

for filename in os.listdir(posts_dir):
    if not filename.endswith('.md'):
        continue
    filepath = os.path.join(posts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 既存のアフィリエイトブロックを削除して入れ直す
    if '## おすすめのVPS' in content or 'a8.net' in content:
        # ブロック前のコンテンツだけ残す
        for marker in ['## おすすめのVPS', '## ドメイン取得はこちら']:
            if marker in content:
                content = content[:content.index(marker)].rstrip()
                break

    block = get_block(filename)
    new_content = content + block

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    updated += 1
    print(f'Updated: {filename}')

print(f'\n完了: {updated}本更新, {skipped}本スキップ')
