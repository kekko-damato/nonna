#!/usr/bin/env bash
# nonna/uninstall.sh
# Remove Nonna from ~/.claude/, restore settings.json from latest backup.

set -e

CLAUDE_DIR="${HOME}/.claude"
SKILL_TARGET="${CLAUDE_DIR}/skills/nonna"
COMMANDS_DIR="${CLAUDE_DIR}/commands"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"

echo "Nonna uninstaller"
echo "================="

# 1. Remove skill dir
if [ -d "$SKILL_TARGET" ]; then
    echo "→ Removing ${SKILL_TARGET}..."
    rm -rf "$SKILL_TARGET"
fi

# 2. Remove command symlinks
echo "→ Removing command links..."
for cmd in nonna-review nonna-architect nonna-checkup nonna-explain; do
    target="${COMMANDS_DIR}/${cmd}.md"
    if [ -L "$target" ]; then
        rm "$target"
    fi
done

# 3. Restore settings.json from latest backup, OR remove only Nonna entries
if [ -f "$SETTINGS_FILE" ]; then
    # shellcheck disable=SC2012  # backup filenames are timestamp-only, no special chars — ls is safe here
    LATEST_BACKUP="$(ls -1t "${SETTINGS_FILE}.bak."* 2>/dev/null | head -1 || echo '')"
    if [ -n "$LATEST_BACKUP" ]; then
        echo "→ Restoring settings.json from ${LATEST_BACKUP}..."
        cp "$LATEST_BACKUP" "$SETTINGS_FILE"
    else
        echo "→ No backup found — manually removing Nonna entries from settings.json..."
        python3 - "$SETTINGS_FILE" <<'PYEOF'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
settings = json.loads(settings_path.read_text())

def filter_hooks(event_list):
    return [
        e for e in event_list
        if not any("nonna" in str(h).lower() for h in e.get("hooks", []))
    ]

if "hooks" in settings:
    for event in list(settings["hooks"].keys()):
        settings["hooks"][event] = filter_hooks(settings["hooks"][event])
        if not settings["hooks"][event]:
            del settings["hooks"][event]
    if not settings["hooks"]:
        del settings["hooks"]

settings_path.write_text(json.dumps(settings, indent=2))
PYEOF
    fi
fi

echo ""
echo "✓ Nonna uninstalled."
echo ""
echo "  Vai pure, ti ho voluto bene."
echo ""
