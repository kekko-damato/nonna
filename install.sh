#!/usr/bin/env bash
# nonna/install.sh
# Install Nonna skill into ~/.claude/skills/nonna/, register hooks in ~/.claude/settings.json.

set -e

NONNA_REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
SKILL_TARGET="${CLAUDE_DIR}/skills/nonna"
COMMANDS_DIR="${CLAUDE_DIR}/commands"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

FORCE=0
for arg in "$@"; do
    case "$arg" in
        --force) FORCE=1 ;;
    esac
done

echo "Nonna installer"
echo "==============="

# 1. Check Claude Code dirs
mkdir -p "${CLAUDE_DIR}/skills"
mkdir -p "${COMMANDS_DIR}"

# 2. Refuse if target exists and not --force
if [ -d "$SKILL_TARGET" ] && [ "$FORCE" -ne 1 ]; then
    echo "ERROR: ${SKILL_TARGET} already exists. Use --force to overwrite."
    exit 1
fi

# 3. Copy skill files
echo "→ Copying skill files to ${SKILL_TARGET}..."
rm -rf "$SKILL_TARGET"
mkdir -p "$SKILL_TARGET"
cp "${NONNA_REPO_DIR}/SKILL.md" "$SKILL_TARGET/"
cp -r "${NONNA_REPO_DIR}/modes" "$SKILL_TARGET/"
cp -r "${NONNA_REPO_DIR}/hooks" "$SKILL_TARGET/"
cp -r "${NONNA_REPO_DIR}/scripts" "$SKILL_TARGET/"
chmod +x "${SKILL_TARGET}/hooks/"*.sh

# 4. Symlink commands (with conflict check)
echo "→ Linking commands..."
for cmd_file in "${NONNA_REPO_DIR}/commands/"*.md; do
    cmd_name="$(basename "$cmd_file")"
    target="${COMMANDS_DIR}/${cmd_name}"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
        echo "  WARNING: ${target} already exists (not a symlink) — skipping"
        continue
    fi
    ln -sf "${SKILL_TARGET}/commands/${cmd_name}" "$target"
done
# Also copy commands into the skill dir (for relative refs)
mkdir -p "${SKILL_TARGET}/commands"
cp "${NONNA_REPO_DIR}/commands/"*.md "${SKILL_TARGET}/commands/"

# 5. Backup + merge settings.json
echo "→ Configuring hooks in ${SETTINGS_FILE}..."
if [ -f "$SETTINGS_FILE" ]; then
    BACKUP="${SETTINGS_FILE}.bak.${TIMESTAMP}"
    cp "$SETTINGS_FILE" "$BACKUP"
    echo "  Backup: ${BACKUP}"
fi

# Use Python to merge JSON (more robust than jq across platforms)
python3 - "$SETTINGS_FILE" "${SKILL_TARGET}/hooks" <<'PYEOF'
import json
import os
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
hooks_dir = sys.argv[2]

if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

settings.setdefault("hooks", {})

def add_hook(event, command, matcher=None):
    settings["hooks"].setdefault(event, [])
    entry = {"hooks": [{"type": "command", "command": command}]}
    if matcher:
        entry["matcher"] = matcher
    # Avoid duplicates
    cmd_str = str(entry)
    if any(str(e) == cmd_str for e in settings["hooks"][event]):
        return
    settings["hooks"][event].append(entry)

add_hook("SessionStart", f"{hooks_dir}/session-start.sh")
add_hook("PreToolUse", f"{hooks_dir}/pre-commit-check.sh", matcher="Bash")
add_hook("Stop", f"{hooks_dir}/stop.sh")

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2))
PYEOF

echo ""
echo "✓ Nonna installed."
echo ""
echo "  Bravo. Finalmente."
echo ""
echo "  Open a new Claude Code session and Nonna will be there."
echo "  Switch modes: /nonna-mode lite|full|del-sud"
echo "  Disable auto-load: export NONNA_AUTO=0"
echo "  Disable late-night warning: export NONNA_QUIET_HOURS=off"
echo ""
