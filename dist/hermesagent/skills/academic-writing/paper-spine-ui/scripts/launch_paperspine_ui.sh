#!/usr/bin/env bash
# Launch the PaperSpine intake TUI in an external terminal window.
# Cross-platform: macOS (Terminal.app), Linux (gnome-terminal / xterm / konsole).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIZARD="$SCRIPT_DIR/intake_wizard.py"
OUTPUT_DIR="${1:-paper_rewriting_output}"

if [ ! -f "$WIZARD" ]; then
    echo "PaperSpine intake wizard not found: $WIZARD" >&2
    exit 1
fi

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3 not found. Install Python and retry." >&2
    exit 1
fi

CMD="$PYTHON \"$WIZARD\" --keyboard-ui --output-dir \"$OUTPUT_DIR\"; echo ''; echo 'PaperSpine intake finished. Config files are in: $OUTPUT_DIR'; echo 'Close this window after checking the result.'; exec bash"

case "$(uname -s)" in
    Darwin)
        osascript -e "tell application \"Terminal\" to do script \"$CMD\""
        ;;
    Linux)
        if command -v gnome-terminal &>/dev/null; then
            gnome-terminal -- bash -c "$CMD"
        elif command -v konsole &>/dev/null; then
            konsole -e bash -c "$CMD"
        elif command -v xfce4-terminal &>/dev/null; then
            xfce4-terminal -e "bash -c '$CMD'"
        elif command -v xterm &>/dev/null; then
            xterm -e bash -c "$CMD" &
        else
            echo "No supported terminal found. Run directly:" >&2
            echo "  $PYTHON $WIZARD --keyboard-ui --output-dir $OUTPUT_DIR" >&2
            exit 1
        fi
        ;;
    *)
        echo "Unsupported OS: $(uname -s)" >&2
        exit 1
        ;;
esac
