#!/usr/bin/env python3
"""Collect read-only, heuristic code-quality signals.

The report is evidence for review, not an automatic refactoring or security
verdict. Project-native linters and scanners remain the authoritative checks
when they are configured and actually run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "__pycache__", ".next", ".turbo",
    "build", "coverage", "dist", "node_modules", "target", "vendor", "out",
    "generated", "gen", "htmlcov",
}

SOURCE_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".h", ".hpp", ".java", ".js",
    ".jsx", ".kt", ".php", ".py", ".rb", ".rs", ".sh", ".sql", ".swift",
    ".ts", ".tsx", ".vue",
}

TEST_PARTS = {"test", "tests", "spec", "specs", "__tests__"}
MAX_FINDINGS_PER_CATEGORY = 80


def iter_source_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in IGNORED_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.suffix.lower() in SOURCE_EXTENSIONS:
                yield path


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_test_path(path: Path, root: Path) -> bool:
    relative_path = relative(path, root).lower()
    parts = set(Path(relative_path).parts)
    stem = path.stem.lower()
    return bool(parts & TEST_PARTS) or stem.startswith(("test_", "spec_")) or stem.endswith(("_test", "_spec", ".test", ".spec"))


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def code_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "//", "/*", "*", "*/", "--", ";")):
            continue
        result.append(line)
    return result


def add_finding(findings: dict[str, list[dict[str, object]]], category: str, severity: str, path: Path, root: Path, line: int | None, rule: str, evidence: str) -> None:
    bucket = findings.setdefault(category, [])
    if len(bucket) >= MAX_FINDINGS_PER_CATEGORY:
        return
    bucket.append({
        "category": category,
        "severity": severity,
        "file": relative(path, root),
        "line": line or "-",
        "rule": rule,
        "evidence": evidence,
    })


def style_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    for path in files:
        for line_number, line in enumerate(read_lines(path), start=1):
            if line.rstrip("\n\r") != line.rstrip():
                add_finding(findings, "style", "low", path, root, line_number, "trailing-whitespace", "line has trailing whitespace")
            if line.startswith("\t") and path.suffix.lower() not in {".mk"}:
                add_finding(findings, "style", "low", path, root, line_number, "tab-indentation", "line starts with a tab")
            if len(line) > 120:
                add_finding(findings, "style", "low", path, root, line_number, "long-line", f"line length is {len(line)}")


def defect_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    for path in files:
        language = path.suffix.lower()
        lines = read_lines(path)
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if language == ".py":
                if stripped == "except:":
                    add_finding(findings, "defects", "medium", path, root, line_number, "bare-except", "bare except can hide unrelated failures")
                if re.search(r"def\s+\w+\([^)]*=\s*(?:\[|\{|set\()", line):
                    add_finding(findings, "defects", "medium", path, root, line_number, "mutable-default", "mutable default argument candidate")
                if re.search(r"(?:==|is)\s*None\s*==|==\s*None\b", line):
                    add_finding(findings, "defects", "low", path, root, line_number, "none-comparison", "ambiguous None comparison")
            if language in {".js", ".jsx", ".ts", ".tsx", ".vue"}:
                if re.search(r"(^|[^=])==([^=]|$)|(^|[^!])!=([^=]|$)", line):
                    add_finding(findings, "defects", "low", path, root, line_number, "loose-equality", "non-strict equality candidate")
                if re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", line):
                    add_finding(findings, "defects", "medium", path, root, line_number, "empty-catch", "empty catch block swallows failures")
def security_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    secret_pattern = re.compile(r"(?i)(?:api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*[\"'][^\"']{8,}[\"']")
    dangerous_patterns = (
        (re.compile(r"\beval\s*\("), "dangerous-eval", "dynamic evaluation call"),
        (re.compile(r"\bexec\s*\("), "dangerous-exec", "dynamic execution call"),
        (re.compile(r"\bos\.system\s*\("), "shell-execution", "shell execution call"),
        (re.compile(r"shell\s*=\s*True"), "shell-true", "subprocess shell=True candidate"),
        (re.compile(r"(?:execute|query)\s*\(\s*(?:f[\"']|[\"'][^\"']*[+%])"), "sql-concat", "SQL call may compose untrusted text"),
    )
    for path in files:
        for line_number, line in enumerate(read_lines(path), start=1):
            if secret_pattern.search(line):
                add_finding(findings, "security", "high", path, root, line_number, "hardcoded-secret", "credential-like literal in source")
            for pattern, rule, evidence in dangerous_patterns:
                if "re.compile(" in line or "dangerous_patterns" in line:
                    continue
                if pattern.search(line):
                    add_finding(findings, "security", "high" if rule in {"hardcoded-secret", "sql-concat"} else "medium", path, root, line_number, rule, evidence)


def complexity_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    function_start = re.compile(r"^\s*(?:(?:async\s+)?def\s+\w+|(?:export\s+)?(?:async\s+)?function\s+\w+|func\s+\w+|(?:public|private|protected)\s+.*\([^)]*\)\s*\{)")
    branch = re.compile(r"\b(?:if|elif|for|while|case|catch|except)\b|&&|\|\|")
    for path in files:
        lines = read_lines(path)
        for start, line in enumerate(lines):
            if not function_start.search(line):
                continue
            indent = len(line) - len(line.lstrip())
            end = len(lines)
            for candidate in range(start + 1, len(lines)):
                current = lines[candidate]
                if current.strip() and len(current) - len(current.lstrip()) <= indent and function_start.search(current) is None:
                    end = candidate
                    break
            body = lines[start:end]
            body_code = code_lines(body)
            branches = sum(len(branch.findall(item)) for item in body_code)
            if len(body_code) >= 80:
                add_finding(findings, "complexity", "medium", path, root, start + 1, "long-function", f"function-like block has {len(body_code)} code lines")
            if branches >= 10:
                add_finding(findings, "complexity", "medium", path, root, start + 1, "branch-heavy", f"function-like block has {branches} branch tokens")


def duplicate_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    windows: dict[tuple[str, ...], list[tuple[Path, int]]] = defaultdict(list)
    for path in files:
        lines = code_lines(read_lines(path))
        normalized = [re.sub(r"\s+", " ", re.sub(r"([\"']).*?\1", "<literal>", line.strip())) for line in lines]
        for index in range(0, max(0, len(normalized) - 5)):
            window = tuple(normalized[index:index + 6])
            if all(len(item) >= 8 for item in window):
                windows[window].append((path, index + 1))
    for window, occurrences in windows.items():
        unique_files = {path for path, _ in occurrences}
        if len(unique_files) < 2:
            continue
        first_path, first_line = occurrences[0]
        second_path, second_line = next(item for item in occurrences if item[0] != first_path)
        add_finding(findings, "duplication", "medium", first_path, root, first_line, "duplicate-block", f"six-line block also appears at {relative(second_path, root)}:{second_line}")


def coverage_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    production = [path for path in files if not is_test_path(path, root)]
    tests = [path for path in files if is_test_path(path, root)]
    names = {path.name.lower() for path in root.iterdir()}
    artifacts = sorted(name for name in {"coverage.xml", "lcov.info", ".coverage"} if name in names)
    config_names = {".coveragerc", "jest.config.js", "jest.config.ts", "vitest.config.ts", "pyproject.toml", "package.json"}
    configs = sorted(name for name in names if name in config_names)
    coverage_evidence = bool(artifacts)
    for config in configs:
        try:
            text = (root / config).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"coverage|pytest|jest|vitest|nyc|--cov", text, re.IGNORECASE):
            coverage_evidence = True
    if production and not tests:
        add_finding(findings, "test_coverage", "high", production[0], root, None, "no-tests-found", "production source exists but no test source was detected")
    elif production and not coverage_evidence:
        add_finding(findings, "test_coverage", "medium", production[0], root, None, "no-coverage-evidence", "tests may exist but no coverage configuration or artifact was detected")
    return {
        "production_files": len(production),
        "test_files": len(tests),
        "coverage_artifacts": artifacts,
        "coverage_configs": configs,
        "coverage_evidence": coverage_evidence,
    }


def smell_checks(root: Path, files: list[Path], findings: dict[str, list[dict[str, object]]]) -> None:
    for path in files:
        parts = {part.lower() for part in path.relative_to(root).parts}
        if parts & {"utils", "util", "helpers", "helper"}:
            add_finding(findings, "smells", "low", path, root, None, "shared-bucket", "generic utils/helpers location needs ownership review")
        for line_number, line in enumerate(read_lines(path), start=1):
            if re.search(r"(?:def|function|func)\s+\w+\s*\([^)]*,[^)]*,[^)]*,[^)]*,[^)]*,", line):
                add_finding(findings, "smells", "medium", path, root, line_number, "long-parameter-list", "function-like declaration has at least six parameters")
            if re.search(r"\?.*\?.*:", line):
                add_finding(findings, "smells", "low", path, root, line_number, "nested-ternary", "nested conditional expression reduces readability")
            if re.search(r"TODO|FIXME|HACK|XXX", line, re.IGNORECASE):
                add_finding(findings, "smells", "low", path, root, line_number, "unfinished-code", "unfinished or workaround marker")


def collect(root: Path, top: int) -> dict[str, object]:
    files = list(iter_source_files(root))
    findings: dict[str, list[dict[str, object]]] = {}
    style_checks(root, files, findings)
    defect_checks(root, files, findings)
    security_checks(root, files, findings)
    complexity_checks(root, files, findings)
    duplicate_checks(root, files, findings)
    coverage = coverage_checks(root, files, findings)
    smell_checks(root, files, findings)
    category_summary = {
        category: {"findings": len(items), "status": "warning" if items else "pass"}
        for category, items in sorted(findings.items())
    }
    for category in {"style", "defects", "security", "complexity", "duplication", "test_coverage", "smells"}:
        category_summary.setdefault(category, {"findings": 0, "status": "pass"})
    all_findings = [item for items in findings.values() for item in items]
    severity_rank = {"high": 0, "medium": 1, "low": 2}
    all_findings.sort(key=lambda item: (severity_rank[str(item["severity"])], str(item["file"]), str(item["line"])))
    return {
        "repository": str(root),
        "heuristic": True,
        "summary": {
            "source_files": len(files),
            "findings": len(all_findings),
            "by_category": category_summary,
        },
        "coverage": coverage,
        "findings": all_findings[:top],
        "omitted_findings": max(0, len(all_findings) - top),
        "disclaimer": "Heuristic candidates require project-native checks or human review before being treated as confirmed defects, vulnerabilities, or coverage gaps.",
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    coverage = report["coverage"]
    assert isinstance(summary, dict) and isinstance(coverage, dict)
    lines = [
        "# Code quality signals",
        "",
        f"- Repository: {report['repository']}",
        f"- Source files: {summary['source_files']}; findings: {summary['findings']}",
        "",
        "## Categories",
        "",
        "| Category | Status | Findings |",
        "|---|---|---:|",
    ]
    categories = summary["by_category"]
    assert isinstance(categories, dict)
    for category, item in categories.items():
        lines.append(f"| {category} | {item['status']} | {item['findings']} |")
    lines.extend([
        "",
        "## Test coverage evidence",
        "",
        f"- Production files: {coverage['production_files']}; test files: {coverage['test_files']}",
        f"- Coverage evidence: {'detected' if coverage['coverage_evidence'] else 'not detected'}",
        f"- Artifacts: {', '.join(coverage['coverage_artifacts']) or 'none'}",
        "",
        "## Findings",
        "",
        "| Severity | Category | File | Line | Rule | Evidence |",
        "|---|---|---|---:|---|---|",
    ])
    findings = report["findings"]
    assert isinstance(findings, list)
    for finding in findings:
        lines.append(f"| {finding['severity']} | {finding['category'] if 'category' in finding else '-'} | {finding['file']} | {finding['line']} | {finding['rule']} | {finding['evidence']} |")
    if report["omitted_findings"]:
        lines.append(f"- Omitted findings: {report['omitted_findings']}; rerun with a larger --top to inspect them.")
    lines.extend(["", f"- {report['disclaimer']}", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect read-only code-quality signals.")
    parser.add_argument("repository", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--top", type=int, default=100)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repository.expanduser().resolve()
    if not root.is_dir() or args.top < 1:
        print("error: repository must be a directory and --top must be positive", file=sys.stderr)
        return 2
    report = collect(root, args.top)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
