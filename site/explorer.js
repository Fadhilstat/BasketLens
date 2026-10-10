(() => {
  'use strict';
  const root = document.getElementById('explorer');
  if (!root) return;
  const query = document.getElementById('rule-query');
  const lift = document.getElementById('rule-lift');
  const count = document.getElementById('rule-joint');
  const type = document.getElementById('rule-type');
  const form = document.getElementById('explorer-filters');
  const results = document.getElementById('rule-results');
  const summary = document.getElementById('rule-summary');
  const empty = document.getElementById('rule-empty');
  const error = document.getElementById('rule-error');
  const more = document.getElementById('rule-more');
  const retry = document.getElementById('rule-retry');
  const fingerprint = document.getElementById('rule-fingerprint');
  let dataset = null;
  let visible = 8;
  let generation = 0;
  let filtered = [];
  const format = value => Number(value).toLocaleString('en-GB');
  const percentage = value => `${(value * 100).toFixed(1)}%`;
  const productText = products => products.map(item => `${item.name} (${item.sku})`).join(' + ');
  const text = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = String(value);
    return element;
  };
  const metadata = (label, value, hint) => {
    const cell = text('div', 'rule-metric', '');
    cell.append(text('span', 'rule-metric-label', label), text('strong', '', value));
    if (hint) cell.append(text('small', '', hint));
    return cell;
  };

  function card(rule) {
    const item = text('article', 'rule-row', '');
    item.setAttribute('role', 'listitem');
    const product = text('div', 'rule-relationship', '');
    product.append(
      text('span', 'rule-description-label', 'IF AN EARLIER BASKET CONTAINS'),
      text('strong', 'rule-product-name', productText(rule.a)),
      text('span', 'rule-description-label rule-then', 'IT ALSO CONTAINS'),
      text('strong', 'rule-product-name', productText([rule.c])),
    );
    const measures = text('div', 'rule-measures', '');
    measures.append(
      metadata('Training baskets together', format(rule.joint), 'Earlier period'),
      metadata('Training confidence', percentage(rule.confidence), 'Descriptive association'),
      metadata('Training lift', `${rule.lift.toFixed(2)}x`, 'Relative to baseline'),
    );
    const holdout = text('div', 'rule-holdout', '');
    holdout.append(text('span', 'rule-description-label', 'LATER HOLDOUT CHECK'));
    if (rule.fires === 0) {
      holdout.append(text('strong', 'rule-holdout-number', 'Not observed'));
      holdout.append(text('small', '', 'Antecedent absent from later baskets'));
    } else {
      holdout.append(text('strong', 'rule-holdout-number', `${format(rule.hits)} / ${format(rule.fires)}`));
      const rate = rule.holdoutConfidence;
      holdout.append(text('small', '', `${rate === null ? 'Rate unavailable' : percentage(rate)} of later antecedent baskets also contained the consequent`));
    }
    item.append(product, measures, holdout);
    return item;
  }

  function render() {
    if (!dataset) return;
    const needle = query.value.trim().toLocaleLowerCase('en');
    const minimumLift = Number(lift.value);
    const minimumJoint = Number(count.value);
    const ruleType = type.value;
    filtered = dataset.rules.filter(rule => {
      if (rule.lift < minimumLift || rule.joint < minimumJoint) return false;
      if (ruleType === 'single' && rule.a.length !== 1) return false;
      if (ruleType === 'multi' && rule.a.length !== 2) return false;
      const searchable = `${productText(rule.a)} ${productText([rule.c])}`.toLocaleLowerCase('en');
      return !needle || searchable.includes(needle);
    });
    const shown = Math.min(visible, filtered.length);
    const fragment = document.createDocumentFragment();
    for (let index = 0; index < shown; index++) fragment.append(card(filtered[index]));
    results.replaceChildren(fragment);
    summary.textContent = `${format(filtered.length)} of ${format(dataset.ruleCount)} published rules, showing ${format(shown)}`;
    empty.hidden = filtered.length !== 0;
    more.hidden = shown >= filtered.length;
    more.textContent = `Show ${Math.min(8, filtered.length - shown)} more rules`;
  }

  async function load() {
    const request = ++generation;
    error.hidden = true;
    retry.hidden = true;
    summary.textContent = 'Loading 1,500 audited rules...';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch('./explorer.v1.json', { cache: 'no-store', signal: controller.signal });
      if (!response.ok) throw new Error('Dataset unavailable');
      const payload = await response.json();
      if (payload.schema !== 'basketlens.rule-explorer.v1' || payload.ruleCount !== 1500 ||
          !Array.isArray(payload.rules) || payload.rules.length !== 1500 ||
          !/^[a-f0-9]{64}$/.test(payload.exhibitSha256)) throw new Error('Invalid dataset version');
      if (request !== generation) return;
      dataset = payload;
      fingerprint.textContent = `Exhibit SHA256 ${payload.exhibitSha256.slice(0, 12)}... / 1,500 training-selected rules`;
      visible = 8;
      render();
    } catch {
      if (request !== generation) return;
      dataset = null;
      results.replaceChildren();
      summary.textContent = 'The published rule table could not be loaded.';
      empty.hidden = true;
      more.hidden = true;
      error.hidden = false;
      retry.hidden = false;
    } finally {
      clearTimeout(timeout);
    }
  }

  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', () => { visible = 8; render(); });
  form.addEventListener('change', () => { visible = 8; render(); });
  form.addEventListener('reset', event => {
    event.preventDefault();
    query.value = '';
    lift.value = '0';
    count.value = '1';
    type.value = 'all';
    visible = 8;
    render();
  });
  more.addEventListener('click', () => { visible += 8; render(); });
  retry.addEventListener('click', load);
  load();
})();