#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env}"

log() {
  echo "[$(date -Is)] [cloudflare-tunnel] $*"
}

fail() {
  echo "[$(date -Is)] [cloudflare-tunnel] ERROR: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

load_env() {
  if [[ -f "$ENV_FILE" ]]; then
    log "Loading environment from ${ENV_FILE}"
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  else
    log "No .env file found at ${ENV_FILE}; using process environment and script defaults."
  fi
}

wait_for_langgraph_api() {
  local deadline=$((SECONDS + LANGGRAPH_STARTUP_TIMEOUT_SECONDS))
  local http_code

  log "Checking local LangGraph API before opening tunnel: ${LANGGRAPH_BASE_URL}"
  while (( SECONDS < deadline )); do
    http_code="$(
      curl -sS -o /dev/null \
        --max-time 2 \
        -w "%{http_code}" \
        "${LANGGRAPH_HEALTH_URL}" || true
    )"

    if [[ "$http_code" =~ ^[234][0-9][0-9]$ ]]; then
      log "LangGraph health endpoint is reachable with HTTP ${http_code}."
      return 0
    fi

    http_code="$(
      curl -sS -o /dev/null \
        --max-time 2 \
        -w "%{http_code}" \
        "${LANGGRAPH_BASE_URL}" || true
    )"

    if [[ "$http_code" =~ ^[234][0-9][0-9]$ ]]; then
      log "LangGraph base URL is reachable with HTTP ${http_code}."
      return 0
    fi

    log "LangGraph API not ready yet; HTTP ${http_code:-000}. Sleeping ${LANGGRAPH_HEALTH_POLL_SECONDS}s."
    sleep "$LANGGRAPH_HEALTH_POLL_SECONDS"
  done

  fail "LangGraph API did not become reachable on ${LANGGRAPH_BASE_URL} within ${LANGGRAPH_STARTUP_TIMEOUT_SECONDS}s."
}

main() {
  load_env

  : "${CLOUDFLARED_BIN:=cloudflared}"
  require_command "${CLOUDFLARED_BIN}"
  require_command curl
  require_command grep
  require_command tail

  : "${LANGGRAPH_BASE_URL:=http://127.0.0.1:8010}"
  : "${LANGGRAPH_HEALTH_URL:=http://127.0.0.1:8010/health}"
  : "${LANGGRAPH_STARTUP_TIMEOUT_SECONDS:=120}"
  : "${LANGGRAPH_HEALTH_POLL_SECONDS:=2}"
  : "${CLOUDFLARED_TARGET_URL:=http://localhost:8010}"
  : "${CLOUDFLARED_LOG_FILE:=.runtime/cloudflared-quick-tunnel.log}"
  : "${CLOUDFLARED_PROTOCOL:=http2}"

  if [[ "$CLOUDFLARED_TARGET_URL" != "http://localhost:8010" && "$CLOUDFLARED_TARGET_URL" != "http://127.0.0.1:8010" ]]; then
    fail "Tunnel target must expose LangGraph port 8010, got: ${CLOUDFLARED_TARGET_URL}"
  fi

  wait_for_langgraph_api

  mkdir -p "$(dirname "${CLOUDFLARED_LOG_FILE}")"
  : > "${CLOUDFLARED_LOG_FILE}"

  log "Starting Cloudflare Quick Tunnel to ${CLOUDFLARED_TARGET_URL} with protocol ${CLOUDFLARED_PROTOCOL}"
  "${CLOUDFLARED_BIN}" tunnel --protocol "${CLOUDFLARED_PROTOCOL}" --url "${CLOUDFLARED_TARGET_URL}" >"${CLOUDFLARED_LOG_FILE}" 2>&1 &
  local tunnel_pid=$!

  cleanup() {
    if kill -0 "$tunnel_pid" >/dev/null 2>&1; then
      log "Stopping cloudflared process ${tunnel_pid}"
      kill "$tunnel_pid" >/dev/null 2>&1 || true
    fi
  }
  trap cleanup INT TERM EXIT

  local deadline=$((SECONDS + 60))
  local public_url=""
  while (( SECONDS < deadline )); do
    if ! kill -0 "$tunnel_pid" >/dev/null 2>&1; then
      cat "${CLOUDFLARED_LOG_FILE}" >&2 || true
      fail "cloudflared exited before publishing a Quick Tunnel URL."
    fi

    public_url="$(grep -Eo 'https://[A-Za-z0-9.-]+\.trycloudflare\.com' "${CLOUDFLARED_LOG_FILE}" | tail -n 1 || true)"
    if [[ -n "$public_url" ]]; then
      log "Public Quick Tunnel URL: ${public_url}"
      log "HF Space should call: ${public_url}/api/triage and ${public_url}/api/status/{run_id}"
      log "Keeping tunnel process attached. Press Ctrl+C to stop."
      break
    fi

    sleep 1
  done

  [[ -n "$public_url" ]] || fail "Timed out waiting for *.trycloudflare.com URL in cloudflared logs."

  tail -f "${CLOUDFLARED_LOG_FILE}" &
  local tail_pid=$!
  wait "$tunnel_pid"
  kill "$tail_pid" >/dev/null 2>&1 || true
}

main "$@"
