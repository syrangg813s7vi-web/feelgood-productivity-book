#!/usr/bin/env python3
"""PR precheck for Feel-Good Productivity book repo.

Checks (for pull_request diffs):
- Only ONE new chapter file under book/ named BOOK_FULL_ChapterX_*.md
- Character count between 10,000 and 15,000
- Forbidden words scan: 字幕/视频/频道/这期/视频里/从.*提取
- Required structure keywords present

Exit code:
- 0: pass
- 1: fail

Usage:
  python3 scripts/precheck_pr.py --base <base-ref> --head <head-ref>

In GitHub Actions, base/head are typically:
  base = origin/${{ github.base_ref }}
  head = HEAD
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Tuple

FORBIDDEN_RE = re.compile(r"视频里|视频|字幕|这期|频道|从.*提取")

REQUIRED_SECTIONS = [
    "概念",
    "框架",
    "案例",
    "FAQ",
    "行动清单",
    "总结",
    "练习",
    "要点",
]

CHAPTER_PATH_RE = re.compile(r"^book/BOOK_FULL_Chapter(\d+)_.*\.md$")


def sh(cmd: List[str]) -> str:
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return out.decode("utf-8", errors="replace")


@dataclass
class Finding:
    ok: bool
    title: str
    detail: str = ""


def git_changed_files(base: str, head: str) -> List[Tuple[str, str]]:
    """Return list of (status, path) from git diff --name-status."""
    txt = sh(["git", "diff", "--name-status", f"{base}...{head}"])
    items: List[Tuple[str, str]] = []
    for line in txt.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0].strip()
        path = parts[-1].strip()
        items.append((status, path))
    return items


def read_file_from_head(path: str, head: str) -> str:
    return sh(["git", "show", f"{head}:{path}"])


def count_chars(s: str) -> int:
    # Use Python's character count (Unicode code points) as proxy for wc -m
    return len(s)


def find_forbidden_lines(text: str) -> List[Tuple[int, str]]:
    res = []
    for i, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN_RE.search(line):
            res.append((i, line.strip()))
    return res


def structure_missing(text: str) -> List[str]:
    missing = []
    low = text.lower()
    for key in REQUIRED_SECTIONS:
        if key.lower() not in low and key not in text:
            missing.append(key)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args()

    findings: List[Finding] = []

    changed = git_changed_files(args.base, args.head)

    added = [p for st, p in changed if st == "A"]
    chapter_added = [p for p in added if CHAPTER_PATH_RE.match(p)]

    # Rule: exactly one new chapter file
    if len(chapter_added) != 1:
        findings.append(Finding(False, "新增章节文件数量", f"期望 1 个，实际 {len(chapter_added)} 个：{chapter_added}"))
    else:
        findings.append(Finding(True, "新增章节文件数量", chapter_added[0]))

    # Rule: no other file changes beyond chapter file
    other_paths = [p for _, p in changed if p not in chapter_added]
    if other_paths:
        findings.append(Finding(False, "变更范围", f"检测到除章节文件外的变更：{other_paths}"))
    else:
        findings.append(Finding(True, "变更范围", "仅新增章节文件"))

    chapter_path = chapter_added[0] if len(chapter_added) == 1 else None

    if chapter_path:
        text = read_file_from_head(chapter_path, args.head)
        n_chars = count_chars(text)
        if 10_000 <= n_chars <= 15_000:
            findings.append(Finding(True, "字数", str(n_chars)))
        else:
            findings.append(Finding(False, "字数", f"{n_chars}（要求 10,000–15,000）"))

        bad = find_forbidden_lines(text)
        if not bad:
            findings.append(Finding(True, "禁词检测", "未命中"))
        else:
            detail = "\n".join([f"L{ln}: {snippet}" for ln, snippet in bad[:20]])
            findings.append(Finding(False, "禁词检测", f"命中 {len(bad)} 处（显示前20）\n{detail}"))

        missing = structure_missing(text)
        if not missing:
            findings.append(Finding(True, "结构关键词", "齐全"))
        else:
            findings.append(Finding(False, "结构关键词", f"缺少：{missing}"))

    # Print markdown report
    ok_all = all(f.ok for f in findings)
    status = "✅ PASS" if ok_all else "❌ FAIL"
    print(f"## PR 自动预审：{status}\n")
    for f in findings:
        icon = "✅" if f.ok else "❌"
        print(f"- {icon} **{f.title}**：{f.detail}")

    # Provide quick next step
    if not ok_all:
        print("\n---\n")
        print("**下一步建议**：按失败项修复后 push，新提交会自动重新触发预审。")

    return 0 if ok_all else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print("## PR 自动预审：❌ FAIL\n")
        print("- ❌ **脚本执行失败**")
        print("\n```\n" + e.output.decode("utf-8", errors="replace") + "\n```\n")
        raise
