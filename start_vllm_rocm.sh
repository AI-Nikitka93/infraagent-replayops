#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env}"

log() {
  echo "[$(date -Is)] [vllm-rocm] $*"
}

fail() {
  echo "[$(date -Is)] [vllm-rocm] ERROR: $*" >&2
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

normalize_secret() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "$value" || "$value" == CHANGE_ME* ]]; then
    require_command openssl
    value="$(openssl rand -hex 32)"
    export "$name=$value"
    log "${name} was not set to a real value; generated a runtime-only key."
  fi
}

wait_for_vllm() {
  local deadline=$((SECONDS + VLLM_STARTUP_TIMEOUT_SECONDS))
  local http_code

  log "Waiting for vLLM health endpoint: ${VLLM_HEALTH_URL}"
  while (( SECONDS < deadline )); do
    http_code="$(
      curl -sS -o /dev/null \
        -H "Authorization: Bearer ${VLLM_API_KEY}" \
        -w "%{http_code}" \
        "${VLLM_HEALTH_URL}" || true
    )"

    if [[ "$http_code" == "200" ]]; then
      log "vLLM is healthy at ${VLLM_HEALTH_URL}"
      return 0
    fi

    log "vLLM not ready yet; HTTP ${http_code:-000}. Sleeping ${VLLM_HEALTH_POLL_SECONDS}s."
    sleep "$VLLM_HEALTH_POLL_SECONDS"
  done

  log "Recent container logs:"
  docker logs --tail 120 "${VLLM_CONTAINER_NAME}" >&2 || true
  fail "vLLM health check timed out after ${VLLM_STARTUP_TIMEOUT_SECONDS}s."
}

main() {
  load_env

  require_command docker
  require_command curl

  : "${HF_CACHE:=/mnt/data/huggingface-cache}"
  : "${VLLM_IMAGE:=vllm/vllm-openai-rocm:v0.20.1}"
  : "${VLLM_CONTAINER_NAME:=infraagent-vllm-qwen25-72b}"
  : "${VLLM_MODEL:=Qwen/Qwen2.5-72B-Instruct}"
  : "${VLLM_SERVED_MODEL_NAME:=qwen2.5-72b-instruct}"
  : "${VLLM_HOST:=0.0.0.0}"
  : "${VLLM_PORT:=8000}"
  : "${VLLM_DTYPE:=bfloat16}"
  : "${VLLM_TENSOR_PARALLEL_SIZE:=1}"
  : "${VLLM_MAX_MODEL_LEN:=32768}"
  : "${VLLM_GPU_MEMORY_UTILIZATION:=0.90}"
  : "${VLLM_MAX_NUM_SEQS:=16}"
  : "${VLLM_STARTUP_TIMEOUT_SECONDS:=2400}"
  : "${VLLM_HEALTH_POLL_SECONDS:=10}"
  : "${VLLM_HEALTH_URL:=http://127.0.0.1:8000/v1/models}"

  normalize_secret VLLM_API_KEY

  [[ -e /dev/kfd ]] || fail "/dev/kfd not found. ROCm device access is not available."
  [[ -e /dev/dri ]] || fail "/dev/dri not found. ROCm render device access is not available."

  mkdir -p "$HF_CACHE"
  log "Using Hugging Face cache: ${HF_CACHE}"
  log "Using vLLM image: ${VLLM_IMAGE}"
  log "Serving model: ${VLLM_MODEL} as ${VLLM_SERVED_MODEL_NAME}"

  if docker ps -a --format '{{.Names}}' | grep -Fxq "$VLLM_CONTAINER_NAME"; then
    log "Removing existing container: ${VLLM_CONTAINER_NAME}"
    docker rm -f "$VLLM_CONTAINER_NAME" >/dev/null
  fi

  docker run -d \
    --name "${VLLM_CONTAINER_NAME}" \
    --restart unless-stopped \
    --device /dev/kfd \
    --device /dev/dri \
    --group-add video \
    --ipc=host \
    --cap-add SYS_PTRACE \
    --security-opt seccomp=unconfined \
    --shm-size 32g \
    -p 127.0.0.1:8000:8000 \
    -v "${HF_CACHE}:/root/.cache/huggingface" \
    -e "HF_TOKEN=${HF_TOKEN:-}" \
    "${VLLM_IMAGE}" \
    --model "${VLLM_MODEL}" \
    --served-model-name "${VLLM_SERVED_MODEL_NAME}" \
    --host "${VLLM_HOST}" \
    --port "${VLLM_PORT}" \
    --dtype "${VLLM_DTYPE}" \
    --tensor-parallel-size "${VLLM_TENSOR_PARALLEL_SIZE}" \
    --max-model-len "${VLLM_MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION}" \
    --max-num-seqs "${VLLM_MAX_NUM_SEQS}" \
    --api-key "${VLLM_API_KEY}" >/dev/null

  log "Container started: ${VLLM_CONTAINER_NAME}"
  wait_for_vllm
  log "OpenAI-compatible base URL: http://127.0.0.1:8000/v1"
  log "Use Authorization: Bearer ${VLLM_API_KEY}"
}

main "$@"
