# Judging Day Runbook

## Launch Order

1. Start AMD vLLM/Qwen runtime.
2. Start FastAPI agent service.
3. Start Cloudflare Tunnel to FastAPI port `8010`.
4. Update HF Space secrets if the API URL changed.
5. Run `scripts/amd_runtime_rehearsal.py`.
6. Run `scripts/public_smoke.py`.
7. Run `scripts/final_submission_gate.py`.
8. Open HF Space and run `Checkout API deploy regression`.
9. Capture screenshot, public status JSON, readiness JSON, video, and slide deck.

## Required Evidence

- `runtime_proof.backend_mode=live_vllm`.
- `runtime_proof.amd_runtime_evidence.ok=true`.
- `Qwen critic: ok`.
- War Room Packet with audit seal.
- `/api/readiness` verdict `GO`.
- `scripts/final_submission_gate.py` verdict `GO_SUBMIT`.
- Public HF Space URL visible.
- Public API URL or readiness endpoint visible.

## Stop Condition

If live AMD/Qwen proof is missing, do not submit as `GO`. Submit only with explicit fallback limitation or wait until the AMD proof is recovered. If `scripts/final_submission_gate.py` returns `NO_GO_UNTIL_BLOCKERS_CLOSE`, treat it as a hard stop for a winning-tier submission.

## Final Smoke Commands

```bash
python scripts/amd_runtime_rehearsal.py --public-api-base "$INFRAAGENT_API_BASE"
python scripts/public_smoke.py --api-base "$INFRAAGENT_API_BASE" --space-host "https://clendeningantonettie-infraagent-replayops.hf.space"
python scripts/final_submission_gate.py --api-base "$INFRAAGENT_API_BASE" --api-key-file .runtime/local_api_key.txt --space-host "https://clendeningantonettie-infraagent-replayops.hf.space"
pytest -q
```
