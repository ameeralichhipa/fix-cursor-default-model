#!/bin/bash
# Double-click on macOS to keep Cursor on Auto.
set -euo pipefail
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3 is required. Install from https://www.python.org/downloads/ then run again."
  read -r -p "Press Enter to close..."
  exit 1
fi

"$PY" "$(dirname "$0")/fix_cursor_default_model.py"
exit $?
