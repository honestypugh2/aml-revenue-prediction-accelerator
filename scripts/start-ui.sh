#!/usr/bin/env bash
# Start the Revenue Prediction Accelerator UI (FastAPI backend serving the built
# React app) as a background process. Idempotent: refuses to start a second
# instance. Use scripts/stop-ui.sh to stop it.
#
# Usage:
#   scripts/start-ui.sh [--host HOST] [--port PORT] [--reload]
#                       [--no-build] [--foreground]
#
# Environment overrides: UI_HOST (default 127.0.0.1), UI_PORT (default 8000).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/.run"
PID_FILE="$RUN_DIR/ui.pid"
LOG_FILE="$RUN_DIR/ui.log"

HOST="${UI_HOST:-127.0.0.1}"
PORT="${UI_PORT:-8000}"
RELOAD=""
BUILD=1
FOREGROUND=0

while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --port|-p) PORT="$2"; shift 2 ;;
    --reload) RELOAD="--reload"; shift ;;
    --no-build) BUILD=0; shift ;;
    --foreground|--fg) FOREGROUND=1; shift ;;
    -h|--help)
      sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

cd "$REPO_ROOT"
mkdir -p "$RUN_DIR"

# Already running?
if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "UI already running (PID $OLD_PID) -> http://$HOST:$PORT"
    echo "Stop it first with: scripts/stop-ui.sh"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

# Build the React app if the bundle is missing (skip with --no-build).
if [ "$BUILD" -eq 1 ] && [ ! -f "$REPO_ROOT/frontend/dist/index.html" ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "==> Building React UI (frontend/dist not found)"
    npm --prefix frontend install
    npm --prefix frontend run build
  else
    echo "==> npm not found; starting API without the built UI (API only at /docs)"
  fi
fi

SERVE_CMD=(uv run revenue-prediction serve --host "$HOST" --port "$PORT")
[ -n "$RELOAD" ] && SERVE_CMD+=("$RELOAD")

if [ "$FOREGROUND" -eq 1 ]; then
  echo "==> Serving in foreground on http://$HOST:$PORT  (Ctrl+C to stop)"
  exec "${SERVE_CMD[@]}"
fi

echo "==> Starting UI on http://$HOST:$PORT"
if command -v setsid >/dev/null 2>&1; then
  setsid "${SERVE_CMD[@]}" >"$LOG_FILE" 2>&1 </dev/null &
else
  nohup "${SERVE_CMD[@]}" >"$LOG_FILE" 2>&1 </dev/null &
fi
PID=$!
echo "$PID" >"$PID_FILE"

# Give it a moment and confirm it stayed up.
sleep 2
if ! kill -0 "$PID" 2>/dev/null; then
  echo "UI failed to start. Last log lines:" >&2
  tail -n 20 "$LOG_FILE" >&2 || true
  rm -f "$PID_FILE"
  exit 1
fi

if command -v curl >/dev/null 2>&1; then
  for _ in $(seq 1 20); do
    if curl -fsS "http://$HOST:$PORT/api/health" >/dev/null 2>&1; then break; fi
    sleep 0.5
  done
fi

echo "UI running (PID $PID)"
echo "  URL:  http://$HOST:$PORT   (API docs at /docs)"
echo "  Log:  $LOG_FILE"
echo "  Stop: scripts/stop-ui.sh"
