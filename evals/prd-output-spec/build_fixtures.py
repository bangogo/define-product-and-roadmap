#!/usr/bin/env python3
"""Build synthetic HTML PRD revisions used for output-spec regression review."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills' / 'define-product-and-roadmap'
OUT = Path(__file__).resolve().parent
TEMPLATE = (SKILL / 'assets' / 'prd-template.html').read_text(encoding='utf-8')


def build(revision: int) -> None:
    text = TEMPLATE
    text = text.replace('示例产品需求文档', '团队工单处理产品需求文档')
    text = text.replace('示例内容流程', '工单处理流程')
    text = text.replace('example-prd', 'ticket-workflow')
    text = text.replace('1.0.0-draft.1', f'1.0.0-draft.{revision}')
    text = text.replace('审阅稿 ·', '审阅稿 ·')
    text = text.replace('2026-09-29', '2026-09-29')
    text = text.replace('<dt>产品主形态</dt><dd>内容/产物生产</dd>', '<dt>产品主形态</dt><dd>内部流程工具</dd>')
    text = text.replace('<dt>风险修饰项</dt><dd>AI</dd>', '<dt>风险修饰项</dt><dd>无</dd>')
    text = text.replace('<dt>当前证据阶段</dt><dd>仅有文档</dd>', '<dt>当前证据阶段</dt><dd>有限真实使用（用户陈述，未独立验证）</dd>')
    text = text.replace('<dt>当前交付目的</dt><dd>决策演示</dd>', '<dt>当前交付目的</dt><dd>流程改进评审</dd>')
    text = text.replace('<dt>适用场景</dt><dd>A（0→1 新产品）</dd>', '<dt>适用场景</dt><dd>B（存量迭代）</dd>')
    text = text.replace('<dt>适用产品合同</dt><dd>内容/产物生产、AI</dd>', '<dt>适用产品合同</dt><dd>内部流程工具</dd>')
    text = text.replace('示例用户提交主题材料，得到可审阅的内容草稿；此处换成项目真实目标、角色与边界。',
                        '处理人员提交工单处理结果，负责人核对后结案。此文件为合成回归样本，当前使用证据仅由本用例输入设定。')
    text = text.replace('当前仅有文档，真实使用效果尚未验证。此处记录来源、日期和缺口。',
                        '用例输入称团队已使用人工工单登记表，未提供系统调用日志；系统自动流转仍未验证。')
    text = text.replace('用户提交材料，系统生成可审阅草稿，用户确认后进入下一步。',
                        '处理人员提交工单，系统展示待核对结果，负责人确认后结案；证据不足时返回补充。')
    text = text.replace('文字路径：提交材料 → 获得草稿 → 用户确认；信息不足时先进入“保留待补材料”，用户补充后再提交。',
                        '文字路径：提交工单 → 处理并记录结果 → 负责人确认结案；信息不足时先保留待补材料，用户补充后再提交。')
    text = text.replace('用户提交材料', '提交工单')
    text = text.replace('生成审阅草稿', '处理工单')
    text = text.replace('用户确认结果', '负责人确认')
    text = text.replace('提交材料 → 获得草稿 → 用户确认；失败时保留原材料并说明可修改的内容。',
                        '提交工单 → 处理并记录结果 → 负责人确认结案；证据缺失时返回处理人员补充。')
    text = text.replace('提交材料并获得草稿', '处理工单并申请结案')
    text = text.replace('用户提供主题和来源；系统生成带来源提示的草稿。若来源不足，展示缺口并允许补充后重试。',
                        '处理人员登记处理结果；工单关闭前需负责人确认。若结果缺失，保留待处理状态并允许补充。')
    text = text.replace('用户能看到草稿、来源和缺口，修改输入后可再次生成。',
                        '处理人员能看到处理结果、当前责任人和缺口；负责人确认后状态变为已结案。')
    text = text.replace('<caption>结果与证据</caption><thead><tr><th scope="col">结果</th><th scope="col">当前状态</th><th scope="col">证据</th></tr></thead><tbody><tr><td>可审阅草稿</td><td>尚未验证</td><td>待真实样本试用</td></tr>',
                        '<caption>工单处理状态</caption><thead><tr><th scope="col">对象</th><th scope="col">当前状态</th><th scope="col">证据</th></tr></thead><tbody><tr><td>人工工单登记</td><td>尚未验证</td><td>合成用户陈述；未做宿主调用</td></tr>')
    text = text.replace('确认草稿的责任边界', '决定是否允许自动结案')
    text = text.replace('背景：草稿可预览，但是否直接用于后续步骤仍待决定。当前证据：只有方案，尚无真实用户效果。拟落位：需求规则与验收。',
                        '背景：人工登记表据称需负责人确认。当前证据：合成用户陈述，系统自动流转未验证。拟落位：需求规则与验收。')
    text = text.replace('value="user-review">方向 A：用户确认后放行（建议）', 'value="manual-close">方向 A：保持负责人确认（建议）')
    text = text.replace('value="auto-release">方向 B：自动放行', 'value="auto-close">方向 B：自动结案')
    if revision >= 2:
        text = text.replace('data-document-kind="new"', 'data-document-kind="revision"')
        text = text.replace('工单关闭前需负责人确认。', '工单关闭前需附处理证据并由负责人确认。')
        text = text.replace('处理人员能看到处理结果、当前责任人和缺口；', '处理人员能看到处理结果、处理证据、当前责任人和缺口；')
        text = text.replace('<th scope="col">证据</th></tr></thead><tbody><tr><td>人工工单登记</td><td>尚未验证</td><td>合成用户陈述；未做宿主调用</td>',
                            '<th scope="col">证据</th><th scope="col">处理证据</th></tr></thead><tbody><tr><td>人工工单登记</td><td>尚未验证</td><td>合成用户陈述；未做宿主调用</td><td>结案前补齐</td>')
        migration = '''<section><h2 id="migration">迁移核对表</h2><div class="table-scroll"><table data-migration-table="v1"><caption>draft.1 到 draft.2 迁移核对</caption><thead><tr><th>旧对象</th><th>旧位置/ID</th><th>新位置/ID</th><th>处理方式</th><th>语义变化</th><th>信息损失说明</th><th>关联验收</th></tr></thead><tbody><tr><td>需求</td><td>P0-01@draft.1</td><td><a href="#req-p0-01">#req-p0-01</a></td><td>改写</td><td>新增处理证据</td><td>无</td><td><a href="#req-p0-01">#req-p0-01</a></td></tr></tbody></table></div></section>'''
        text = text.replace('  <section><h2 id="risks">风险与待确认</h2>', migration + '\n  <section><h2 id="risks">风险与待确认</h2>')
        text = text.replace('<li><a href="#risks">风险与待确认</a></li>', '<li><a href="#risks">风险与待确认</a></li><li><a href="#migration">迁移核对表</a></li>')
    if revision >= 3:
        text = text.replace('工单关闭前需附处理证据并由负责人确认。', '工单关闭前需附处理证据并由当班负责人确认。')
        text = text.replace('负责人确认结案', '当班负责人确认结案')
        text = text.replace('负责人确认</text>', '当班负责人确认</text>')
        text = text.replace('负责人确认后状态变为已结案。', '当班负责人确认后状态变为已结案。')
        text = text.replace('<th scope="col">处理证据</th></tr></thead><tbody><tr><td>人工工单登记</td><td>尚未验证</td><td>合成用户陈述；未做宿主调用</td><td>结案前补齐</td>',
                            '<th scope="col">处理证据</th><th scope="col">确认责任</th></tr></thead><tbody><tr><td>人工工单登记</td><td>尚未验证</td><td>合成用户陈述；未做宿主调用</td><td>结案前补齐</td><td>当班负责人</td>')
        text = text.replace('<caption>draft.1 到 draft.2 迁移核对</caption>', f'<caption>draft.1 到 draft.{revision} 迁移核对</caption>')
        text = text.replace('<td>新增处理证据</td>', '<td>新增处理证据并改由当班负责人确认</td>')
    text = text.replace('review-001', f'review-{revision:03d}')
    path = OUT / f'existing-prd-draft.{revision}.html'
    path.write_text(text, encoding='utf-8')
    subprocess.run([sys.executable, str(SKILL / 'scripts' / 'stamp_html_prd.py'), str(path)], check=True, capture_output=True)


if __name__ == '__main__':
    for i in (1, 2, 3):
        build(i)
