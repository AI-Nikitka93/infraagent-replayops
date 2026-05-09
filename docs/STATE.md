# InfraAgent State

<!-- STATE_JSON_START -->
```json
{
  "current_goal": "Prepare InfraAgent ReplayOps for a maximum-signal AMD Developer Hackathon submission.",
  "current_task": "Public fallback demo path has been refreshed and verified through a live Cloudflare Tunnel plus HF Space secrets; external submission still requires AMD MI300X live Qwen/vLLM proof.",
  "status": "PUBLIC_FALLBACK_DEMO_VERIFIED_BLOCKED_ON_AMD_LIVE_VLLM",
  "active_step": "HF Space reaches READY with score 100/100 through the current tunnel; readiness remains 4/5 external with live_vllm as the only blocker",
  "next_step": "Obtain or open the AMD Developer Cloud MI300X VM, start vLLM/Qwen, point the same FastAPI/HF Space contract at the AMD tunnel, and verify /api/readiness returns GO with runtime_proof.backend_mode=live_vllm.",
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
    "scripts/refresh_public_demo.py",
    "docs/market-pain-map.md",
    ".gitignore",
    "submission_assets/infraagent-replayops-demo.mp4",
    "submission_assets/infraagent-replayops-slides.pdf"
  ],
  "updated_at": "2026-05-10 02:29 Europe/Minsk"
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
No local code blocker. Public GitHub, HF Space, application URL, video artifact, slide artifact, refreshed public Cloudflare Tunnel, runtime truth contract, readiness gate, and submission package are verified in fallback mode. Remaining blocker: AMD Developer Cloud MI300X live Qwen/vLLM proof. Current environment has no discovered AMD Developer Cloud SSH/host/runtime path.

## Local Running Services
- FastAPI: `http://127.0.0.1:8010` with process `server.py`.
- Gradio UI: `http://127.0.0.1:7860` with process `app.py`.
- Public GitHub: `https://github.com/AI-Nikitka93/infraagent-replayops`.
- Hugging Face Space: `https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops`.
- Demo app: `https://clendeningantonettie-infraagent-replayops.hf.space`.
- Public API tunnel: `https://seattle-rock-south-bath.trycloudflare.com` via local `cloudflared --protocol http2`.
- Local demo auth: generated in `.runtime/local_api_key.txt` and mirrored into the HF Space secret.

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
- Public GitHub repo created and pushed: `https://github.com/AI-Nikitka93/infraagent-replayops`, commit `71189fb`.
- HF Space created under `clendeningantonettie/infraagent-replayops`, metadata fixed after the first `CONFIG_ERROR`, and runtime reached `RUNNING`.
- HF Space browser smoke reached `READY`, showed `fallback_without_live_vllm`, and rendered War Room Packet.
- Public API tunnel smoke reached `ready`, score `100/100`, runtime `fallback_without_live_vllm`, Qwen critic `skipped`, packet `true`.
- Live `/api/readiness` now reports local `7/7`, external `4/5`, formal blockers `["live_vllm"]`.
- Slide artifact and video artifact are public through GitHub raw URLs.
- Refreshed public tunnel `https://seattle-rock-south-bath.trycloudflare.com` reached `/health`, `/api/readiness`, `/api/triage`, and `/api/status/{run_id}`.
- HF Space secrets were updated to the refreshed tunnel and the public Gradio API run reached `READY`, `Score: 100/100`, `fallback_without_live_vllm`, visible Submission Readiness, and no network error.
- Added `scripts/refresh_public_demo.py` to make the tunnel + HF secret + public smoke workflow reproducible before judging.
- Searched the local repo, environment, and SSH inventory for AMD Developer Cloud/MI300X access. No usable AMD VM host, SSH config, or live vLLM endpoint was found in the current environment.

## Next Step
Run end-to-end AMD VM rehearsal once AMD Developer Cloud access is available: start vLLM, start FastAPI, open Cloudflare Tunnel with `CLOUDFLARED_PROTOCOL=http2`, update `INFRAAGENT_API_BASE` and `INFRAAGENT_API_KEY` in HF Spaces if the AMD tunnel URL changes, and verify the UI reaches `ready` with `runtime_proof.backend_mode=live_vllm` and Qwen critic `ok`. Then verify `/api/readiness` returns `GO`.
