#!/usr/bin/env bash
# evals/run_subscription.sh
# Run all prompts.jsonl entries through `claude -p` (subscription auth)
# in two conditions: default and Nonna. Saves outputs for offline analysis.
#
# Usage:
#   bash evals/run_subscription.sh
#   CLAUDE_EVAL_MODEL=claude-opus-4-7 bash evals/run_subscription.sh
#
# After collection, analyse with:
#   python3 evals/sycophancy.py --from-dir evals/manual-results
#   python3 evals/pushback.py   --from-dir evals/manual-results
#   python3 evals/code_smell.py --from-dir evals/manual-results

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROMPTS_FILE="$REPO_ROOT/evals/benchmarks/prompts.jsonl"
RESULTS_DIR="$REPO_ROOT/evals/manual-results"
DEFAULT_DIR="$RESULTS_DIR/default"
NONNA_DIR="$RESULTS_DIR/nonna"
ERROR_LOG="$RESULTS_DIR/errors.log"
MODEL="${CLAUDE_EVAL_MODEL:-claude-sonnet-4-6}"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"

mkdir -p "$DEFAULT_DIR" "$NONNA_DIR"

# Verify claude binary is available
if ! command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
    # Try the known npm-global path as fallback
    if [ -x "/Users/$(whoami)/.npm-global/bin/claude" ]; then
        CLAUDE_BIN="/Users/$(whoami)/.npm-global/bin/claude"
    else
        echo "ERROR: claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code" >&2
        exit 1
    fi
fi

# Build Nonna system prompt
NONNA_SYSTEM="$(cat "$REPO_ROOT/SKILL.md")
$(cat "$REPO_ROOT/modes/full.md")"

TOTAL=$(grep -c '' "$PROMPTS_FILE")
COUNT=0

echo "Model: $MODEL" >&2
echo "Prompts: $PROMPTS_FILE ($TOTAL entries)" >&2
echo "Results: $RESULTS_DIR" >&2
echo "" >&2

while IFS= read -r line; do
    [ -z "$line" ] && continue
    COUNT=$((COUNT + 1))

    # Parse JSON line via python3 (preserves newlines and backticks in prompt)
    eval "$(printf '%s' "$line" | python3 -c "
import json, sys, shlex
o = json.loads(sys.stdin.read())
print('ID=' + shlex.quote(str(o['id'])))
print('PROMPT=' + shlex.quote(str(o['prompt'])))
")"

    DEFAULT_FILE="$DEFAULT_DIR/$ID.txt"
    NONNA_FILE="$NONNA_DIR/$ID.txt"

    if [ -f "$DEFAULT_FILE" ] && [ -f "$NONNA_FILE" ]; then
        echo "[$COUNT/$TOTAL] $ID — skip (cached)" >&2
        continue
    fi

    echo "[$COUNT/$TOTAL] $ID — running..." >&2

    # Run default (no system prompt).
    # Pass prompt via stdin (printf '%s' | claude -p) to avoid shell-escaping issues
    # with multiline content and backtick-heavy code blocks in smell prompts.
    if [ ! -f "$DEFAULT_FILE" ]; then
        if ! printf '%s' "$PROMPT" | "$CLAUDE_BIN" -p --model "$MODEL" > "$DEFAULT_FILE" 2>>"$ERROR_LOG"; then
            echo "ERROR (default) $ID at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ERROR_LOG"
            rm -f "$DEFAULT_FILE"   # don't leave partial file as a cached result
        fi
        sleep 1
    fi

    # Run Nonna (with appended system prompt)
    if [ ! -f "$NONNA_FILE" ]; then
        if ! printf '%s' "$PROMPT" | "$CLAUDE_BIN" -p --model "$MODEL" \
                --append-system-prompt "$NONNA_SYSTEM" > "$NONNA_FILE" 2>>"$ERROR_LOG"; then
            echo "ERROR (nonna) $ID at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ERROR_LOG"
            rm -f "$NONNA_FILE"
        fi
        sleep 1
    fi

done < "$PROMPTS_FILE"

# Summary
DEFAULT_COUNT=$(find "$DEFAULT_DIR" -name "*.txt" | wc -l | tr -d ' ')
NONNA_COUNT=$(find "$NONNA_DIR" -name "*.txt" | wc -l | tr -d ' ')

echo "" >&2
echo "Done. Captured: $DEFAULT_COUNT default, $NONNA_COUNT nonna responses." >&2
echo "Results in $RESULTS_DIR" >&2
echo "" >&2
echo "Now run:" >&2
echo "  python3 evals/sycophancy.py --from-dir $RESULTS_DIR" >&2
echo "  python3 evals/pushback.py   --from-dir $RESULTS_DIR" >&2
echo "  python3 evals/code_smell.py --from-dir $RESULTS_DIR" >&2
