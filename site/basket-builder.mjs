import { catalogueFromRules, searchCatalogue, matchBasket } from './basket-matcher.mjs';

const section = document.getElementById('basket');
if (section) {
  const byId = id => document.getElementById(id);
  const search = byId('basket-search');
  const options = byId('basket-options');
  const chosen = byId('basket-chosen');
  const output = byId('basket-candidates');
  const summary = byId('basket-status');
  const empty = byId('basket-empty');
  const error = byId('basket-error');
  const help = byId('basket-search-hint');
  const example = byId('basket-example');
  const clear = byId('basket-clear');
  let rules = null;
  let catalogue = [];
  let selected = [];

  const make = (tag, className, value) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = String(value);
    return element;
  };
  const number = value => Number(value).toLocaleString('en-GB');
  const pct = value => (Number(value) * 100).toFixed(1) + '%';

  function renderSearch() {
    options.replaceChildren();
    if (!rules) return;
    if (selected.length === 3) {
      help.textContent = 'Three products selected. Remove one to choose another.';
      return;
    }
    const term = search.value.trim();
    if (term.length < 2) {
      help.textContent = 'Type at least two characters of a product name or SKU.';
      return;
    }
    const matches = searchCatalogue(catalogue, term, selected);
    help.textContent = matches.length ? number(matches.length) + ' matching products shown.' :
      'No matching published antecedent product. Try another name or stock code.';
    for (const item of matches) {
      const li = make('li', 'basket-choice');
      const button = make('button', 'basket-choice-button', item.name + ' (' + item.sku + ')');
      button.type = 'button';
      button.setAttribute('aria-label', 'Add ' + item.name + ' (' + item.sku + ')');
      button.addEventListener('click', () => {
        if (selected.length === 3 || selected.includes(item.sku)) return;
        selected.push(item.sku);
        search.value = '';
        render();
        search.focus();
      });
      li.append(button);
      options.append(li);
    }
  }

  function renderSelected() {
    chosen.replaceChildren();
    const known = new Map(catalogue.map(item => [item.sku, item]));
    for (const sku of selected) {
      const li = make('li', 'basket-selected');
      const item = known.get(sku);
      li.append(make('span', '', (item ? item.name : sku) + ' (' + sku + ')'));
      const remove = make('button', 'basket-remove', 'Remove');
      remove.type = 'button';
      remove.setAttribute('aria-label', 'Remove ' + (item ? item.name : sku));
      remove.addEventListener('click', () => {
        selected = selected.filter(value => value !== sku);
        render();
        search.focus();
      });
      li.append(remove);
      chosen.append(li);
    }
    clear.disabled = selected.length === 0;
  }

  function renderCandidates() {
    output.replaceChildren();
    empty.hidden = true;
    if (!rules) return;
    if (!selected.length) {
      summary.textContent = 'No products selected.';
      empty.hidden = false;
      empty.textContent = 'Choose a product above or load the audited Pink Polkadot example.';
      return;
    }
    const matched = matchBasket(rules, selected);
    summary.textContent = number(selected.length) + (selected.length === 1 ? ' product selected. ' : ' products selected. ') +
      number(matched.total) + ' distinct candidate products in the curated rule set.';
    if (!matched.total) {
      empty.hidden = false;
      empty.textContent = 'No selected antecedent matches the 1,500 published rules. This does not mean the products were never bought together.';
      return;
    }
    for (const rule of matched.suggestions) {
      const li = make('li', 'basket-candidate');
      const heading = make('div', 'basket-candidate-head');
      heading.append(make('span', 'basket-candidate-index', rule.a.length + '-product antecedent'),
        make('strong', 'basket-candidate-name', rule.c.name + ' (' + rule.c.sku + ')'));
      const context = make('p', 'basket-candidate-context',
        'Triggered by: ' + rule.a.map(item => item.name + ' (' + item.sku + ')').join(' + '));
      const evidence = make('div', 'basket-candidate-evidence');
      evidence.append(make('span', '', number(rule.joint) + ' earlier joint baskets'),
        make('span', '', pct(rule.confidence) + ' training confidence'),
        make('span', '', Number(rule.lift).toFixed(2) + 'x training lift'));
      const later = rule.fires > 0 ?
        number(rule.hits) + ' / ' + number(rule.fires) + ' later antecedent baskets also contained this item' :
        'No later-period antecedent baskets observed';
      li.append(heading, context, evidence, make('p', 'basket-candidate-later', 'Later holdout: ' + later));
      output.append(li);
    }
  }

  function render() {
    if (!rules) return;
    renderSelected();
    renderSearch();
    renderCandidates();
  }

  function setData(payload) {
    if (!payload || payload.schema !== 'basketlens.rule-explorer.v1' ||
        !Array.isArray(payload.rules) || payload.rules.length !== 1500) {
      fail();
      return;
    }
    rules = payload.rules;
    catalogue = catalogueFromRules(rules);
    error.hidden = true;
    search.disabled = false;
    example.disabled = !catalogue.some(item => item.sku === '22386');
    render();
  }

  function fail() {
    rules = null;
    output.replaceChildren();
    options.replaceChildren();
    chosen.replaceChildren();
    error.hidden = false;
    empty.hidden = true;
    search.disabled = true;
    example.disabled = true;
    clear.disabled = true;
    summary.textContent = 'Basket matching unavailable until the published rules load.';
  }

  search.addEventListener('input', renderSearch);
  example.addEventListener('click', () => {
    if (!rules || !catalogue.some(item => item.sku === '22386')) return;
    selected = ['22386'];
    search.value = '';
    render();
  });
  clear.addEventListener('click', () => {
    selected = [];
    search.value = '';
    render();
    search.focus();
  });
  window.addEventListener('basketlens:dataset-ready', event => setData(event.detail));
  window.addEventListener('basketlens:dataset-error', fail);
  if (window.BasketLensPublicDataset) setData(window.BasketLensPublicDataset);
  else if (window.BasketLensPublicDatasetStatus === 'error') fail();
}
