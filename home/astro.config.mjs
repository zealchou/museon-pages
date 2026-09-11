import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://muse-on.biz',
  trailingSlash: 'always',
  integrations: [sitemap({ customPages: ['https://muse-on.biz/', 'https://muse-on.biz/about.html', 'https://muse-on.biz/kairos.html', 'https://muse-on.biz/media.html', 'https://muse-on.biz/onemuse.html'] })]
});
