import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const repo = resolve(import.meta.dirname, '..', '..');
const publicUrl = 'https://basketlens-fadhil-9768s-projects.vercel.app/';
const documents = [
  'README.md', 'docs/publication-readiness.md', 'docs/vercel-frontend.md',
  'docs/verification.md', 'docs/release-notes-v1.0.0.md',
  'docs/architecture.md', 'docs/social/linkedin-post.md',
];
const read = path => readFileSync(resolve(repo, path), 'utf8');

test('public-facing documentation uses Vercel rather than retired Streamlit Cloud links', () => {
  for (const path of ['README.md', 'docs/publication-readiness.md',
    'docs/release-notes-v1.0.0.md', 'docs/social/linkedin-post.md']) {
    assert.doesNotMatch(read(path), /https?:\/\/basketlens-retail\.streamlit\.app/i, path);
    assert.ok(read(path).includes(publicUrl), 'Missing public Vercel URL in ' + path);
  }
  assert.match(read('README.md'), /not an actively supported public Streamlit Cloud demo/);
  assert.match(read('docs/publication-readiness.md'), /Mandatory Vercel guest check/);
  assert.match(read('docs/release-notes-v1.0.0.md'), /DRAFT, NOT PUBLISHED/);
});

test('release instructions reflect exact-commit provenance and selective UCI audit', () => {
  assert.ok(read('README.md').includes(publicUrl + 'release.json'));
  assert.match(read('docs/publication-readiness.md'), /current GitLab/);
  assert.match(read('docs/verification.md'), /full-source quality gate \(selective\)/);
  assert.match(read('docs/architecture.md'), /Supported public deployment/);
  assert.match(read('docs/vercel-frontend.md'), /VERCEL_GIT_COMMIT_SHA/);
});

test('local Markdown links in publication-facing documentation resolve', () => {
  for (const file of documents) {
    for (const match of read(file).matchAll(/!?\[[^\]\n]*\]\(([^)]+)\)/g)) {
      const href = match[1].trim().split(/\s+"/)[0].replace(/^<|>$/g, '');
      if (!href || href.startsWith('#') || /^[a-z][a-z0-9+.-]*:/i.test(href)) continue;
      const relative = decodeURIComponent(href.split('#')[0].split('?')[0]);
      assert.ok(existsSync(resolve(repo, dirname(file), relative)),
        file + ' has a broken relative link: ' + href);
    }
  }
});
