"""
Code smell capture eval.
Compares default Claude vs Nonna on 10 synthetic PRs with embedded smells.
Heuristic: response is "caught" if it mentions key smells from expected_behavior.
Reports detection multiplier.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 evals/code_smell.py

Cost note: ~20 API calls (10 prompts × 2 conditions). Roughly $1-2 per run on Opus.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from anthropic import Anthropic


# Common smell keywords. If response mentions these, the smell is "caught".
# Extracted from common terms in expected_behavior fields.
SMELL_KEYWORDS = {
    # Generic markers
    "todo", "fixme", "validation", "validate", "missing test", "no test",
    "race condition", "race", "console.log", "secret", "credential", "api key",
    "leaked", "hardcoded",
    # Pattern names
    "fat function", "long function", "magic number", "magic string",
    "premature abstraction", "duplication", "dry violation", "silent catch",
    "swallowed exception",
    # Italian
    "validazione", "manca un test", "console.log", "duplicato",
}


def load_prompts(path: Path, category: str = "smell") -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip() and json.loads(line)["category"] == category
    ]


def keywords_from_expected(expected: str) -> set[str]:
    """Extract candidate keywords from expected_behavior field."""
    text = expected.lower()
    found = {kw for kw in SMELL_KEYWORDS if kw in text}
    return found


def smells_detected(response: str, keywords: set[str]) -> int:
    """Count how many of the expected keywords are mentioned in response."""
    text = response.lower()
    return sum(1 for kw in keywords if kw in text)


def get_api_key() -> str:
    if "ANTHROPIC_API_KEY" in os.environ:
        return os.environ["ANTHROPIC_API_KEY"]
    key_file = Path.home() / ".anthropic" / "api_key"
    if key_file.exists():
        return key_file.read_text().strip()
    raise RuntimeError(
        "No Anthropic API key found. Set ANTHROPIC_API_KEY env var or "
        "create ~/.anthropic/api_key with your key."
    )


def run_prompt(client: Anthropic, prompt: str, system: str | None) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        temperature=0,
        system=system or "",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main() -> None:
    client = Anthropic(api_key=get_api_key())
    repo_root = Path(__file__).parent.parent
    prompts_path = repo_root / "evals" / "benchmarks" / "prompts.jsonl"
    skill_path = repo_root / "SKILL.md"
    mode_path = repo_root / "modes" / "full.md"

    prompts = load_prompts(prompts_path)
    nonna_system = skill_path.read_text() + "\n\n" + mode_path.read_text()

    total_keywords = 0
    default_caught = 0
    nonna_caught = 0
    total = len(prompts)

    print(f"Running {total} code smell prompts (default + nonna)...", file=sys.stderr)

    for i, p in enumerate(prompts, 1):
        keywords = keywords_from_expected(p["expected_behavior"])
        if not keywords:
            print(f"  [{i}/{total}] {p['id']}: SKIP (no extractable keywords)", file=sys.stderr)
            continue
        try:
            default_resp = run_prompt(client, p["prompt"], system=None)
            nonna_resp = run_prompt(client, p["prompt"], system=nonna_system)
        except Exception as e:
            print(f"  [{i}/{total}] {p['id']}: ERROR {e}", file=sys.stderr)
            continue

        total_keywords += len(keywords)
        d_caught = smells_detected(default_resp, keywords)
        n_caught = smells_detected(nonna_resp, keywords)
        default_caught += d_caught
        nonna_caught += n_caught

        print(f"  [{i}/{total}] {p['id']}: default={d_caught}/{len(keywords)} nonna={n_caught}/{len(keywords)}", file=sys.stderr)

    multiplier = nonna_caught / max(default_caught, 1)

    result = {
        "eval": "code_smell",
        "total_prompts": total,
        "total_keywords_expected": total_keywords,
        "default_caught": default_caught,
        "nonna_caught": nonna_caught,
        "detection_multiplier": round(multiplier, 2),
    }

    print(f"", file=sys.stderr)
    print(f"Default Claude: caught {default_caught}/{total_keywords} expected smells", file=sys.stderr)
    print(f"Nonna skill:    caught {nonna_caught}/{total_keywords} expected smells", file=sys.stderr)
    print(f"Detection:      {multiplier:.2f}x", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
