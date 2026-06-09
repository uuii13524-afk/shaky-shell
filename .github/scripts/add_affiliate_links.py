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

# 学習系リンク
PRO_WRITER = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" rel="nofollow">未経験から3ヶ月でプロライターの思考力を習得</a><img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4B3VRB+6M5ER6+4XF8+5ZEMQ" alt="">'
WIN_SCHOOL = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+7N2A9E+529E+5YJRM" rel="nofollow">資格と仕事に強い！個人レッスンのプログラミングスクール【Winスクール】</a><img border="0" width="1" height="1" src="https://www18.a8.net/0.gif?a8mat=4B3VRB+7N2A9E+529E+5YJRM" alt="">'

# ブロック定義
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

LEARNING_BLOCK = f'''
## スキルアップにおすすめ
エラーを自力で解決できる力を身につけたい方に。
- {WIN_SCHOOL}
- {PRO_WRITER}
'''

DEFAULT_BLOCK = f'''
## おすすめのVPS
- {CONOHA}
- {XSERVER_VPS}
- {SAKURA}
'''

# キーワード → ブロックの優先順位: DOMAIN > VPS > LEARNING > DEFAULT
DOMAIN_KEYWORDS = ['cloudflare', 'xserver', 'domain', 'astro-cloudflare', 'astro-sitemap']
VPS_KEYWORDS    = ['docker', 'linux', 'nginx', 'vps', 'ssh', 'wsl', 'github-actions']
LEARNING_KEYWORDS = ['git', 'python', 'node', 'javascript', 'beginner', 'error', 'debug']

# 削除対象マーカー（既存ブロックをすべて検知）
BLOCK_MARKERS = ['## おすすめのVPS', '## ドメイン取得はこちら', '## スキルアップにおすすめ']

def get_block(filename: str) -> str:
    slug = filename.replace('.md', '')
    if any(kw in slug for kw in DOMAIN_KEYWORDS):
        return DOMAIN_BLOCK
    if any(kw in slug for kw in VPS_KEYWORDS):
        return VPS_BLOCK
    if any(kw in slug for kw in LEARNING_KEYWORDS):
        return LEARNING_BLOCK
    return DEFAULT_BLOCK

def strip_existing_block(content: str) -> str:
    """既存のアフィリエイトブロックを末尾から除去する"""
    for marker in BLOCK_MARKERS:
        if marker in content:
            idx = content.index(marker)
            return content[:idx].rstrip()
    # マーカーがなくてもa8.netリンクが残存している場合は警告のみ
    if 'a8.net' in content:
        print('  [WARN] a8.netリンクがマーカー外に存在します。手動確認を推奨。')
    return content.rstrip()

posts_dir = 'src/pages/posts'
updated = 0
skipped = 0

for filename in sorted(os.listdir(posts_dir)):
    if not filename.endswith('.md'):
        skipped += 1
        continue

    filepath = os.path.join(posts_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    clean_content = strip_existing_block(content)
    block = get_block(filename)
    new_content = clean_content + '\n' + block

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    updated += 1
    print(f'Updated: {filename}')

print(f'\n完了: {updated}本更新, {skipped}本スキップ')