#!/usr/bin/env python3
"""Collect read-only repository evidence for AI convention documents."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

MANIFEST_NAMES = {
    "Cargo.toml",
    "Gemfile",
    "go.mod",
    "package.json",
    "pnpm-workspace.yaml",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}

LOCKFILE_NAMES = {
    "Cargo.lock",
    "Gemfile.lock",
    "composer.lock",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}

BUILD_FILE_NAMES = {
    "Dockerfile",
    "Justfile",
    "Makefile",
    "Taskfile.yml",
    "compose.yaml",
    "docker-compose.yml",
}

DOC_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "README.md",
}

IMPACT_RULES = (
    (
        "dependencies-and-toolchain",
        lambda p: Path(p).name in (MANIFEST_NAMES | LOCKFILE_NAMES),
        ["AGENTS.md/CLAUDE.md", "quality gates", "architecture/operations when runtime changes"],
    ),
    (
        "api-and-contracts",
        lambda p: any(
            token in p.lower()
            for token in ("openapi", "swagger", "graphql", ".proto", "/api/", "/routes/", "/controllers/")
        ),
        ["API standard", "architecture", "requirements/design", "contract tests"],
    ),
    (
        "data-and-migrations",
        lambda p: any(
            token in p.lower()
            for token in ("migration", "schema", "/database/", "/db/", "prisma", "liquibase", "flyway")
        ),
        ["database standard", "architecture/design", "operations/rollback"],
    ),
    (
        "security-and-permissions",
        lambda p: any(
            token in p.lower()
            for token in ("auth", "permission", "policy", "security", "rbac", "acl", "secret")
        ),
        ["security standard", "architecture/design", "quality gates", "operations"],
    ),
    (
        "delivery-and-operations",
        lambda p: (
            p.startswith((".github/workflows/", ".gitlab/", "deploy/", "infra/", "k8s/", "terraform/"))
            or any(token in p.lower() for token in ("dockerfile", "compose.y", "helm", "deployment"))
        ),
        ["quality gates", "deployment/rollback runbooks", "AGENTS.md/CLAUDE.md target environments"],
    ),
    (
        "tests-and-quality",
        lambda p: (
            p.startswith(("test/", "tests/", ".github/workflows/", ".gitlab/"))
            or any(token in p.lower() for token in ("/test/", "/tests/", ".spec.", ".test.", "lint", "eslint"))
        ),
        ["quality gates", "testing standard", "AGENTS.md/CLAUDE.md commands"],
    ),
    (
        "domain-language",
        lambda p: any(token in p.lower() for token in ("/domain/", "domain-model", "glossary", "bounded-context")),
        ["domain glossary", "project map", "architecture", "requirements"],
    ),
    (
        "documentation",
        lambda p: p.lower().endswith((".md", ".mdx", ".rst")) or p.startswith("docs/"),
        ["document routes", "links", "status and review metadata"],
    ),
)


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)
        current_path = Path(current)
        for name in sorted(files):
            yield current_path / name


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def run_git(root: Path, args: list[str]) -> tuple[list[str], str | None]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [], result.stderr.strip() or "git command failed"
    return [line for line in result.stdout.splitlines() if line], None


def git_changes(root: Path, since: str | None) -> tuple[list[str], list[str]]:
    inside, error = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if error or inside != ["true"]:
        return [], ["Not a Git worktree; change-based backfill evidence is unavailable."]

    changes: set[str] = set()
    warnings: list[str] = []
    commands: list[list[str]] = [
        ["diff", "--name-only", "--diff-filter=ACDMRTUXB"],
        ["diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB"],
        ["ls-files", "--others", "--exclude-standard"],
    ]
    if since:
        commands.insert(0, ["diff", "--name-only", "--diff-filter=ACDMRTUXB", f"{since}...HEAD"])

    for command in commands:
        paths, command_error = run_git(root, command)
        if command_error:
            warnings.append(f"git {' '.join(command)}: {command_error}")
        else:
            changes.update(paths)
    return sorted(changes), warnings


def package_scripts(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    return {str(name): str(command) for name, command in scripts.items()}


def make_targets(path: Path) -> list[str]:
    targets: list[str] = []
    pattern = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*(?:\s+[A-Za-z0-9][A-Za-z0-9_.-]*)*):(?:\s|$)")
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return targets
    for line in lines:
        if line.startswith((" ", "\t", ".PHONY")):
            continue
        match = pattern.match(line)
        if match:
            targets.extend(match.group(1).split())
    return sorted(set(targets))


def just_targets(path: Path) -> list[str]:
    targets: list[str] = []
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)(?:\s+[^:=]+)?\s*:")
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return targets
    for line in lines:
        if line.startswith((" ", "\t", "#")):
            continue
        match = pattern.match(line)
        if match:
            targets.append(match.group(1))
    return sorted(set(targets))


def collect_commands(root: Path, files: list[Path]) -> dict[str, object]:
    commands: dict[str, object] = {}
    for path in files:
        relative = relpath(path, root)
        if path.name == "package.json":
            scripts = package_scripts(path)
            if scripts:
                commands[relative] = {"package_scripts": scripts}
        elif path.name == "Makefile":
            targets = make_targets(path)
            if targets:
                commands[relative] = {"make_targets": targets}
        elif path.name == "Justfile":
            targets = just_targets(path)
            if targets:
                commands[relative] = {"just_recipes": targets}
    return commands


def classify_changes(paths: list[str]) -> dict[str, dict[str, object]]:
    impacts: dict[str, dict[str, object]] = {}
    matched_paths: set[str] = set()
    for name, predicate, documents in IMPACT_RULES:
        evidence = sorted(path for path in paths if predicate(path))
        if evidence:
            impacts[name] = {"changed_paths": evidence, "review": documents}
            matched_paths.update(evidence)
    unclassified = sorted(set(paths) - matched_paths)
    if unclassified:
        impacts["implementation-review"] = {
            "changed_paths": unclassified,
            "review": ["Inspect behavior and callers before deciding whether any long-lived document changes."],
        }
    return impacts


def collect(root: Path, since: str | None) -> dict[str, object]:
    files = list(iter_files(root))
    relative_files = [relpath(path, root) for path in files]
    manifests = sorted(
        relative
        for path, relative in zip(files, relative_files)
        if path.name in MANIFEST_NAMES | LOCKFILE_NAMES | BUILD_FILE_NAMES
    )
    docs = sorted(
        relative
        for path, relative in zip(files, relative_files)
        if path.name in DOC_NAMES
        or (
            relative.startswith("docs/")
            and path.suffix.lower() in {".md", ".mdx", ".rst"}
        )
    )
    ci = sorted(
        relative
        for relative in relative_files
        if relative.startswith((".github/workflows/", ".gitlab/", ".circleci/"))
    )
    changes, warnings = git_changes(root, since)
    return {
        "repository": str(root),
        "comparison_base": since,
        "inventory": {
            "manifests_and_build_files": manifests,
            "ai_and_project_documents": docs,
            "ci_files": ci,
            "declared_commands": collect_commands(root, files),
        },
        "changes": changes,
        "document_impact_hints": classify_changes(changes),
        "warnings": warnings,
        "disclaimer": (
            "This report contains discovery evidence and heuristic impact hints. "
            "Confirm claims in the relevant code, configuration, tests, decisions, and target environment."
        ),
    }


def render_markdown(report: dict[str, object]) -> str:
    inventory = report["inventory"]
    assert isinstance(inventory, dict)
    lines = [
        "# Project evidence report",
        "",
        f"- Repository: `{report['repository']}`",
        f"- Comparison base: `{report['comparison_base'] or 'working tree only'}`",
        f"- Disclaimer: {report['disclaimer']}",
        "",
    ]
    for key, title in (
        ("manifests_and_build_files", "Manifests and build files"),
        ("ai_and_project_documents", "AI and project documents"),
        ("ci_files", "CI files"),
    ):
        lines.extend([f"## {title}", ""])
        values = inventory[key]
        assert isinstance(values, list)
        lines.extend([f"- `{value}`" for value in values] or ["- None discovered"])
        lines.append("")

    lines.extend(["## Declared commands", ""])
    declared = inventory["declared_commands"]
    assert isinstance(declared, dict)
    if declared:
        lines.append("```json")
        lines.append(json.dumps(declared, ensure_ascii=False, indent=2, sort_keys=True))
        lines.extend(["```", ""])
    else:
        lines.extend(["- None parsed from package.json, Makefile, or Justfile", ""])

    lines.extend(["## Changed paths", ""])
    changes = report["changes"]
    assert isinstance(changes, list)
    lines.extend([f"- `{path}`" for path in changes] or ["- None discovered"])
    lines.append("")

    lines.extend(["## Document impact hints", ""])
    impacts = report["document_impact_hints"]
    assert isinstance(impacts, dict)
    if not impacts:
        lines.extend(["- No change-based hints available", ""])
    for name, detail in impacts.items():
        assert isinstance(detail, dict)
        lines.append(f"### {name}")
        lines.append("")
        lines.append("Changed paths: " + ", ".join(f"`{path}`" for path in detail["changed_paths"]))
        lines.append("")
        lines.append("Review: " + "; ".join(detail["review"]))
        lines.append("")

    warnings = report["warnings"]
    assert isinstance(warnings, list)
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect read-only evidence and documentation-impact hints from a project repository."
    )
    parser.add_argument("repository", type=Path, help="Project repository to inspect")
    parser.add_argument("--since", help="Git ref used as the committed-change comparison base")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repository.expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository is not a directory: {root}", file=sys.stderr)
        return 2
    report = collect(root, args.since)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
