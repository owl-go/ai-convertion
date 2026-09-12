#!/usr/bin/env python3
"""Collect read-only structural health signals for a project repository.

The script deliberately reports heuristics instead of pretending to infer
architecture. A skill invocation should combine this output with code, tests,
configuration, and change-history evidence before assigning a score.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    ".next",
    ".turbo",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "out",
    "generated",
    "gen",
}

SOURCE_EXTENSIONS = {
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".kt": "kotlin",
    ".php": "php",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".sh": "shell",
    ".sql": "sql",
    ".swift": "swift",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".vue": "vue",
}

SYMBOL_PATTERNS = {
    "python": re.compile(r"^\s*(?:async\s+def|def|class)\s+[A-Za-z_]\w*"),
    "javascript": re.compile(
        r"^\s*(?:(?:export\s+)?(?:async\s+)?function\s+\w+|"
        r"(?:export\s+)?class\s+\w+|"
        r"(?:export\s+)?(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\()"
    ),
    "typescript": re.compile(
        r"^\s*(?:(?:export\s+)?(?:async\s+)?function\s+\w+|"
        r"(?:export\s+)?class\s+\w+|"
        r"(?:export\s+)?(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\()"
    ),
    "go": re.compile(r"^\s*(?:func\s+\w+|type\s+\w+\s+(?:struct|interface))"),
    "rust": re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?(?:fn|struct|enum|trait)\s+\w+"),
    "java": re.compile(r"^\s*(?:(?:public|private|protected|abstract|final|static)\s+)*(?:class|interface|enum)\s+\w+"),
    "kotlin": re.compile(r"^\s*(?:(?:public|private|protected|internal)\s+)?(?:class|object|interface|fun)\s+\w+"),
    "csharp": re.compile(r"^\s*(?:(?:public|private|protected|internal|static|abstract|sealed)\s+)*(?:class|interface|struct|enum)\s+\w+"),
    "ruby": re.compile(r"^\s*(?:def|class|module)\s+[A-Za-z_]\w*[!?=]?"),
    "php": re.compile(r"^\s*(?:(?:public|private|protected|static|abstract|final)\s+)*(?:function|class|interface|trait)\s+\w+"),
    "swift": re.compile(r"^\s*(?:(?:public|private|internal|fileprivate|open|static)\s+)*(?:func|class|struct|enum|protocol)\s+\w+"),
}

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


def source_scope(path: Path, root: Path) -> str:
    relative_path = relative(path, root).lower()
    parts = set(Path(relative_path).parts)
    stem = path.stem.lower()
    if parts.intersection({"test", "tests", "spec", "specs", "__tests__"}):
        return "test"
    if stem.startswith(("test_", "spec_")) or stem.endswith(("_test", "_spec", ".test", ".spec")):
        return "test"
    return "production"


def strip_line_comments(lines: list[str], language: str) -> list[str]:
    """Remove blank and whole-line comments; keep inline code untouched."""
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if language in {"python", "ruby", "shell"} and stripped.startswith("#"):
            continue
        if language in {"sql"} and stripped.startswith("--"):
            continue
        if stripped.startswith(("//", "/*", "*", "*/")):
            continue
        if stripped.startswith(";"):
            continue
        result.append(line)
    return result


def read_file(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def symbols_for(lines: list[str], language: str) -> int:
    pattern = SYMBOL_PATTERNS.get(language)
    if pattern is None:
        return 0
    # Count file-level declarations only; nested methods are evidence for
    # complexity, not a separate top-level responsibility.
    return sum(1 for line in lines if not line[:1].isspace() and pattern.search(line))


def file_signal(path: Path, root: Path, warn_lines: int, critical_lines: int, warn_symbols: int, critical_symbols: int) -> dict[str, object]:
    language = SOURCE_EXTENSIONS[path.suffix.lower()]
    raw_lines = read_file(path)
    code_lines = strip_line_comments(raw_lines, language)
    symbols = symbols_for(code_lines, language)
    severity = "normal"
    reasons: list[str] = []
    if len(code_lines) >= critical_lines or symbols >= critical_symbols:
        severity = "critical"
    elif len(code_lines) >= warn_lines or symbols >= warn_symbols:
        severity = "warning"
    if len(code_lines) >= critical_lines:
        reasons.append(f"code_lines>={critical_lines}")
    elif len(code_lines) >= warn_lines:
        reasons.append(f"code_lines>={warn_lines}")
    if symbols >= critical_symbols:
        reasons.append(f"symbols>={critical_symbols}")
    elif symbols >= warn_symbols:
        reasons.append(f"symbols>={warn_symbols}")
    return {
        "path": relative(path, root),
        "scope": source_scope(path, root),
        "language": language,
        "total_lines": len(raw_lines),
        "code_lines": len(code_lines),
        "top_level_symbols": symbols,
        "severity": severity,
        "reasons": reasons,
    }


def collect(root: Path, args: argparse.Namespace) -> dict[str, object]:
    signals = [
        file_signal(
            path,
            root,
            args.warn_lines,
            args.critical_lines,
            args.warn_symbols,
            args.critical_symbols,
        )
        for path in iter_source_files(root)
    ]
    severity_rank = {"critical": 0, "warning": 1, "normal": 2}
    signals.sort(key=lambda item: (severity_rank[str(item["severity"])], -int(item["code_lines"])))
    language_counts = Counter(str(item["language"]) for item in signals)
    critical = [item for item in signals if item["severity"] == "critical"]
    warning = [item for item in signals if item["severity"] == "warning"]
    production = [item for item in signals if item["scope"] == "production"]
    tests = [item for item in signals if item["scope"] == "test"]
    return {
        "repository": str(root),
        "heuristic": True,
        "thresholds": {
            "warn_code_lines": args.warn_lines,
            "critical_code_lines": args.critical_lines,
            "warn_top_level_symbols": args.warn_symbols,
            "critical_top_level_symbols": args.critical_symbols,
        },
        "summary": {
            "source_files": len(signals),
            "production_files": len(production),
            "test_files": len(tests),
            "production_code_lines": sum(int(item["code_lines"]) for item in production),
            "test_code_lines": sum(int(item["code_lines"]) for item in tests),
            "languages": dict(sorted(language_counts.items())),
            "critical_files": len(critical),
            "warning_files": len(warning),
        },
        "file_signals": signals[: args.top],
        "omitted_hotspots": max(0, len(signals) - args.top),
        "disclaimer": (
            "Line and symbol counts are heuristic signals. They do not prove module boundaries, "
            "complexity, generated-code ownership, or architecture quality."
        ),
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    thresholds = report["thresholds"]
    assert isinstance(summary, dict)
    assert isinstance(thresholds, dict)
    lines = [
        "# Project health signals",
        "",
        f"- Repository: `{report['repository']}`",
        "- Mode: read-only heuristic evidence",
        (
            "- Thresholds: "
            f"warning {thresholds['warn_code_lines']} lines/{thresholds['warn_top_level_symbols']} symbols; "
            f"critical {thresholds['critical_code_lines']} lines/{thresholds['critical_top_level_symbols']} symbols"
        ),
        f"- Source files: `{summary['source_files']}`; production: `{summary['production_files']}` ({summary['production_code_lines']} code lines); tests: `{summary['test_files']}` ({summary['test_code_lines']} code lines)",
        f"- Hotspots: critical `{summary['critical_files']}`; warning `{summary['warning_files']}`",
        "",
        "## Languages",
        "",
    ]
    languages = summary["languages"]
    assert isinstance(languages, dict)
    lines.extend(f"- `{name}`: {count}" for name, count in languages.items())
    lines.extend(["", "## File hotspots", "", "| Severity | Scope | File | Language | Code lines | Total lines | Top-level symbols | Reasons |", "|---|---|---|---|---:|---:|---:|---|"])
    signals = report["file_signals"]
    assert isinstance(signals, list)
    for item in signals:
        assert isinstance(item, dict)
        reasons = ", ".join(str(reason) for reason in item["reasons"]) or "-"
        lines.append(
            f"| {item['severity']} | {item['scope']} | `{item['path']}` | {item['language']} | {item['code_lines']} | {item['total_lines']} | {item['top_level_symbols']} | {reasons} |"
        )
    if report["omitted_hotspots"]:
        lines.extend(["", f"- Omitted hotspots: `{report['omitted_hotspots']}`; rerun with a larger `--top` to inspect them."])
    lines.extend(["", "## Limits", "", f"- {report['disclaimer']}"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect read-only project structure health signals.")
    parser.add_argument("repository", type=Path, help="Project repository to inspect")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--top", type=int, default=10, help="Number of file hotspots to print")
    parser.add_argument("--warn-lines", type=int, default=400)
    parser.add_argument("--critical-lines", type=int, default=800)
    parser.add_argument("--warn-symbols", type=int, default=20)
    parser.add_argument("--critical-symbols", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repository.expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository is not a directory: {root}", file=sys.stderr)
        return 2
    if (
        args.top < 1
        or args.warn_lines < 1
        or args.critical_lines < args.warn_lines
        or args.warn_symbols < 1
        or args.critical_symbols < args.warn_symbols
    ):
        print("error: invalid size thresholds or --top", file=sys.stderr)
        return 2
    report = collect(root, args)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
