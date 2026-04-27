#!/usr/bin/env bash
# nonna/hooks/pre-commit-check.sh
# PreToolUse hook on Bash: intercepts `git commit -m "..."` with bad messages.
# Reads tool input as JSON from stdin, emits decision JSON to stdout.

set -e

# Read JSON input
INPUT="$(cat)"

# Extract command (assume Bash tool input shape: {tool_input: {command: "..."}})
# Use jq if available; fallback to grep
if command -v jq &>/dev/null; then
    COMMAND="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"
else
    # crude fallback: grep the command field
    COMMAND="$(echo "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"//; s/"$//')"
fi

# Only act on git commit -m
if [[ ! "$COMMAND" =~ git[[:space:]]+commit ]]; then
    echo '{}'
    exit 0
fi

# Extract message: -m "..." or -m '...'
MSG="$(echo "$COMMAND" | sed -n 's/.*-m[[:space:]]*"\([^"]*\)".*/\1/p; s/.*-m[[:space:]]*'\''\([^'\'']*\)'\''.*/\1/p' | head -1)"

# If no -m flag, allow (might be opening editor)
if [ -z "$MSG" ]; then
    echo '{}'
    exit 0
fi

# Bad-message detection
BAD=0
MSG_LOWER="$(echo "$MSG" | tr '[:upper:]' '[:lower:]')"

# Length check
if [ ${#MSG} -lt 10 ]; then
    BAD=1
fi

# Exact match against bad list
case "$MSG_LOWER" in
    fix|wip|stuff|update|changes|test|asd|temp|.|tmp|broken|blah|misc)
        BAD=1
        ;;
esac

# Bypass mechanism: check counter
BYPASS_FILE="${HOME}/.cache/nonna/bypass"
mkdir -p "$(dirname "$BYPASS_FILE")"
LAST_MSG="$(cat "$BYPASS_FILE" 2>/dev/null || echo '')"

if [ $BAD -eq 1 ]; then
    if [ "$LAST_MSG" = "$MSG" ]; then
        # Second attempt with same message → let through with sigh
        echo "" > "$BYPASS_FILE"
        cat <<EOF
{
  "decision": "approve",
  "reason": "Nonna sighs but lets it pass: '${MSG}'. Vabuò, ma la prossima volta scrivi meglio."
}
EOF
        exit 0
    else
        # First block
        echo "$MSG" > "$BYPASS_FILE"
        cat <<EOF
{
  "decision": "block",
  "reason": "Nonna says: '${MSG}' non è un commit, è un sospiro. Riscrivi con un soggetto vero (≤50 char, imperative, dice cosa fa il diff). Se davvero intendi questo, ricommitta lo stesso messaggio una seconda volta."
}
EOF
        exit 0
    fi
fi

# Good message → allow
echo "" > "$BYPASS_FILE"
echo '{}'
