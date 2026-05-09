# InfraAgent State

<!-- STATE_JSON_START -->
```json
{
  "current_goal": "Prepare InfraAgent ReplayOps for a maximum-signal AMD Developer Hackathon submission.",
  "current_task": "Local product and submission package are hardened; external submission still requires AMD MI300X live proof, public GitHub, HF Space, video, and slides.",
  "status": "LOCAL_SUBMISSION_PACKAGE_VERIFIED_BLOCKED_ON_EXTERNAL_PROOF",
  "active_step": "Runtime truth contract, business lens, readiness gate, market pain map, and submission package verified locally",
  "next_step": "Run on AMD Developer Cloud MI300X, publish public GitHub and HF Space, record video, publish slide deck, set external URLs, then verify /api/readiness returns GO.",
  "blockers": [],
  "artifacts": [
    "docs/research-report.md",
    "docs/architecture.md",
    "docs/state_graph.md",
    ".env.example",
    "inference_config.yaml",
    "start_vllm_rocm.sh",
    "start_tunnel.sh",
    "requirements.txt",
    "tools.py",
    "agent.py",
    "server.py",
    "tests/test_backend_contracts.py",
    "app.py",
    "requirements-ui.txt",
    "tests/test_ui_contracts.py",
    ".runtime/infraagent-ui-desktop.png",
    ".runtime/infraagent-ui-mobile.png",
    "docs/COMPETITION_REVIEW.md",
    "infraagent-replayops-final.png",
    "infraagent-replayops-desktop.png",
    "infraagent-replayops-verify.png",
    "infraagent-replayops-public-tunnel.png",
    "LICENSE",
    "SUBMISSION.md",
    "DEMO_SCRIPT.md",
    "SLIDES.md",
    "HACKATHON_READINESS.md",
    "docs/market-pain-map.md",
    ".gitignore"
  ],
  "updated_at": "2026-05-09 03:55 Europe/Minsk"
}
```
<!-- STATE_JSON_END -->

## Human Summary
InfraAgent has been upgraded into InfraAgent ReplayOps: evidence-verified incident triage with runtime proof, agent trace, evidence timeline, deterministic eval scorecard, Business / Ownership Lens, Submission Readiness gate, and War Room Packet export. Hugging Face Spaces remains a thin UI and uses polling through Cloudflare Tunnel.

## Active Architecture Choice
Use a deterministic pipeline with a single verification gate:

Alert Ingestor -> Investigator -> Root Cause Analyst -> Runbook Generator -> Verification Gate.

The gate may request one extra investigation round, but the graph ends with either `ready`, `needs_human_review`, or `failed` before `max_steps` is exceeded.

## Current Blockers
No local code blocker. Local API, local UI, public Cloudflare Quick Tunnel rehearsal, runtime truth contract, readiness gate, and submission package are verified. Remaining blockers are external submission blockers: AMD Developer Cloud MI300X live Qwen/vLLM proof, public GitHub URL, HF Space URL, video URL, and slide deck URL.

## Local Running Services
- FastAPI: `http://127.0.0.1:8010` with process `server.py`.
- Gradio UI: `http://127.0.0.1:7860` with process `app.py`.
- Public API tunnel: `https://cst-stack-bit-yeah.trycloudflare.com` via local `cloudflared --protocol http2`.
- Local demo auth: `PUBLIC_API_KEY=test-key`, `INFRAAGENT_API_KEY=test-key`.

## Latest Verification
- `python -m compileall agent.py tools.py server.py app.py` passed.
- `pytest -q` passed: 10 tests.
- `bash -n start_vllm_rocm.sh` and `bash -n start_tunnel.sh` passed.
- 5 graph scenarios reached `ready`.
- FastAPI TestClient reached `ready`, score `100`, War Room Packet generated.
- Playwright opened the Gradio UI, clicked `Start Evidence Triage`, and observed `READY`, score `100/100`, evidence timeline, node trace, root cause, runbook, and War Room Packet.
- Screenshot: `infraagent-replayops-verify.png`.
- Docker CLI exists, but Docker daemon is not running locally.
- Docker daemon was started, but ROCm device mapping fails: Docker cannot add `/dev/kfd` because the device does not exist locally.
- `cloudflared` was installed locally to `.runtime/bin/cloudflared.exe`.
- Quick Tunnel over default QUIC created a URL but public access returned 530 due QUIC handshake timeouts.
- Quick Tunnel over `--protocol http2` worked: `/health` returned ok and `/api/triage` reached `ready`, score `100`, packet `true`.
- UI was restarted with `INFRAAGENT_API_BASE=https://cst-stack-bit-yeah.trycloudflare.com` and completed the browser flow to `READY`, score `100/100`.
- Screenshot: `infraagent-replayops-public-tunnel.png`.
- Market-pain research captured in `docs/market-pain-map.md` for alert fatigue, tool sprawl, ownership, MTTR, and agentic observability.
- Runtime proof now separates target AMD stack from observed backend mode and labels fallback honestly.
- `/api/readiness` returns strict local/external readiness and lists formal blockers.
- Browser check on updated local UI reached `READY`, `Score: 100/100`, with Business / Ownership Lens and Submission Readiness visible.
- `pytest -q` passed: 16 tests.

## Next Step
Run end-to-end AMD VM rehearsal: start vLLM, start FastAPI, open Cloudflare Tunnel with `CLOUDFLARED_PROTOCOL=http2`, set `INFRAAGENT_API_BASE` and `INFRAAGENT_API_KEY` in HF Spaces, and verify the UI reaches `ready` with `runtime_proof.backend_mode=live_vllm` and Qwen critic `ok`. Then publish public GitHub, HF Space, video, and slide deck, set URLs, and verify `/api/readiness` returns `GO`.
