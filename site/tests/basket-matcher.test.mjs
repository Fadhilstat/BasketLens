import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { catalogueFromRules, searchCatalogue, matchBasket } from '../basket-matcher.mjs';

const root = resolve(import.meta.dirname, '..');
const publicRules = JSON.parse(readFileSync(resolve(root, 'dist', 'explorer.v1.json'), 'utf8')).rules;
const catalogue = catalogueFromRules(publicRules);

test('real audited catalogue and featured starter basket are available', () => {
  assert.ok(catalogue.length > 20);
  assert.ok(catalogue.some(item => item.sku === '22386'));
  assert.ok(searchCatalogue(catalogue, 'pOlKaDot').some(item => item.sku === '22386'));
  assert.ok(searchCatalogue(catalogue, '22386').some(item => item.sku === '22386'));
  const hero = publicRules.find(rule => rule.a.length === 1 &&
    rule.a[0].sku === '22386' && rule.c.sku === '85099B');
  assert.ok(hero);
  const matched = matchBasket([hero], ['22386']);
  assert.equal(matched.total, 1);
  assert.equal(matched.suggestions[0].hits, 279);
  assert.equal(matched.suggestions[0].fires, 416);
});

test('antecedent must be contained in selected basket, consequent must be absent', () => {
  const single = { a: [{sku:'A'}], c:{sku:'C'}, joint:12, confidence:.5, lift:2, fires:2, hits:1 };
  const pair = { a: [{sku:'A'},{sku:'B'}], c:{sku:'D'}, joint:8, confidence:.5, lift:3, fires:0, hits:0 };
  assert.deepEqual(matchBasket([single,pair], ['A']).suggestions.map(r=>r.c.sku), ['C']);
  assert.deepEqual(matchBasket([single,pair], ['A','B']).suggestions.map(r=>r.c.sku), ['D','C']);
  assert.equal(matchBasket([single,pair], ['A','C']).total, 0);
  assert.equal(matchBasket([single,pair], []).total, 0);
});

test('same consequent is unique, more-specific earlier rule wins', () => {
  const single = {a:[{sku:'A'}],c:{sku:'X'},joint:100,confidence:.9,lift:6,fires:0,hits:0};
  const pair = {a:[{sku:'A'},{sku:'B'}],c:{sku:'X'},joint:40,confidence:.7,lift:2,fires:0,hits:0};
  const result = matchBasket([single,pair],['A','B']);
  assert.equal(result.total, 1);
  assert.equal(result.suggestions[0], pair);
});

test('ranking never uses later-period success and respects maximum cart size', () => {
  const strong = {a:[{sku:'A'}],c:{sku:'X'},joint:90,confidence:.6,lift:2,fires:50,hits:0};
  const weak = {a:[{sku:'A'}],c:{sku:'Y'},joint:20,confidence:.9,lift:9,fires:50,hits:50};
  assert.deepEqual(matchBasket([weak,strong], ['A']).suggestions.map(r=>r.c.sku),['X','Y']);
  assert.equal(matchBasket([weak,strong], ['A','A']).total, 2);
  assert.throws(()=>matchBasket([strong], ['A','B','C','D']), RangeError);
  assert.throws(()=>matchBasket([strong], ['A'], 21), RangeError);
  assert.deepEqual(searchCatalogue(catalogue,'',[]),[]);
});

test('basket feature is reachable and does not introduce data-writing inputs', () => {
  const html=readFileSync(resolve(root,'index.html'),'utf8');
  for(const token of ['id="basket"','id="basket-search"','id="basket-candidates"',
    'id="basket-chosen"','id="basket-example"','href="#basket"',
    'src="./basket-builder.mjs"','Training-selected','No sales uplift']) {
      assert.ok(html.includes(token),'Basket feature missing '+token);
  }
  assert.doesNotMatch(html, /basketlens-retail\.streamlit\.app|customer_id|invoice_no/i);
});
