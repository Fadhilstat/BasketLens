import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const html = readFileSync(resolve(root, 'index.html'), 'utf8');

test('source-backed research figures and honest evidence boundary', () => {
  for (const fact of ['40,280', '32,224', '8,056', '1,067,371', '1,500', 'SKU 22386', 'SKU 85099B', '83 conflicting invoices', '63.1294', '67.0673', '6.24×', '6.77×', '1,166 joint baskets', '279 of 416 baskets']) {
    assert.ok(html.includes(fact), `Expected documented fact: ${fact}`);
  }
  assert.match(html, /not incremental revenue|not an experiment/i);
  assert.ok(html.includes('Read full case study'));
  assert.ok(html.includes('Interactive analysis and reproducible methods are documented in the source repository.'));
  assert.doesNotMatch(html, /basketlens-retail\.streamlit\.app/);
});

test('internal links target existing anchors', () => {
  const anchorIds = new Set([...html.matchAll(/\bid="([a-z][a-z0-9-]+)"/g)].map(m => m[1]));
  const internalLinks = [...html.matchAll(/href="#([a-z][a-z0-9-]+)"/g)].map(m => m[1]);
  assert.ok(internalLinks.length >= 5);
  for (const hash of internalLinks) assert.ok(anchorIds.has(hash), `Missing anchor: ${hash}`);
});

test('functional accessible controls and reduced motion', () => {
  for (const token of ['class="skip-link"', 'role="tablist"', 'role="tabpanel"', 'role="progressbar"', 'ArrowRight', 'ArrowLeft', 'aria-selected', 'navigator.clipboard.writeText', 'focus-visible', 'prefers-reduced-motion']) {
    assert.ok(html.includes(token), `Missing accessibility behavior: ${token}`);
  }
  assert.doesNotMatch(html, /href="#"|javascript:|Lorem ipsum|99\.9% uptime|AI powered|trusted by/i);
  assert.ok(!html.includes('\u2014'));
});

test('retail intelligence dashboard has true visual structure, real numbers and responsive navigation', () => {
  for (const token of ['class="app-shell"', 'class="sidebar"', 'class="kpi-row"', 'class="hero-banner"', 'class="finding-grid"', 'class="evidence-card"', 'class="compare-row"', 'class="method-steps"', 'class="decision-panel"', 'class="bag-outline"']) {
    assert.ok(html.includes(token), `Dashboard structure missing: ${token}`);
  }
  assert.ok(html.includes('Confidence by period'));
  assert.ok(html.includes('2009 - 2011'));
  assert.ok(html.includes('40,280'));
  assert.ok(html.includes('67.1%'));
});

test('build exposes exactly one self-contained HTML entrypoint', () => {
  assert.match(html, /<style>[\s\S]*<\/style>/);
  assert.match(html, /<script>[\s\S]*<\/script>/);
  assert.doesNotMatch(html, /src="\.\/app\.js"|href="\.\/styles\.css"/);
  assert.match(html, /target="_blank" rel="noopener noreferrer"/);
});

test('visitor can reach the new source-backed explorer without empty navigation', () => {
  for (const marker of ['id="explorer"', 'id="rule-query"', 'id="rule-lift"', 'id="rule-joint"',
    'id="rule-type"', 'id="rule-results"', 'id="rule-more"', 'id="rule-error"',
    'href="#explorer"', 'src="./explorer.js" defer']) {
    assert.ok(html.includes(marker), `Missing working explorer structure: ${marker}`);
  }
  assert.match(html, /Training-selected|Selected using earlier orders only/i);
  assert.match(html, /neither is a measured response to a recommendation/i);
  assert.doesNotMatch(html, /src="https?:\/\/|data:\s*text\/html/i);
});
test('M6.8 retail typography and Vercel-only publication', () => {
  for (const token of ['Manrope','Instrument Serif','fonts.googleapis.com/css2?',
    'font-synthesis: none','font-variant-numeric: tabular-nums','id="basket"','id="explorer"'])
    assert.ok(html.includes(token), `Missing M6.8 contract: ${token}`);
  assert.ok(!html.includes('font: 14px/1.5 Arial, Helvetica, sans-serif'));
  assert.ok(!html.includes('basketlens-retail.streamlit.app'));
});
