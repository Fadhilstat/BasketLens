// A deterministic, training-only matching layer for the aggregate public rule exhibit.
// No transaction rows, identity fields, model inference or holdout-based ranking.
export function catalogueFromRules(rules) {
  if (!Array.isArray(rules)) throw new TypeError('Rules must be an array');
  const products = new Map();
  for (const rule of rules) {
    for (const item of rule.a || []) {
      if (typeof item.sku !== 'string' || !item.sku || products.has(item.sku)) continue;
      products.set(item.sku, { sku: item.sku, name: String(item.name || item.sku) });
    }
  }
  return [...products.values()].sort((a, b) =>
    a.name.localeCompare(b.name, 'en') || a.sku.localeCompare(b.sku, 'en'));
}

export function searchCatalogue(catalogue, search, selected = [], limit = 7) {
  if (!Array.isArray(catalogue)) throw new TypeError('Catalogue must be an array');
  const query = String(search).trim().toLocaleLowerCase('en');
  if (query.length < 2) return [];
  const excluded = new Set(selected);
  return catalogue.filter(item => !excluded.has(item.sku) &&
    (item.name + ' ' + item.sku).toLocaleLowerCase('en').includes(query)).slice(0, limit);
}

export function matchBasket(rules, skuList, limit = 6) {
  if (!Array.isArray(rules) || !Array.isArray(skuList)) throw new TypeError('Invalid basket inputs');
  if (!Number.isInteger(limit) || limit < 1 || limit > 20) throw new RangeError('Invalid result limit');
  const basket = new Set(skuList);
  if (basket.size > 3) throw new RangeError('The example basket supports at most 3 different products');
  if (!basket.size) return { total: 0, suggestions: [] };
  const eligible = rules.filter(rule =>
    Array.isArray(rule.a) && rule.a.length > 0 &&
    rule.a.every(item => basket.has(item.sku)) &&
    rule.c && !basket.has(rule.c.sku));
  eligible.sort((a, b) => b.a.length - a.a.length ||
    b.joint - a.joint || b.confidence - a.confidence || b.lift - a.lift ||
    a.c.sku.localeCompare(b.c.sku, 'en'));
  const seen = new Set();
  const unique = [];
  for (const rule of eligible) {
    if (seen.has(rule.c.sku)) continue;
    seen.add(rule.c.sku);
    unique.push(rule);
  }
  return { total: unique.length, suggestions: unique.slice(0, limit) };
}
