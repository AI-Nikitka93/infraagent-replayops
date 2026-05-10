# Hackathon Readiness Gate

This file is the strict pre-submission gate. Do not submit until every required external item is filled.

Current judge-facing gap statement: fallback demo verified, live AMD/Qwen proof pending.

## Local Package
- [x] README explains the project quickly.
- [x] MIT license exists.
- [x] Submission copy exists.
- [x] Demo script exists.
- [x] Slide outline exists.
- [x] Market pain map exists.
- [x] `.gitignore` protects `.env`, runtime logs, process IDs, caches, and local browser artifacts.
- [x] Backend tests cover polling, auth, runtime proof, readiness, and ReplayOps fields.
- [x] UI tests cover polling, evidence panels, business lens, and runtime truth wording.

## External Submission
- [x] Public GitHub URL: https://github.com/AI-Nikitka93/infraagent-replayops
- [x] HF Space URL: https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops
- [x] Application URL: https://clendeningantonettie-infraagent-replayops.hf.space
- [x] Video URL: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-demo.mp4
- [x] Slide deck URL: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-slides.pdf
- [x] Current public API tunnel smoke: https://seattle-rock-south-bath.trycloudflare.com reached `/health`, `/api/triage`, and HF Space `READY`.
- [ ] AMD VM proof: `/api/status/{run_id}` shows `runtime_proof.backend_mode=live_vllm`
- [ ] Qwen proof: root cause panel shows `Qwen critic: ok`
- [ ] `/api/readiness` returns `verdict=GO`

## Artifacts to refresh after live AMD proof
- README, SUBMISSION, HACKATHON_READINESS, STATE, state.json, EXEC_PLAN, and PROJECT_HISTORY.
- Final demo video, slide deck, screenshot, `.runtime/amd_live_proof.json`, and `.runtime/public_demo_status.json`.
- HF Space secrets and public API URL if the AMD-backed tunnel changes.

## Stable Public Access Plan
- Preferred: named Cloudflare Tunnel on a stable hostname targeting FastAPI on `8010`.
- Fallback: Quick Tunnel refreshed immediately before judging.
- Boundary: expose the agent service only; do not expose raw vLLM on `8000`.

## Non-Negotiable Honesty Rules
- Do not claim production telemetry. The demo uses mock observability fixtures.
- Do not claim live Qwen unless `live_vllm` is visible in the run.
- Do not hide fallback mode in video or screenshots.
- Do not claim auto-remediation. The product recommends actions with human approval.

## Claim Audit
- README, SUBMISSION, SLIDES, DEMO_SCRIPT, HF Space UI, and readiness all must keep fallback/live truth visible.
- Screenshots and videos must not crop out runtime mode.
- Build in Public posts must not reveal tokens, local private hostnames, `.runtime` files, or Cloudflare credentials.
- Public repository history must be checked with `scripts/security_privacy_audit.py` before final publication.

## Final Judge Path
1. Judge opens HF Space.
2. Judge starts scenario.
3. Judge sees graph reach READY.
4. Judge checks runtime proof.
5. Judge reads evidence timeline and owner routing.
6. Judge opens War Room Packet.
7. Judge sees README and public GitHub match the demo behavior.

## Final Submit Gate

Run the blocking gate after the AMD-backed public path is refreshed:

```bash
python scripts/final_submission_gate.py --api-base "$INFRAAGENT_API_BASE" --api-key-file .runtime/local_api_key.txt --space-host https://clendeningantonettie-infraagent-replayops.hf.space
```

Only submit on `GO_SUBMIT`. If it returns `NO_GO_UNTIL_BLOCKERS_CLOSE`, fix the listed blockers instead of editing the wording around them.

## Refresh Procedure
Run before final judging if using a Cloudflare Quick Tunnel:

```bash
python scripts/refresh_public_demo.py --update-hf-space --smoke-space
```

Quick Tunnel URLs are temporary. A named Cloudflare Tunnel with a stable hostname is preferred for final judging if a Cloudflare-managed domain is available.

## Recovery / Judging Procedures
- Manual recovery: `docs/RECOVERY_CHECKLIST.md`
- Judging day runbook: `docs/JUDGING_DAY_RUNBOOK.md`
- Public smoke: `python scripts/public_smoke.py --api-base <public-api-url> --api-key-file .runtime/local_api_key.txt --space-host https://clendeningantonettie-infraagent-replayops.hf.space`
