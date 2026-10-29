// The paper site's tabs, in order; a tab with nothing in it is left out.
import { facts } from './facts.js';
import { config, resolve, root } from './store.js';

const infoPages = import.meta.glob('../pages/info/*.{md,mdx,astro}');

/** The webapps on the Explore tab, in syw-site.yml's order. */
export const exploreApps = () => Object.entries(facts.webapps ?? {}).filter(([, w]) => w.explore).map(([name, w]) => ({ name, ...w }));

/** The grants that funded the paper: `grant` items among its refs on nstarkman.space. */
export const grants = () => (root ? (resolve(root).refs ?? []).map(resolve).filter((i) => i?.type === 'grant') : []);

/** Co-authors on the collaborator map: those the snapshot places. */
export const hasMap = () => config.collaborators.people.length > 0;

/** The author's own Info pages (src/pages/info/*), by URL. */
export const infoLinks = () => Object.keys(infoPages).map((f) => f.replace('../pages/', '').replace(/\.(mdx?|astro)$/, '/')).filter((p) => p !== 'info/index/');

export function tabs() {
  return [
    { key: 'overview', label: 'Overview', href: '' },
    exploreApps().length && { key: 'explore', label: 'Explore', href: 'explore/' },
    { key: 'figures', label: 'Figures', href: 'figures/' },
    (hasMap() || grants().length || infoLinks().length) && { key: 'info', label: 'Info', href: 'info/' },
    { key: 'cite', label: 'Cite', href: 'cite/' },
  ].filter(Boolean);
}
