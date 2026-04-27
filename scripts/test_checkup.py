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


def test_detects_fat_file(tmp_path):
    big = tmp_path / "big.py"
    big.write_text("x = 1\n" * 600)
    result = run_checkup(str(tmp_path))
    assert any(f["file"] == "big.py" for f in result["fat_files"])
    fat_entry = next(f for f in result["fat_files"] if f["file"] == "big.py")
    assert fat_entry["lines"] == 600


def test_detects_obese_file(tmp_path):
    huge = tmp_path / "huge.py"
    huge.write_text("x = 1\n" * 1200)
    result = run_checkup(str(tmp_path))
    assert any(f["file"] == "huge.py" for f in result["obese_files"])


def test_normal_file_not_fat(tmp_path):
    normal = tmp_path / "normal.py"
    normal.write_text("x = 1\n" * 100)
    result = run_checkup(str(tmp_path))
    assert not any(f["file"] == "normal.py" for f in result["fat_files"])


def test_counts_orphan_logs(tmp_path):
    src = tmp_path / "code.js"
    src.write_text("function f() {\n  console.log('debug')\n  return 42\n}\n")
    result = run_checkup(str(tmp_path))
    assert result["orphan_logs"] == 1


def test_skips_logs_in_test_files(tmp_path):
    test = tmp_path / "thing.test.js"
    test.write_text("console.log('test debug')\n")
    result = run_checkup(str(tmp_path))
    assert result["orphan_logs"] == 0


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)


def test_no_git_warns_gracefully(tmp_path):
    result = run_checkup(str(tmp_path))
    assert result["zombie_branches"] == 0
    assert result["bad_commits_30d"] == 0
    assert any("git" in w.lower() for w in result["warnings"])


def test_counts_bad_commits(tmp_path):
    init_git_repo(tmp_path)
    (tmp_path / "f.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "fix"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "f.py").write_text("x = 2\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "wip"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "f.py").write_text("x = 3\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "feat: add proper feature"], cwd=tmp_path, check=True, capture_output=True)
    result = run_checkup(str(tmp_path))
    assert result["bad_commits_30d"] == 2
