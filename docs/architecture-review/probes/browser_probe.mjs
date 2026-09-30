// Read-only browser probe of the shipped template, not a replacement implementation.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = fileURLToPath(new URL('../../../', import.meta.url));
const templatePath = path.join(root, 'skills/define-product-and-roadmap/assets/prd-template.html');
const output = process.argv[2];
assert.ok(output, 'output directory argument is required');
await mkdir(output, { recursive: true });
const template = await readFile(templatePath, 'utf8');
const browser = await chromium.launch({ headless: true,
  ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
const results = [];
try {
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    await page.route('**/*', route => route.abort());
    await page.setContent(template);
    await page.locator('input[name="D-01-direction"][value="user-review"]').check();
    await page.locator('input[name="D-01"][value="确认"]').check();
    await page.locator('#review-content').check();
    await page.locator('#review-visual').check();
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#export-decisions').click();
    const download = await downloadPromise;
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const record = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    const screenshot = `template-${viewport.width}.png`;
    await page.locator('.decision').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(output, screenshot) });
    const data = { viewport, chosenDirection: 'user-review', chosenChoice: '确认',
      downloadedDirection: record.decisions[0].direction, downloadedChoice: record.decisions[0].choice,
      matchesUserChoice: record.decisions[0].choice === '确认', screenshot,
      proof_boundary: 'Synthetic browser actions, never user approval' };
    results.push(data);
    await writeFile(path.join(output, `download-${viewport.width}.json`), JSON.stringify(record, null, 2) + '\n');
    await page.close();
  }
} finally {
  await browser.close();
}
await writeFile(path.join(output, 'browser-results.json'), JSON.stringify({
  template_sha256: createHash('sha256').update(template).digest('hex'), results,
}, null, 2) + '\n');
console.log(JSON.stringify(results, null, 2));
