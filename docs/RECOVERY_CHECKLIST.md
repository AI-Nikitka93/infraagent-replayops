# Manual Recovery Checklist

## Runtime

1. SSH into the AMD Developer Cloud VM.
2. Confirm GPU access: `ls /dev/kfd /dev/dri` and `rocminfo`.
3. Start vLLM: `bash start_vllm_rocm.sh`.
4. Confirm model service locally: `curl http://127.0.0.1:8000/v1/models`.

## Agent Service

1. Export `PUBLIC_API_KEY` and vLLM env values.
2. Start FastAPI: `python server.py`.
3. Confirm local health: `curl http://127.0.0.1:8010/health`.
4. Confirm readiness: `curl http://127.0.0.1:8010/api/readiness`.

## Tunnel

1. Preferred: start named Cloudflare Tunnel pointing to `http://127.0.0.1:8010`.
2. Fallback: `bash start_tunnel.sh` or `python scripts/refresh_public_demo.py --force-new-tunnel`.
3. Confirm public `/health`.
4. Do not expose `http://127.0.0.1:8000` or raw vLLM.

## Hugging Face Space

1. Update `INFRAAGENT_API_BASE` only if the public API URL changed.
2. Keep `INFRAAGENT_API_KEY` as a Space secret.
3. Run public smoke: `python scripts/public_smoke.py --api-base <public-api-url> --space-host https://clendeningantonettie-infraagent-replayops.hf.space`.

## If Live AMD Fails

Use contingency wording from `SUBMISSION.md`. Keep fallback demo available, but do not claim `GO`, `live_vllm`, or Qwen critic proof.
