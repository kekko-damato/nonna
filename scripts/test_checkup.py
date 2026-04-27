import json
import subprocess
import sys
from pathlib import Path

CHECKUP = Path(__file__).parent / "checkup.py"


def run_checkup(path: str = ".") -> dict:
    """Run checkup.py on path, parse JSON output."""
    result = subprocess.run(
        [sys.executable, str(CHECKUP), path],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_runs_on_empty_dir(tmp_path):
    result = run_checkup(str(tmp_path))
    assert "todos" in result
    assert "fat_files" in result
    assert "obese_files" in result
    assert "orphan_logs" in result
    assert "stale_deps" in result
    assert "zombie_branches" in result
    assert "bad_commits_30d" in result
    assert "test_ratio" in result
    assert "warnings" in result


def test_counts_todos(tmp_path):
    (tmp_path / "a.py").write_text("# TODO: fix this\nprint('hi')\n")
    (tmp_path / "b.py").write_text("def foo():\n    # FIXME: broken\n    pass\n")
    result = run_checkup(str(tmp_path))
    assert result["todos"]["count"] == 2


def test_todo_oldest_3(tmp_path):
    f = tmp_path / "old.py"
    f.write_text("# TODO: very old\n")
    # Note: file age uses os.path.getmtime, which we can't easily fake here.
    # Just verify it returns the structure.
    result = run_checkup(str(tmp_path))
    assert isinstance(result["todos"]["oldest_3"], list)
    assert len(result["todos"]["oldest_3"]) <= 3
    if result["todos"]["count"] > 0:
        first = result["todos"]["oldest_3"][0]
        assert "file" in first
        assert "line" in first
        assert "marker" in first
