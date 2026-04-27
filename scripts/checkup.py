"""
Repo health scanner. stdlib-only.
Outputs JSON to stdout for /nonna-checkup command consumption.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
import time

TODO_MARKERS = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
BAD_COMMIT_PATTERNS = re.compile(
    r"^(fix|wip|stuff|update|changes|test|asd|temp|\.|tmp|broken|blah|misc)$",
    re.IGNORECASE,
)
FAT_THRESHOLD = 500
OBESE_THRESHOLD = 1000
ORPHAN_LOG_PATTERNS = re.compile(
    r"\b(console\.log|print|fmt\.Println|dbg!|System\.out\.println|println!)\b"
)
TEST_FILE_PATTERNS = re.compile(
    r"(\.test\.|\.spec\.|_test\.|test_|/tests?/|/__tests__/|_spec\.)"
)
SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift",
    ".kt", ".sh",
}
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".cache",
}


def iter_source_files(root: Path):
    """Yield source files under root, skipping common ignore dirs."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SCAN_EXTENSIONS:
            yield path


def is_git_repo(root: Path) -> bool:
    """True if root contains a `.git` dir or is inside a git work tree."""
    if (root / ".git").exists():
        return True
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def scan_todos(root: Path) -> dict[str, Any]:
    """Find TODO/FIXME/HACK/XXX markers across source files."""
    findings = []  # (file, line_num, marker, mtime)
    for f in iter_source_files(root):
        try:
            mtime = f.stat().st_mtime
            for line_num, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                m = TODO_MARKERS.search(line)
                if m:
                    findings.append((f, line_num, m.group(1).upper(), mtime))
        except (PermissionError, OSError):
            continue

    # Sort by mtime ascending (oldest first)
    findings.sort(key=lambda x: x[3])

    oldest_3 = []
    now = time.time()
    for f, line_num, marker, mtime in findings[:3]:
        age_days = int((now - mtime) / 86400)
        oldest_3.append({
            "file": str(f.relative_to(root)),
            "line": line_num,
            "marker": marker,
            "age_days": age_days,
        })

    return {
        "count": len(findings),
        "oldest_3": oldest_3,
    }


def scan_fat_files(root: Path) -> list[dict[str, Any]]:
    """Files between FAT_THRESHOLD and OBESE_THRESHOLD lines."""
    results = []
    for f in iter_source_files(root):
        try:
            lines = sum(1 for _ in f.open(errors="ignore"))
            if FAT_THRESHOLD <= lines < OBESE_THRESHOLD:
                results.append({"file": str(f.relative_to(root)), "lines": lines})
        except (PermissionError, OSError):
            continue
    results.sort(key=lambda x: -x["lines"])
    return results[:5]


def scan_obese_files(root: Path) -> list[dict[str, Any]]:
    """Files exceeding OBESE_THRESHOLD lines (red flag)."""
    results = []
    for f in iter_source_files(root):
        try:
            lines = sum(1 for _ in f.open(errors="ignore"))
            if lines >= OBESE_THRESHOLD:
                results.append({"file": str(f.relative_to(root)), "lines": lines})
        except (PermissionError, OSError):
            continue
    results.sort(key=lambda x: -x["lines"])
    return results


def scan_orphan_logs(root: Path) -> int:
    """Count debug-print orphans in non-test source files."""
    count = 0
    for f in iter_source_files(root):
        path_str = str(f.relative_to(root)).replace(os.sep, "/")
        if TEST_FILE_PATTERNS.search(path_str):
            continue
        try:
            for line in f.read_text(errors="ignore").splitlines():
                if ORPHAN_LOG_PATTERNS.search(line):
                    count += 1
        except (PermissionError, OSError):
            continue
    return count


def scan_stale_deps(root: Path) -> dict[str, Any]:
    return {"count": 0, "with_cve": 0, "list": []}  # placeholder


def scan_zombie_branches(root: Path) -> int:
    """Count local branches with no commits in last 30 days, not merged to main."""
    if not is_git_repo(root):
        return 0
    try:
        result = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short) %(committerdate:unix)", "refs/heads/"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return 0
        now = time.time()
        thirty_days_ago = now - (30 * 86400)
        count = 0
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            branch, ts = parts
            try:
                if float(ts) < thirty_days_ago and branch not in ("main", "master"):
                    count += 1
            except ValueError:
                continue
        return count
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0


def scan_bad_commits(root: Path) -> int:
    """Count commits in last 30 days with bad messages."""
    if not is_git_repo(root):
        return 0
    try:
        result = subprocess.run(
            ["git", "log", "--since=30.days", "--pretty=format:%s"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return 0
        count = 0
        for msg in result.stdout.splitlines():
            msg = msg.strip()
            if BAD_COMMIT_PATTERNS.match(msg) or len(msg) < 10:
                count += 1
        return count
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 0


def scan_test_ratio(root: Path) -> float:
    return 0.0  # placeholder


def scan_repo(root: Path) -> dict[str, Any]:
    """Scan repo at root, return structured findings."""
    warnings = []
    if not is_git_repo(root):
        warnings.append("no git repo detected — skipped branches/commits checks")

    # detect package managers for stale deps
    has_npm = (root / "package.json").exists()
    has_pip = (root / "requirements.txt").exists() or (root / "pyproject.toml").exists()
    if not has_npm and not has_pip:
        warnings.append("no package.json or requirements.txt — skipped stale deps check")

    return {
        "todos": scan_todos(root),
        "fat_files": scan_fat_files(root),
        "obese_files": scan_obese_files(root),
        "orphan_logs": scan_orphan_logs(root),
        "stale_deps": scan_stale_deps(root),
        "zombie_branches": scan_zombie_branches(root),
        "bad_commits_30d": scan_bad_commits(root),
        "test_ratio": scan_test_ratio(root),
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Nonna repo health scanner")
    parser.add_argument("path", nargs="?", default=".", help="Repo path (default: cwd)")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}), file=sys.stderr)
        sys.exit(1)

    result = scan_repo(root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
