#!/usr/bin/env bash
# assets/record_demo.sh
# Auto-record a demo GIF for the Nonna skill.
#
# What it does:
#   1. Moves ~/.claude/skills/nonna/ out temporarily (prevents auto-discovery contamination)
#   2. Records the main display for ~75 seconds (macOS screencapture)
#   3. Runs default Claude on the demo prompt (no Nonna present)
#   4. Runs same prompt with Nonna injected via --append-system-prompt
#   5. Stops recording, restores Nonna, converts to GIF
#
# Requirements:
#   - macOS (uses `screencapture`)
#   - ffmpeg (`brew install ffmpeg`)
#   - claude CLI (Claude Code) in PATH
#   - Nonna files at ~/.claude/skills/nonna/ (run ./install.sh from repo root if missing)
#
# First run: macOS will ask for Screen Recording permission.
# Grant it in System Settings → Privacy & Security → Screen Recording, then re-run.
#
# Override defaults via env vars:
#   NONNA_DEMO_PROMPT="..." NONNA_DEMO_DURATION=80 NONNA_DEMO_WIDTH=720 bash assets/record_demo.sh

set -e

# ───── CONFIG ─────
DEMO_PROMPT="${NONNA_DEMO_PROMPT:-I want to add microservices to my 5-user app}"
RECORDING_SECONDS="${NONNA_DEMO_DURATION:-75}"
TARGET_WIDTH="${NONNA_DEMO_WIDTH:-900}"
GIF_FPS="${NONNA_DEMO_FPS:-12}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
NONNA_DIR="$SKILLS_DIR/nonna"
NONNA_DISABLED="$SKILLS_DIR/.nonna-disabled-during-recording"
RAW_VIDEO="/tmp/nonna-demo-raw-$$.mov"
OUTPUT_GIF="$REPO_ROOT/assets/demo.gif"

# ───── PRE-FLIGHT ─────
fail() { echo "✗ $1" >&2; exit 1; }

[ "$(uname -s)" = "Darwin" ] || fail "This script requires macOS (uses screencapture)."
command -v screencapture >/dev/null || fail "screencapture not found."
command -v claude >/dev/null || fail "claude CLI not found in PATH."
command -v ffmpeg >/dev/null || fail "ffmpeg not installed. Run: brew install ffmpeg"

# Use repo files directly for Nonna injection (more reliable than ~/.claude/skills/ path)
[ -f "$REPO_ROOT/SKILL.md" ] || fail "SKILL.md not found at $REPO_ROOT — run from inside repo."
[ -f "$REPO_ROOT/modes/full.md" ] || fail "modes/full.md not found."

NONNA_SYSTEM="$(cat "$REPO_ROOT/SKILL.md")
$(cat "$REPO_ROOT/modes/full.md")"

# ───── CLEANUP TRAP (always restore Nonna) ─────
restore_nonna() {
    if [ -d "$NONNA_DISABLED" ]; then
        mv "$NONNA_DISABLED" "$NONNA_DIR" 2>/dev/null || true
        echo "✓ Restored ~/.claude/skills/nonna"
    fi
}
trap restore_nonna EXIT INT TERM

# ───── INTRO ─────
clear
cat <<'EOF'
═══════════════════════════════════════════════════
   Nonna demo recorder
═══════════════════════════════════════════════════

This script will record a screen demo (~75s) showing:
  1. Default Claude responding to a prompt
  2. Same prompt, with Nonna active

Output: assets/demo.gif (auto-converted)

BEFORE pressing ENTER:

  □ Make THIS terminal big          (Cmd+Opt+F or maximize)
  □ Use a dark theme + ~18pt font
  □ Hide Dock                        (Cmd+Opt+D)
  □ Hide menu bar                    (System Settings → Control Center → Auto-hide)
  □ Enable Do Not Disturb            (Focus → Do Not Disturb)
  □ Close apps that may pop notifications

DURING recording (75s):
  → DON'T touch keyboard or mouse
  → DON'T switch windows
  → The script handles everything

If macOS asks for Screen Recording permission, grant it then re-run.

Press ENTER when ready (or Ctrl+C to abort)...
EOF
read

# ───── DISABLE NONNA AUTO-DISCOVERY ─────
if [ -d "$NONNA_DIR" ]; then
    echo "→ Temporarily disabling Nonna auto-discovery..."
    mv "$NONNA_DIR" "$NONNA_DISABLED"
fi

# ───── COUNTDOWN ─────
clear
for i in 5 4 3 2 1; do
    printf "\rStarting in %s... " "$i"
    sleep 1
done
echo ""

# ───── START RECORDING ─────
screencapture -v -V "$RECORDING_SECONDS" -x -C "$RAW_VIDEO" 2>/dev/null &
SCREEN_PID=$!
sleep 1.5

# ───── ACT 1: DEFAULT CLAUDE ─────
clear
cat <<'EOF'
╔═══════════════════════════════════════╗
║         DEFAULT CLAUDE                ║
╚═══════════════════════════════════════╝
EOF
sleep 2
echo ""
echo "$ $DEMO_PROMPT"
echo ""
sleep 2

# Default: no system prompt, no Nonna in skills dir
claude -p "$DEMO_PROMPT" 2>/dev/null || echo "(claude failed)"

sleep 3

# ───── ACT 2: WITH NONNA ─────
clear
cat <<'EOF'
╔═══════════════════════════════════════╗
║         WITH NONNA                    ║
╚═══════════════════════════════════════╝
EOF
sleep 2
echo ""
echo "$ $DEMO_PROMPT"
echo ""
sleep 2

# Nonna injected via system prompt
claude -p --append-system-prompt "$NONNA_SYSTEM" "$DEMO_PROMPT" 2>/dev/null || echo "(claude failed)"

sleep 3

# ───── ACT 3: CTA ─────
clear
cat <<'EOF'




   github.com/kekko-damato/nonna




EOF
sleep 4

# ───── STOP RECORDING ─────
if kill -0 "$SCREEN_PID" 2>/dev/null; then
    kill -INT "$SCREEN_PID" 2>/dev/null || true
fi
wait "$SCREEN_PID" 2>/dev/null || true

# Restore Nonna (trap will also catch this on exit)
restore_nonna
trap - EXIT INT TERM  # disarm trap since we handled it

if [ ! -f "$RAW_VIDEO" ] || [ ! -s "$RAW_VIDEO" ]; then
    fail "Recording produced empty file. Check Screen Recording permission in System Settings."
fi

clear
echo "✓ Recording done. Raw: $RAW_VIDEO ($(ls -lh "$RAW_VIDEO" | awk '{print $5}'))"
echo ""
echo "Converting to GIF (~30s)..."

# ───── CONVERT TO GIF ─────
mkdir -p "$(dirname "$OUTPUT_GIF")"
ffmpeg -y -i "$RAW_VIDEO" \
    -vf "fps=$GIF_FPS,scale=$TARGET_WIDTH:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
    -loop 0 \
    "$OUTPUT_GIF" 2>&1 | tail -3

GIF_SIZE_KB=$(stat -f %z "$OUTPUT_GIF" 2>/dev/null | awk '{print int($1/1024)}')

cat <<EOF

═══════════════════════════════════════════════════
✓ Done!

  GIF: $OUTPUT_GIF
  Size: ${GIF_SIZE_KB} KB
  Width: ${TARGET_WIDTH}px

Preview: open "$OUTPUT_GIF"

EOF

if [ "$GIF_SIZE_KB" -gt 10240 ]; then
    echo "⚠  GIF >10MB. GitHub may not render inline. Re-run with smaller width:"
    echo "   NONNA_DEMO_WIDTH=720 bash assets/record_demo.sh"
    echo ""
fi

echo "Cleanup raw video? [y/N]"
read -r CLEANUP
if [ "$CLEANUP" = "y" ] || [ "$CLEANUP" = "Y" ]; then
    rm -f "$RAW_VIDEO"
    echo "Cleaned up."
else
    echo "Raw video kept at: $RAW_VIDEO"
fi
