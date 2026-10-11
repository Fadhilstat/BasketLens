import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { buildProvenance } from '../scripts/provenance.mjs';

const exhibit = '5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20';
const sha = 'a'.repeat(40);

test('Vercel release exposes only the expected public provenance fields', () => {
  const stamp = buildProvenance({
    VERCEL: '1', VERCEL_GIT_COMMIT_SHA: sha.toUpperCase(),
    EXAMPLE_PRIVATE_SECRET: 'must-not-be-published',
  }, exhibit, 1500);
  assert.deepEqual(stamp, {
    schema: 'basketlens.release-provenance.v1',
    gitSha: sha, source: 'vercel-git', exhibitSha256: exhibit, ruleCount: 1500,
  });
  assert.ok(!JSON.stringify(stamp).includes('must-not-be-published'));
});

test('Vercel build fails closed without a valid source SHA', () => {
  assert.throws(() => buildProvenance({ VERCEL: '1' }, exhibit, 1500), /Missing VERCEL_GIT_COMMIT_SHA/);
  assert.throws(() => buildProvenance({ VERCEL: '1', VERCEL_GIT_COMMIT_SHA: 'abc' }, exhibit, 1500), /Invalid git commit SHA/);
});

test('GitLab CI builds carry their own full git commit SHA', () => {
  const stamp = buildProvenance({ CI_COMMIT_SHA: sha }, exhibit, 1500);
  assert.equal(stamp.source, 'gitlab-ci');
  assert.equal(stamp.gitSha, sha);
});

test('local build reports unknown SHA rather than inventing provenance', () => {
  assert.deepEqual(buildProvenance({}, exhibit, 1500), {
    schema: 'basketlens.release-provenance.v1',
    gitSha: null, source: 'unverified-local', exhibitSha256: exhibit, ruleCount: 1500,
  });
});

test('invalid public dataset fingerprints and counts are rejected', () => {
  assert.throws(() => buildProvenance({}, 'wrong', 1500));
  assert.throws(() => buildProvenance({}, exhibit, 1499));
});

test('emitted release manifest has the expected public contract', () => {
  const release = JSON.parse(readFileSync(resolve(import.meta.dirname, '..', 'dist', 'release.json'), 'utf8'));
  assert.equal(release.schema, 'basketlens.release-provenance.v1');
  assert.equal(release.exhibitSha256, exhibit);
  assert.equal(release.ruleCount, 1500);
  assert.ok(release.gitSha === null || /^[0-9a-f]{40}$/.test(release.gitSha));
});
