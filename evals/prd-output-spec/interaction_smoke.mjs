import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../../skills/define-product-and-roadmap/assets/prd-template.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'template inline script exists');

async function run(cards) {
  const events = {};
  const blobs = [];
  const main = { dataset: {documentId:'example-prd', version:'1.0.0-draft.1', reviewId:'review-001', contentFingerprint:'sha256:test'} };
  const content = { checked: false };
  const visual = { checked: false };
  const summary = { textContent:'' };
  const status = { textContent:'' };
  const buttons = {
    'show-selections': { addEventListener: (_, fn) => {events.show = fn;} },
    'export-decisions': { addEventListener: (_, fn) => {events.export = fn;} },
  };
  const elements = {'review-content':content, 'review-visual':visual, 'selection-summary':summary, 'export-status':status, ...buttons};
  const document = {
    querySelector: selector => selector === 'main' ? main : null,
    querySelectorAll: selector => selector === '[data-decision-id]' ? cards : [],
    getElementById: id => elements[id],
    createElement: tag => ({ click() {assert.equal(tag, 'a'); this.clicked = true; blobs.at(-1).clicked = true;} }),
  };
  vm.runInNewContext(script, {document, Blob, URL:{createObjectURL(blob){blobs.push({blob, clicked:false}); return 'blob:local-test';}, revokeObjectURL(){}}, setTimeout(){} });
  events.show();
  assert.match(summary.textContent, /内容确认：否；视觉确认：否/);
  events.export();
  return {events, elements, blobs, status, content, visual};
}

function card(id='D-01') {
  const state = {choice:'', note:''};
  return {dataset:{decisionId:id}, state, querySelector(selector) {
    if (selector.startsWith('input')) return state.choice ? {value:state.choice} : null;
    if (selector === 'textarea') return {value:state.note};
    return null;
  }};
}

const c = card();
const one = await run([c]);
assert.equal(one.blobs.length, 0, 'initial blank choice blocks export');
c.state.choice = '修改';
one.events.export();
assert.equal(one.blobs.length, 0, 'modification without note blocks export');
c.state.note = '保留人工复核';
one.events.export();
assert.equal(one.blobs.length, 1, 'valid modification exports');
const exported = JSON.parse(await one.blobs[0].blob.text());
assert.equal(exported.decisions[0].decision_id, 'D-01');
assert.equal(exported.decisions[0].source, 'web-export');
assert.equal(exported.decisions[0].note, '保留人工复核');
assert.equal(exported.review_confirmation.content, false);
assert.match(one.status.textContent, /保持审阅稿/);

c.state.choice = '确认'; c.state.note = '';
one.content.checked = true; one.visual.checked = true;
one.events.export();
const completed = JSON.parse(await one.blobs.at(-1).blob.text());
assert.deepEqual(completed.review_confirmation, {content:true, visual:true});
assert.match(one.status.textContent, /核对当前源稿指纹/);

const zero = await run([]);
assert.equal(zero.blobs.length, 1, 'no pending card still has version-level export');
assert.equal(JSON.parse(await zero.blobs[0].blob.text()).decisions.length, 0);
console.log('interaction smoke: blank, modify, export, version confirmation, no-pending passed');
