import rss from '@astrojs/rss';

export async function GET(context) {
  const postImports = import.meta.glob('./posts/*.md', { eager: true });
  
  const posts = Object.entries(postImports).map(([path, post]) => ({
    title: post.frontmatter.title,
    pubDate: new Date(post.frontmatter.date),
    link: path.replace('./posts/', '/posts/').replace('.md', ''),
  }));

  posts.sort((a, b) => b.pubDate - a.pubDate);

  return rss({
    title: 'ErrNotes - エラー解決ログ',
    description: '実際に詰まったエラーの記録と解決ログ。Docker・Linux・GitHub Actions・Cloudflareなど開発現場のリアルなトラブルシューティング集。',
    site: context.site,
    items: posts,
    customData: `<language>ja</language>`,
  });
}
