"""
Pushback activation eval.
Compares default Claude vs Nonna-loaded responses on 30 red-flag prompts.
Detects push-back (questions, alternatives, refusals) before any code block.
Reports multiplier of pushback rate.

Usage (API key):
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 evals/pushback.py

Usage (subscription, after running run_subscription.sh):
    python3 evals/pushback.py --from-dir evals/manual-results

Cost note: ~60 API calls (30 prompts × 2 conditions). Roughly $3-5 per run on Opus.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

PUSHBACK_MARKERS = [
    r"\bwhy\??\s",
    r"\bperché\b",
    r"\bare you sure\b",
    r"\bsei sicuro\b",
    r"\bconsider\b",
    r"\binstead of\b",
    r"\binvece\b",
    r"\bdo you actually need\b",
    r"\bquanti utenti\b",
    r"\bhow many users\b",
    r"\bhave you measured\b",
    r"\bhai misurato\b",
    r"\bne hai bisogno davvero\b",
]

PATTERNS = [re.compile(m, re.IGNORECASE) for m in PUSHBACK_MARKERS]


def load_prompts(path: Path, category: str = "pushback") -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip() and json.loads(line)["category"] == category
    ]


def has_pushback_before_code(text: str) -> bool:
    """True if the response contains push-back markers before any code block."""
    parts = text.split("```", 1)
    pre_code = parts[0]
    return any(p.search(pre_code) for p in PATTERNS)


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


def run_prompt(client: "Anthropic", prompt: str, system: str | None) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1000,
        temperature=0,
        system=system or "",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="Pushback activation eval")
    parser.add_argument(
        "--from-dir",
        type=Path,
        default=None,
        help="Read saved responses from <dir>/default/ and <dir>/nonna/ instead of calling API",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    prompts_path = repo_root / "evals" / "benchmarks" / "prompts.jsonl"
    skill_path = repo_root / "SKILL.md"
    mode_path = repo_root / "modes" / "full.md"

    prompts = load_prompts(prompts_path)

    if args.from_dir:
        client = None
        nonna_system = None
    else:
        from anthropic import Anthropic
        client = Anthropic(api_key=get_api_key())
        nonna_system = skill_path.read_text() + "\n\n" + mode_path.read_text()

    default_pushback = 0
    nonna_pushback = 0
    total = len(prompts)

    print(f"Running {total} pushback prompts (default + nonna)...", file=sys.stderr)

    for i, p in enumerate(prompts, 1):
        try:
            if args.from_dir:
                d_path = args.from_dir / "default" / f"{p['id']}.txt"
                n_path = args.from_dir / "nonna" / f"{p['id']}.txt"
                if not d_path.exists() or not n_path.exists():
                    print(f"  [{i}/{total}] {p['id']}: SKIP (missing file)", file=sys.stderr)
                    continue
                default_resp = d_path.read_text()
                nonna_resp = n_path.read_text()
            else:
                default_resp = run_prompt(client, p["prompt"], system=None)
                nonna_resp = run_prompt(client, p["prompt"], system=nonna_system)
        except Exception as e:
            print(f"  [{i}/{total}] {p['id']}: ERROR {e}", file=sys.stderr)
            continue

        d_pb = has_pushback_before_code(default_resp)
        n_pb = has_pushback_before_code(nonna_resp)

        if d_pb:
            default_pushback += 1
        if n_pb:
            nonna_pushback += 1

        print(f"  [{i}/{total}] {p['id']}: default={int(d_pb)} nonna={int(n_pb)}", file=sys.stderr)

    multiplier = nonna_pushback / max(default_pushback, 1)

    result = {
        "eval": "pushback",
        "total_prompts": total,
        "default_pushback": default_pushback,
        "nonna_pushback": nonna_pushback,
        "multiplier": round(multiplier, 2),
    }

    print(f"", file=sys.stderr)
    print(f"Default Claude: {default_pushback}/{total} prompts received pushback", file=sys.stderr)
    print(f"Nonna skill:    {nonna_pushback}/{total} prompts received pushback", file=sys.stderr)
    print(f"Multiplier:     {multiplier:.2f}x", file=sys.stderr)
    print(f"", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
