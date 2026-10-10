import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const artifactPath = resolve(root, 'dist', 'explorer.v1.json');
const raw = readFileSync(artifactPath, 'utf8');
const data = JSON.parse(raw);

test('exact source-backed and reasonably lightweight dataset contract', () => {
  assert.equal(data.schema, 'basketlens.rule-explorer.v1');
  assert.equal(data.exhibitSha256, '5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20');
  assert.deepEqual(data.cohort, { baskets: 40280, earlier: 32224, later: 8056 });
  assert.equal(data.ruleCount, 1500);
  assert.equal(data.rules.length, 1500);
  assert.ok(statSync(artifactPath).size < 2_000_000, 'Explorer payload too large');
  assert.doesNotMatch(raw, /"(?:invoice_no|customer_id|basket_id|source_row|email)"\s*:/);
  assert.ok(data.selection.includes('Holdout never used for selection or ranking'));
});

test('earlier-training ranking, valid rule arithmetic and no leakage', () => {
  for (let i = 0; i < data.rules.length; i++) {
    const rule = data.rules[i];
    assert.ok(rule.a.length === 1 || rule.a.length === 2);
    assert.ok(rule.joint >= 1 && rule.confidence >= 0 && rule.confidence <= 1 && rule.lift > 0);
    assert.ok(rule.fires >= rule.hits && rule.hits >= 0);
    if (rule.fires === 0) assert.equal(rule.holdoutConfidence, null);
    if (i > 0) assert.ok(data.rules[i - 1].joint >= rule.joint, 'Holdout ranking leaked into training order');
  }
});

test('published Pink Polkadot pair is linked to actual later observations', () => {
  const rule = data.rules.find(item => item.a.length === 1 &&
    item.a[0].sku === '22386' && item.c.sku === '85099B');
  assert.ok(rule, 'Canonical training-selected hero rule is absent');
  assert.equal(rule.joint, 1166);
  assert.ok(Math.abs(rule.confidence - 0.631294) < 0.00001);
  assert.equal(rule.fires, 416);
  assert.equal(rule.hits, 279);
  assert.ok(Math.abs(rule.holdoutConfidence - 279 / 416) < 0.00001);
});