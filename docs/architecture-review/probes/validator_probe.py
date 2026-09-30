#!/usr/bin/env python3
"""Reproduce v4.1.0 audit observations without editing the skill or fixtures."""

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "define-product-and-roadmap"
sys.path.insert(0, str(SKILL / "scripts"))
from html_prd_validator import FINGERPRINT_ATTR, PRDParser, content_fingerprint, validate_html_prd


def stamp(text):
    digest = content_fingerprint(text)
    return FINGERPRINT_ATTR.sub(lambda m: m.group(1) + digest + m.group(2), text)


def record_for(text, choice="确认", note=""):
    parser = PRDParser()
    parser.feed(text)
    return {
        "document_id": parser.main["data-document-id"],
        "version": parser.main["data-version"],
        "review_id": parser.main["data-review-id"],
        "content_fingerprint": parser.main["data-content-fingerprint"],
        "decisions": [
            {"decision_id": key, "direction": sorted(card["directions"])[0],
             "choice": choice, "note": note, "source": "conversation"}
            for key, card in parser.decisions.items()
        ],
        "review_confirmation": {"content": True, "visual": True},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    template_path = SKILL / "assets" / "prd-template.html"
    template = template_path.read_text(encoding="utf-8")
    results = []
    with tempfile.TemporaryDirectory(prefix="prd-architecture-probe-") as directory:
        temporary = Path(directory)

        def check(case_id, text, expectation, record=None):
            path = temporary / (case_id + ".html")
            text = stamp(text)
            path.write_text(text, encoding="utf-8")
            record_path = None
            if record is not None:
                record_path = temporary / (case_id + ".json")
                record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            try:
                errors, warnings, parsed = validate_html_prd(path, record_path)
                result = {"id": case_id, "expectation": expectation,
                          "observed": "rejected" if errors else "accepted",
                          "errors": errors, "warnings": warnings,
                          "requirement_count": len(parsed.requirements) if parsed else None}
            except Exception as error:
                result = {"id": case_id, "expectation": expectation,
                          "observed": "exception", "exception_type": type(error).__name__,
                          "message": str(error)}
            results.append(result)
            return path

        check("baseline", template, "accepted")
        without_requirements = re.sub(r'<article class="requirement"[\s\S]*?</article>', "", template)
        check("no-requirements", without_requirements, "rejected: a full PRD needs requirements")
        empty = re.sub(r'(<article class="requirement"[^>]*>)[\s\S]*?(</article>)', r'\1\2', template)
        check("empty-requirement", empty, "rejected: requirement needs content and acceptance")
        invalid_metadata = template.replace("<dt>产品主形态</dt><dd>内容/产物生产</dd>",
                                            "<dt>产品主形态</dt><dd>not-a-product-shape</dd>")
        check("invalid-product-shape", invalid_metadata, "rejected: unknown closed-enum value")
        no_flow = re.sub(r' data-(?:flow-node|flow-edge|from|to|kind|node-kind|rule|rule-phrase)="[^"]*"', "", template)
        check("missing-flow-metadata", no_flow, "rejected: diagram still exists but has no flow contract")
        wrong_rule = template.replace("失败规则：信息不足时保留待补材料，用户补充后可再次提交。", "失败规则：此处没有声明那条规则。")
        check("rule-phrase-only-in-attribute", wrong_rule, "rejected: phrase is absent from target rule text")

        final = stamp(template.replace('data-status="审阅稿"', 'data-status="最终版"', 1)
                      .replace("<dt>文档状态</dt><dd>审阅稿</dd>", "<dt>文档状态</dt><dd>最终版</dd>"))
        ready_final = stamp(final.replace("否（关键决定待确认）", "是（已批准）"))
        check("final-still-needs-modification", ready_final,
              "rejected: requested changes have not been applied or re-reviewed",
              record_for(ready_final, "修改", "改为需要第二位审批人，正文尚未修改。"))
        check("final-readiness-is-no", final,
              "rejected: final status contradicts visible readiness=no", record_for(final))
        malformed_record = copy.deepcopy(record_for(template))
        malformed_record["decisions"][0]["choice"] = []
        check("malformed-choice-type", template, "structured rejection, not exception", malformed_record)
        nested = template.replace('<fieldset><legend>第一步', '<div class="layout"></div><fieldset><legend>第一步', 1)
        check("nested-decision-layout", nested, "accepted: empty layout wrapper must not end the decision card")

        fake_migration = '''<section><h2 id="migration">迁移核对</h2><table data-migration-table="v1"><caption>迁移</caption><tr><th>旧对象</th><th>旧位置/ID</th><th>新位置/ID</th><th>处理方式</th><th>语义变化</th><th>信息损失说明</th><th>关联验收</th></tr><tr><td>需求</td><td>invented-old-id</td><td>#req-p0-01</td><td>保留</td><td>无</td><td>无</td><td>#req-p0-01</td></tr></table></section>'''
        revision = template.replace('data-document-kind="new"', 'data-document-kind="revision"', 1)
        revision = revision.replace("</ol></nav>", '<li><a href="#migration">迁移核对</a></li></ol></nav>', 1)
        revision = revision.replace("</main>", fake_migration + "</main>", 1)
        check("invented-old-object", revision, "needs baseline comparison; current API has no baseline input")

        html = check("cross-format-base", template, "accepted")
        roadmap = temporary / "roadmap.md"
        roadmap.write_text("# Different Product\n\n- 文档版本：99.0.0\n\n## 需求落位映射\n\nR1: P0-01\nR2: P0-01\n", encoding="utf-8")
        command = [sys.executable, str(SKILL / "scripts" / "validate_product_docs.py"),
                   "--prd-html", str(html), "--roadmap", str(roadmap), "--format", "json"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
        observed = json.loads(result.stdout)
        observed["prd_html"] = "<temporary>/cross-format-base.html"
        observed["roadmap"] = "<temporary>/roadmap.md"
        results.append({"id": "incomplete-duplicate-roadmap", "expectation": "rejected: version mismatch, incomplete contract and duplicate allocation",
                        "returncode": result.returncode, "observed": observed})
        result = subprocess.run([sys.executable, str(SKILL / "scripts" / "validate_product_docs.py"),
                                 "--prd", str(ROOT / "evals/prd-output-spec/requested-markdown.md")],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        results.append({"id": "standalone-markdown-entry", "expectation": "independent validation entry exists",
                        "returncode": result.returncode, "stderr": result.stderr})

    report = {"baseline_tag": "v4.1.0", "baseline_commit": "29cf020572aa613d01daa617b31bc88b9f64b27f",
              "template_sha256": hashlib.sha256(template_path.read_bytes()).hexdigest(),
              "proof_boundary": "synthetic validator probes; not product execution or user approval",
              "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(result["id"], ":", result.get("observed", result.get("returncode")))


if __name__ == "__main__":
    main()
