// The paper's LaTeX as HTML: math through KaTeX (an error stops the build), siunitx's \qty and
// \qtyrange, and the text commands papers use. Not a TeX engine: extend it when a paper needs more.
import katex from 'katex';

const UNITS = {
  kpc: 'kpc', pc: 'pc', Mpc: 'Mpc', km: 'km', meter: 'm', metre: 'm', second: 's', kilo: 'k',
  Gyr: 'Gyr', Myr: 'Myr', year: 'yr', degree: '^{\\circ}', deg: '^{\\circ}', Msun: 'M_{\\odot}',
};

// \qty{1.2e-10}{\meter\per\second\squared} → 1.2\times10^{-10}\,\mathrm{m\,s^{-2}}
function units(spec) {
  const parts = [];
  let per = false;
  for (const [, name] of spec.matchAll(/\\([A-Za-z]+)/g)) {
    if (name === 'per') { per = true; continue; }
    if (name === 'squared' || name === 'cubed') {
      const p = name === 'squared' ? 2 : 3;
      parts[parts.length - 1] = parts.at(-1).replace(/\^\{(-?)1\}$|$/, (m, neg) => `^{${neg || ''}${p}}`);
      continue;
    }
    const u = UNITS[name] ?? `\\mathrm{${name}}`;
    parts.push((/^[A-Za-z]+$/.test(u) ? `\\mathrm{${u}}` : u) + (per ? '^{-1}' : ''));
    per = false;
  }
  return parts.join('\\,');
}
const num = (n) => n.replace(/e([+-]?\d+)/, (_, e) => `\\times10^{${Number(e)}}`);
const siunitx = (s) => s
  .replace(/\\qtyrange\{([^}]*)\}\{([^}]*)\}\{((?:[^{}]|\{[^}]*\})*)\}/g, (_, a, b, u) => `${num(a)}\\text{--}${num(b)}\\,${units(u)}`)
  .replace(/\\qty\{([^}]*)\}\{((?:[^{}]|\{[^}]*\})*)\}/g, (_, v, u) => `${num(v)}\\,${units(u)}`)
  .replace(/\\num\{([^}]*)\}/g, (_, v) => num(v));

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export const math = (s) => katex.renderToString(siunitx(s), { throwOnError: true, output: 'html' });

function text(s) {
  return esc(s)
    .replace(/\\(?:cite[pt]?|citealp|citeauthor)\*?(?:\[[^\]]*\])*\{[^}]*\}/g, '')
    .replace(/\\(?:emph|textit)\{([^}]*)\}/g, '<em>$1</em>')
    .replace(/\\textbf\{([^}]*)\}/g, '<strong>$1</strong>')
    .replace(/\\url\{([^}]*)\}/g, '<a href="$1">$1</a>')
    .replace(/\\([%&_#$])/g, '$1')
    .replace(/---/g, '—').replace(/--/g, '–').replace(/~/g, '&nbsp;')
    .replace(/``/g, '“').replace(/''/g, '”')
    .replace(/\\[A-Za-z]+\*?\{([^}]*)\}/g, '$1')
    .replace(/\\[A-Za-z]+\*?/g, '')
    .replace(/[{}]/g, '');
}

const SIUNITX = /\\qtyrange\{[^}]*\}\{[^}]*\}\{(?:[^{}]|\{[^}]*\})*\}|\\qty\{[^}]*\}\{(?:[^{}]|\{[^}]*\})*\}|\\num\{[^}]*\}/g;

// Running text: siunitx commands in it are rendered as math, the rest as text.
function prose(s) {
  const rendered = [];
  s = s.replace(SIUNITX, (m) => `\u0000${rendered.push(math(m)) - 1}\u0000`);
  return text(s).replace(/\u0000(\d+)\u0000/g, (_, i) => rendered[i]);
}

/** Text with inline $math$; with refs, \ref{label} becomes that figure's number. */
export function tex(s, refs = {}) {
  s = s.replace(/\\(?:c|C)?ref\{([^}]*)\}/g, (_, l) => refs[l] ?? '?');
  return s.split(/(?<!\\)\$/).map((part, i) => (i % 2 ? math(part) : prose(part))).join('');
}

/** A \variable value: math when it has TeX in it, text otherwise. */
export const value = (s) => (s.includes('$') ? tex(s) : /[\\^_]/.test(s) ? math(s) : prose(s));
