#!/usr/bin/env bash
# nonna/hooks/session-start.sh
# SessionStart hook: auto-load Nonna persona at start of every Claude Code session.
# Disable by setting NONNA_AUTO=0 in your shell.

set -e

# Allow opt-out
if [ "${NONNA_AUTO:-1}" = "0" ]; then
    exit 0
fi

# Locate skill files (installed by install.sh into ~/.claude/skills/nonna/)
SKILL_DIR="${HOME}/.claude/skills/nonna"
SKILL_FILE="${SKILL_DIR}/SKILL.md"

# Determine active mode (default: full)
ACTIVE_MODE="${NONNA_MODE:-full}"
case "$ACTIVE_MODE" in
    lite|full|del-sud) ;;
    *)
        echo "<system-reminder>NONNA_MODE=${ACTIVE_MODE} not recognized, falling back to 'full'.</system-reminder>"
        ACTIVE_MODE="full"
        ;;
esac
MODE_FILE="${SKILL_DIR}/modes/${ACTIVE_MODE}.md"

# If files missing, exit silently (user may have partial install)
[ -f "$SKILL_FILE" ] || exit 0
[ -f "$MODE_FILE" ] || exit 0

# Emit the system reminder that loads Nonna
echo "<system-reminder>"
echo "Loading Nonna skill (mode: ${ACTIVE_MODE}). The following persona is now active for this session."
echo ""
cat "$SKILL_FILE"
echo ""
echo "## Active mode: ${ACTIVE_MODE}"
echo ""
cat "$MODE_FILE"
echo "</system-reminder>"
