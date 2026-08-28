import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

// ATT website — Austin Trading Team / Austin Trading Engine
// Static output, suitable for GitHub Pages (free tier).
export default defineConfig({
  // Public site hosted on GitHub Pages. To use a custom domain later,
  // change `site` to e.g. 'https://att.trading' and remove the `base` field
  // (or set it to '/').
  site: process.env.ATT_SITE_URL ?? 'https://paulaustin3977.github.io',
  base: '/ATT-Trading-Framework',
  output: 'static',
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
  },
  integrations: [
    sitemap(),
  ],
  markdown: {
    syntaxHighlight: 'shiki',
    shikiConfig: {
      theme: 'github-dark-dimmed',
      wrap: true,
    },
  },
  rehypePlugins: [
    rehypeSlug,
    [
      rehypeAutolinkHeadings,
      {
        behavior: 'wrap',
        properties: { className: ['heading-anchor'] },
      },
    ],
  ],
  vite: {
    build: {
      cssCodeSplit: true,
    },
  },
  server: {
    host: '0.0.0.0',
    port: 4321,
  },
});
