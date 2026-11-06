#!/usr/bin/env bash
# Quickstart (macOS / Linux)
set -u
PY=${PYTHON:-python3}
echo "Running doctor check..."
if ! "$PY" -m lab doctor; then
  echo "Doctor check failed. See the checks marked ok=false above." >&2
  exit 1
fi
echo "Starting OpenCode..."
if command -v opencode >/dev/null 2>&1; then
  exec opencode
else
  echo "OpenCode CLI is not on PATH. Install it from https://opencode.ai/docs/" >&2
fi
