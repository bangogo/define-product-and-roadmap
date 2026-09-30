#!/bin/sh
# Reproduce the architecture-review observations. Read-only against the skill source.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
skill="$root/skills/define-product-and-roadmap"
python3="${PYTHON:-python3}"
node="${NODE:-node}"

"$python3" "$here/validator_probe.py" --output "$here/../evidence/validator-results.json"

if command -v playwright >/dev/null 2>&1; then
  play=playwright
else
  play="$root/node_modules/playwright"
fi
PLAYWRIGHT_MODULE="$play" \
BROWSER_EXECUTABLE="${BROWSER_EXECUTABLE:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}" \
  "$node" "$here/browser_probe.mjs" "$here/../evidence/browser"

# The mis-exported record must be rejected by the validator.
"$python3" "$skill/scripts/validate_product_docs.py" \
  --prd-html "$skill/assets/prd-template.html" \
  --decisions "$here/../evidence/browser/download-1440.json" \
  --format json || true
