// The docs site of {{REPO}}, published at nstarkman.space/{{NAME}}/ (made by syw-site).
import fs from 'node:fs';
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// $math$ in pages gets the paper's own macros, as components' math does (src/lib/tex.js); an
// unknown command stops the build. facts.json is checked with a clear message in src/lib/facts.js.
const facts = 'public/generated/facts.json';
const macros = fs.existsSync(facts) ? JSON.parse(fs.readFileSync(facts, 'utf8')).macros ?? {} : {};

export default defineConfig({
  site: 'https://nstarkman.space',
  base: '/{{NAME}}',
  build: { format: 'directory' },
  integrations: [mdx()],
  markdown: { remarkPlugins: [remarkMath], rehypePlugins: [[rehypeKatex, { macros, throwOnError: true }]] },
});
