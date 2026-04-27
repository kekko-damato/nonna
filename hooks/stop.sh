#!/usr/bin/env bash
# nonna/hooks/stop.sh
# Stop hook: desktop notification when Claude finishes responding.
# Late-night warning if local time is in NONNA_QUIET_HOURS (default: 23-5).

set -e

# Allow opt-out
QUIET="${NONNA_QUIET_HOURS:-23-5}"
if [ "$QUIET" = "off" ]; then
    exit 0
fi

# Parse start-end (format "23-5" means 23:00 to 05:00)
START="${QUIET%-*}"
END="${QUIET#*-}"
HOUR=$(date +%H | sed 's/^0*//')
HOUR=${HOUR:-0}

LATE=0
if [ "$START" -gt "$END" ]; then
    # Wraps midnight: late if hour >= start OR hour < end
    if [ "$HOUR" -ge "$START" ] || [ "$HOUR" -lt "$END" ]; then
        LATE=1
    fi
else
    if [ "$HOUR" -ge "$START" ] && [ "$HOUR" -lt "$END" ]; then
        LATE=1
    fi
fi

# Build message
if [ $LATE -eq 1 ]; then
    MSG="Nonna: vai a dormire, caro. Domani lo vedi meglio."
else
    MSG="Nonna: finito."
fi

# Cross-platform notification
case "$(uname -s)" in
    Darwin)
        osascript -e "display notification \"$MSG\" with title \"Nonna\" sound name \"Glass\"" 2>/dev/null || true
        ;;
    Linux)
        if command -v notify-send &>/dev/null; then
            notify-send "Nonna" "$MSG" 2>/dev/null || true
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # Windows: skip silently unless PowerShell available
        if command -v powershell.exe &>/dev/null; then
            powershell.exe -Command "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('$MSG', 'Nonna')" 2>/dev/null || true
        fi
        ;;
esac

# Optional ntfy.sh push (power-user feature)
if [ -n "$NONNA_NOTIFY" ]; then
    case "$NONNA_NOTIFY" in
        ntfy:*)
            TOPIC="${NONNA_NOTIFY#ntfy:}"
            curl -s -d "$MSG" "https://ntfy.sh/$TOPIC" >/dev/null || true
            ;;
    esac
fi

exit 0
