# Hackathon Readiness Gate

This file is the strict pre-submission gate. Do not submit until every required external item is filled.

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

## Non-Negotiable Honesty Rules
- Do not claim production telemetry. The demo uses mock observability fixtures.
- Do not claim live Qwen unless `live_vllm` is visible in the run.
- Do not hide fallback mode in video or screenshots.
- Do not claim auto-remediation. The product recommends actions with human approval.

## Final Judge Path
1. Judge opens HF Space.
2. Judge starts scenario.
3. Judge sees graph reach READY.
4. Judge checks runtime proof.
5. Judge reads evidence timeline and owner routing.
6. Judge opens War Room Packet.
7. Judge sees README and public GitHub match the demo behavior.

## Refresh Procedure
Run before final judging if using a Cloudflare Quick Tunnel:

```bash
python scripts/refresh_public_demo.py --update-hf-space --smoke-space
```

Quick Tunnel URLs are temporary. A named Cloudflare Tunnel with a stable hostname is preferred for final judging if a Cloudflare-managed domain is available.
