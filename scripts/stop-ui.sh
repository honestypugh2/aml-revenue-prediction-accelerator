#!/usr/bin/env bash
# Stop the Revenue Prediction Accelerator UI started by scripts/start-ui.sh.
# Falls back to the listening port if the PID file is missing.
#
# Usage:
#   scripts/stop-ui.sh [--port PORT]
#
# Environment override: UI_PORT (default 8000).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/.run"
PID_FILE="$RUN_DIR/ui.pid"

PORT="${UI_PORT:-8000}"
while [ $# -gt 0 ]; do
  case "$1" in
    --port|-p) PORT="$2"; shift 2 ;;
    -h|--help) sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

# Send TERM (then KILL) to a PID, targeting its process group when possible.
_terminate() {
  local pid="$1"
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || return 1
  for _ in $(seq 1 20); do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.25
  done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
  return 0
}

STOPPED=0

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    echo "==> Stopping UI (PID $PID)"
    _terminate "$PID" && STOPPED=1
  else
    echo "==> Stale PID file; process not running"
  fi
  rm -f "$PID_FILE"
fi

# Fallback: nothing stopped via PID file, try whatever is on the port.
if [ "$STOPPED" -eq 0 ]; then
  PORT_PID=""
  if command -v lsof >/dev/null 2>&1; then
    PORT_PID="$(lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null | head -n1 || true)"
  elif command -v fuser >/dev/null 2>&1; then
    PORT_PID="$(fuser "$PORT/tcp" 2>/dev/null | tr -d ' ' || true)"
  fi
  if [ -n "$PORT_PID" ]; then
    echo "==> Stopping process on port $PORT (PID $PORT_PID)"
    _terminate "$PORT_PID" && STOPPED=1
  fi
fi

if [ "$STOPPED" -eq 1 ]; then
  echo "UI stopped."
else
  echo "No running UI found (checked PID file and port $PORT)."
fi
