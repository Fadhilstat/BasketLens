import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { gunzipSync } from 'node:zlib';

// The source is the audited aggregate-only public exhibit, not UCI invoice data.
const root = resolve(import.meta.dirname, '..');
const target = resolve(root, 'dist');
const exhibit = resolve(root, 'data', 'basketlens_public_v1.b64');
const canonical = resolve(root, '..', '..', 'data', 'public_demo', 'basketlens_public_v1.b64');
const expectedHash = '5303df81bb5d8c5c4eb452a774d1c9d42233ff9bf56d6319021eefc6dfd69b20';
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const finite = (value, label) => {
  const n = Number(value);
  assert.ok(value !== null && value !== '' && Number.isFinite(n), `Invalid ${label}`);
  return n;
};
const optional = value => value === null || value === undefined || value === '' ? null : finite(value, 'optional metric');
const safeCode = value => {
  assert.equal(typeof value, 'string', 'Expected string SKU');
  assert.ok(value.length > 0 && value.length <= 80 && !/[<>\x00-\x1f]/.test(value), 'Invalid public SKU');
  return value;
};

async function loadExhibit() {
  const b64 = (await readFile(exhibit, 'ascii')).trim();
  assert.ok(/^[A-Za-z0-9+/]+={0,2}$/.test(b64), 'Invalid exhibit base64');
  const compressed = Buffer.from(b64, 'base64');
  assert.ok(compressed.length < 6_000_000 && compressed.length > 0, 'Unexpected exhibit size');
  const actualHash = digest(compressed);
  const companion = (await readFile(exhibit + '.sha256', 'utf8')).trim();
  assert.equal(actualHash, expectedHash, 'Exhibit fingerprint changed without review');
  assert.equal(actualHash, companion, 'Exhibit SHA256 mismatch');
  if (existsSync(canonical)) {
    const canonicalBytes = Buffer.from((await readFile(canonical, 'ascii')).trim(), 'base64');
    assert.equal(digest(canonicalBytes), actualHash, 'Site mirror differs from canonical public exhibit');
  }
  const pack = JSON.parse(gunzipSync(compressed).toString('utf8'));
  assert.equal(pack.schema, 'basketlens.public-demo.v1');
  assert.equal(pack.publication?.visible_rule_count, 1500);
  assert.equal(pack.publication?.full_rule_count, 113001);
  assert.equal(Number(pack.manifest?.basket_count_all), 40280);
  assert.equal(pack.manifest?.partial_data, false);
  assert.equal(pack.manifest?.inconsistent_invoice_policy, 'quarantine');
  assert.ok(Array.isArray(pack.tables?.rules) && pack.tables.rules.length === 1500);
  assert.ok(Array.isArray(pack.tables?.evaluation) && pack.tables.evaluation.length === 1500);
  assert.ok(Array.isArray(pack.tables?.products) && pack.tables.products.length > 0);
  for (const [name, records] of Object.entries(pack.tables)) {
    assert.ok(!['basket_id', 'invoice_no', 'customer_id', 'source_row', 'email'].some(
      field => records.some(row => Object.hasOwn(row, field))), `Unexpected private field in ${name}`);
  }
  return { pack, actualHash };
}

function explorePayload(pack, hash) {
  const catalog = new Map(pack.tables.products.map(product => [
    safeCode(String(product.stock_code)), String(product.description || product.stock_code).trim().slice(0, 150),
  ]));
  const ruleKey = rule => `${rule.antecedent}\x00${rule.consequent}`;
  const evaluation = new Map(pack.tables.evaluation.map(row => [ruleKey(row), row]));
  const seen = new Set();
  const rules = pack.tables.rules.map(rule => {
    const key = ruleKey(rule);
    assert.ok(!seen.has(key), 'Duplicate public association rule');
    seen.add(key);
    const later = evaluation.get(key);
    assert.ok(later, 'Missing verified holdout evaluation');
    const antecedent = String(rule.antecedent).split('||').map(safeCode);
    const consequent = safeCode(String(rule.consequent));
    assert.ok(antecedent.length >= 1 && antecedent.length <= 2, 'Unexpected antecedent');
    const count = finite(rule.joint_count, 'training co-purchase count');
    const confidence = finite(rule.confidence, 'training confidence');
    const lift = finite(rule.lift, 'training lift');
    const fires = finite(later.fires, 'holdout antecedent baskets');
    const hits = finite(later.hits, 'holdout joint baskets');
    assert.ok(Number.isInteger(count) && count >= 1 && confidence >= 0 && confidence <= 1);
    assert.ok(lift > 0 && Number.isInteger(fires) && Number.isInteger(hits) && hits >= 0 && hits <= fires);
    const hconfidence = optional(later.holdout_confidence);
    const hlift = optional(later.holdout_lift);
    if (fires > 0 && hconfidence !== null) assert.ok(Math.abs(hconfidence - hits / fires) < 1e-6);
    return {
      a: antecedent.map(sku => ({ sku, name: catalog.get(sku) || sku })),
      c: { sku: consequent, name: catalog.get(consequent) || consequent },
      joint: count, confidence, lift, fires, hits,
      holdoutConfidence: fires ? hconfidence : null,
      holdoutLift: fires ? hlift : null,
    };
  });
  rules.sort((a, b) => b.joint - a.joint || b.confidence - a.confidence || b.lift - a.lift ||
    a.a.map(item => item.sku).join('||').localeCompare(b.a.map(item => item.sku).join('||')) ||
    a.c.sku.localeCompare(b.c.sku));
  assert.equal(rules.length, 1500);
  return {
    schema: 'basketlens.rule-explorer.v1',
    exhibitSha256: hash,
    selection: 'Training-selected published rules, sorted by earlier joint count, confidence and lift. Holdout never used for selection or ranking.',
    cohort: { baskets: 40280, earlier: 32224, later: 8056 },
    ruleCount: rules.length,
    rules,
  };
}

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
const { pack, actualHash } = await loadExhibit();
const output = explorePayload(pack, actualHash);
await Promise.all([
  copyFile(resolve(root, 'index.html'), resolve(target, 'index.html')),
  copyFile(resolve(root, 'explorer.js'), resolve(target, 'explorer.js')),
  copyFile(resolve(root, 'basket-matcher.mjs'), resolve(target, 'basket-matcher.mjs')),
  copyFile(resolve(root, 'basket-builder.mjs'), resolve(target, 'basket-builder.mjs')),
  writeFile(resolve(target, 'explorer.v1.json'), JSON.stringify(output) + '\n', 'utf8'),
]);
console.log(`Built verified BasketLens explorer: ${output.ruleCount} rules, source SHA256 ${actualHash}`);