import os
import re

# アフィリエイトリンク定義
CONOHA = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" rel="nofollow">ConoHa VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZB+CFPZOY+50+4Z0M6A" alt="">'
XSERVER = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZC+2G46B6+CO4+25EKCY" rel="nofollow">XServer VPS</a><img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B3UZC+2G46B6+CO4+25EKCY" alt="">'
SAKURA = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" rel="nofollow">さくらのVPS</a><img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4B3UZB+GC8AGI+D8Y+BWVTE" alt="">'
GMO = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" rel="nofollow">GMOクラウド ALTUS</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+6S3QSY+2KX0+1HL85U" alt="">'
ONAMAE = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+64VU7M+50+2HHVNM" rel="nofollow">お名前.com</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B3VRB+64VU7M+50+2HHVNM" alt="">'
MUUMUU = '<a href="https://px.a8.net/svt/ejp?a8mat=4B3VRB+69NB1U+348+1BNBJM" rel="nofollow">ムームードメイン</a><img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3VRB+69NB1U+348+1BNBJM" alt="">'

# 記事カテゴリ別リンクマッピング
LINK_MAP = {
    # VPS・サーバー・Docker・Linux・nginx系
    'docker':  f'\n\n## おすすめのVPS\n\nDockerを本番環境で動かすなら、VPSが必要です。\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n- {GMO}\n',
    'linux':   f'\n\n## おすすめのVPS\n\nLinuxを本番環境で使うなら、VPSが手軽です。\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n- {GMO}\n',
    'nginx':   f'\n\n## おすすめのVPS\n\nnginxを動かすなら、VPSが必要です。\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n- {GMO}\n',
    'vps':     f'\n\n## おすすめのVPS\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n- {GMO}\n',
    'ssh':     f'\n\n## おすすめのVPS\n\nSSHで接続できるVPSをお探しなら。\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n- {GMO}\n',
    # Cloudflare・DNS・ドメイン系
    'cloudflare': f'\n\n## ドメイン取得はこちら\n\nCloudflareと組み合わせるドメインの取得に。\n\n- {ONAMAE}\n- {MUUMUU}\n',
    'xserver':    f'\n\n## ドメイン取得はこちら\n\n- {ONAMAE}\n- {MUUMUU}\n',
    'domain':     f'\n\n## ドメイン取得はこちら\n\n- {ONAMAE}\n- {MUUMUU}\n',
    # GitHub Actions・git系
    'github-actions': f'\n\n## おすすめのVPS\n\nGitHub Actionsで自動デプロイするサーバーをお探しなら。\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n',
    # その他（デフォルト）
    'default': f'\n\n## おすすめのVPS\n\n- {CONOHA}\n- {XSERVER}\n- {SAKURA}\n',
}

def get_affiliate_block(filename):
    slug = filename.replace('.md', '')
    for key in LINK_MAP:
        if key == 'default':
            continue
        if key in slug:
            return LINK_MAP[key]
    return LINK_MAP['default']

posts_dir = 'src/pages/posts'
updated = 0
skipped = 0

for filename in os.listdir(posts_dir):
    if not filename.endswith('.md'):
        continue

    filepath = os.path.join(posts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # すでにa8.netリンクが入っている場合はスキップ
    if 'a8.net' in content:
        skipped += 1
        continue

    affiliate_block = get_affiliate_block(filename)
    new_content = content.rstrip() + affiliate_block

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    updated += 1
    print(f'Updated: {filename}')

print(f'\n完了: {updated}本更新, {skipped}本スキップ')
