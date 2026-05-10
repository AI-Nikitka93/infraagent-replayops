# InfraAgent ReplayOps

Evidence-verified incident triage for the AMD Developer Hackathon.

Current judge-facing gap statement: fallback demo verified, live AMD/Qwen proof pending.

InfraAgent ReplayOps is a bounded LangGraph system that turns an incident alert into a replayable War Room Packet:

1. Normalize alert context.
2. Collect mock observability evidence with stable evidence IDs.
3. Rank a root cause with evidence citations and optional Qwen critique.
4. Generate a human-approved recovery runbook.
5. Verify the result with a deterministic eval scorecard.
6. Expose the whole run through a polling API and Hugging Face Spaces UI.

The judge-facing difference: InfraAgent does not ask judges to trust a final paragraph. It shows the evidence IDs, node trace, ownership routing, business risk, runtime truth, scorecard, and packet that produced the answer.

## Why This Is Not A Simple RAG Demo

The system does not retrieve documents and answer a question. It runs a stateful incident workflow with:

- LangGraph node orchestration.
- Tool-call evidence collection.
- Runtime proof for local vLLM/Qwen.
- Evidence timeline.
- Node trace and loop protection.
- Root-cause citation checks.
- Runbook safety checks.
- War Room Packet export with audit seal.
- Business / ownership lens for noisy incident queues.
- Runtime truth contract that separates the target AMD stack from the observed backend mode.

## Not A Generic Incident Assistant

Generic incident assistants summarize alerts. InfraAgent ReplayOps produces a verifiable handoff: evidence IDs, rejected alternatives, owner routing, scorecard, runtime truth, and an audit-sealed packet. The product surface is built for incident command, not chat.

## Why AMD Matters

The target runtime is local Qwen2.5-72B-Instruct on AMD Developer Cloud MI300X through ROCm and vLLM. AMD matters because the judge can see whether the large model is served locally beside the agent service instead of through an external API. The project keeps this honest by showing `live_vllm` only when the configured vLLM endpoint responds and Qwen critique runs.

## Judge FAQ

See `docs/JUDGE_FAQ.md` for the concise distinction between what is live, what is deterministic fixture data, what requires human approval, and what does not count as AMD proof.

## Market Pain Fit

Current SRE and incident-response pain is not a lack of dashboards. The hard parts are alert fatigue, tool sprawl, unclear ownership, slow MTTR, and agent governance. InfraAgent ReplayOps maps those pains to visible product surfaces:

- alert fatigue -> one ranked evidence packet instead of another alert stream;
- tool sprawl -> metrics, logs, deploy events, traces, and topology in one timeline;
- unclear ownership -> owner routing and business risk in every run;
- slow MTTR -> bounded graph and time-to-insight lens;
- agent governance -> node traces, audit seal, and no automatic remediation.

See `docs/market-pain-map.md` for the source-backed pain map checked on 2026-05-09.

## Local Backend

Install backend requirements:

```bash
pip install -r requirements.txt
```

Set local secrets:

```bash
cp .env.example .env
# Replace PUBLIC_API_KEY and VLLM_API_KEY with openssl rand -hex 32 values.
```

Run API:

```bash
python server.py
```

The API listens on `127.0.0.1:8010`.

## Local UI

Install UI requirements:

```bash
pip install -r requirements-ui.txt
```

Run UI against the local API:

```bash
export INFRAAGENT_API_BASE=http://127.0.0.1:8010
export INFRAAGENT_API_KEY=<PUBLIC_API_KEY>
python app.py
```

For Hugging Face Spaces, set these as Space secrets:

- `INFRAAGENT_API_BASE`
- `INFRAAGENT_API_KEY`

Refresh the judge-facing public path after starting the local API:

```bash
python scripts/refresh_public_demo.py --update-hf-space --smoke-space
```

The script starts a fresh Cloudflare Quick Tunnel, updates the HF Space secrets, verifies the public API, runs the HF Space through its Gradio API, and writes `.runtime/public_demo_status.json`. Quick Tunnel URLs are temporary, so run this before final judging or switch to a named Cloudflare Tunnel with a stable hostname.

## AMD VM Runtime

Start Qwen2.5-72B on ROCm/vLLM:

```bash
bash start_vllm_rocm.sh
```

Start the Cloudflare Quick Tunnel to the FastAPI service:

```bash
bash start_tunnel.sh
```

The tunnel should expose FastAPI on port `8010`, not raw vLLM on port `8000`.

## Runtime Truth Contract

The UI and API use three explicit runtime modes:

- `live_vllm`: the configured vLLM `/v1/models` endpoint responded and Qwen critique can run.
- `runtime_unhealthy`: the endpoint responded but did not pass health checks.
- `fallback_without_live_vllm`: the graph, evidence flow, scorecard, and packet work, but Qwen critique is skipped.

Do not claim live AMD/Qwen proof unless the demo visibly shows `runtime_proof.backend_mode=live_vllm`.

## Submission Package

Local package files:

- `SUBMISSION.md` - lablab submission copy draft.
- `DEMO_SCRIPT.md` - 75-90 second video script.
- `SLIDES.md` - slide outline.
- `HACKATHON_READINESS.md` - strict pre-submission gate.
- `docs/JUDGE_FAQ.md` - judge-facing truth map.
- `docs/BUILD_IN_PUBLIC.md` - public technical updates and friction notes.
- `docs/RECOVERY_CHECKLIST.md` - manual recovery path.
- `docs/JUDGING_DAY_RUNBOOK.md` - launch, smoke, screenshot, and stop-condition order.
- `submission_assets/visual_assets_manifest.json` - curated visual asset manifest.
- `LICENSE` - MIT license.
- Public GitHub: https://github.com/AI-Nikitka93/infraagent-replayops
- Hugging Face Space: https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops
- Demo app: https://clendeningantonettie-infraagent-replayops.hf.space
- Video artifact: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-demo.mp4
- Slide deck artifact: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-slides.pdf
- Current refreshed public API tunnel: https://seattle-rock-south-bath.trycloudflare.com

Official contest truth snapshot:

- `docs/contest_truth.json` records the 2026-05-10 rules/freshness pass, selected Track 1 scope, submission fields, judging criteria, prize-scope signals, and freshness dependencies.

Artifacts to refresh after live AMD proof:

- `README.md`, `SUBMISSION.md`, `HACKATHON_READINESS.md`, `docs/STATE.md`, `docs/state.json`, `docs/EXEC_PLAN.md`, and `docs/PROJECT_HISTORY.md`.
- Demo video, slide deck, final screenshot, `.runtime/amd_live_proof.json`, and `.runtime/public_demo_status.json`.
- HF Space secrets if the AMD-backed public API URL changes.

Stable public access plan:

- Preferred final path: named Cloudflare Tunnel on a stable hostname that targets FastAPI on `8010`.
- Acceptable fallback path: Quick Tunnel refreshed immediately before judging through `scripts/refresh_public_demo.py`.
- Never expose raw vLLM on `8000` through the public tunnel.

Contingency Wording:

If final AMD runtime is unavailable, say: "The public ReplayOps workflow is verified in fallback mode, but the winning-tier AMD proof is not complete because the public run does not show `live_vllm` and `Qwen critic: ok`."

Readiness endpoint:

```bash
curl http://127.0.0.1:8010/api/readiness
```

The readiness gate is intentionally strict. Local files can pass while external submission remains `NO_GO_UNTIL_BLOCKERS_CLOSE` until public GitHub, HF Space, video, slides, and live AMD/Qwen proof are filled.

Final blocking gate before submission:

```bash
python scripts/final_submission_gate.py --api-base "$INFRAAGENT_API_BASE" --api-key-file .runtime/local_api_key.txt --space-host https://clendeningantonettie-infraagent-replayops.hf.space
```

Submit only when this returns `GO_SUBMIT`. It runs tests, compile checks, claim/security/visual audits, AMD runtime rehearsal, public smoke, and blocks if `live_vllm`, `amd_runtime_evidence.ok=true`, `Qwen critic: ok`, or public readiness `GO` is missing.

## Verification Run

Local verification completed on 2026-05-10:

```bash
python -m compileall agent.py tools.py server.py app.py scripts\amd_runtime_rehearsal.py scripts\refresh_public_demo.py scripts\public_smoke.py scripts\security_privacy_audit.py scripts\claim_audit.py scripts\visual_asset_audit.py scripts\final_submission_gate.py
pytest -q
python scripts\security_privacy_audit.py
```

Observed:

- `36 passed`.
- Six-scenario graph smoke reached five `ready` runs and one expected `needs_human_review` negative case.
- Eval score: `100/100`.
- Evidence records: `9`.
- Node traces: `5`.
- War Room Packet generated.
- Playwright opened the Gradio UI and completed a visible run.
- HF Space public Gradio API smoke reached `READY`, `Score: 100/100`, `fallback_without_live_vllm`, and no network error after Space secrets were refreshed.
- Security/privacy audit found no token patterns in release files or git history.
- Public readiness currently reports local `7/7`, external `4/7`, with blockers `live_vllm`, `amd_runtime_proof`, and `qwen_critic_ok`.
- `scripts/final_submission_gate.py` correctly returns `NO_GO_UNTIL_BLOCKERS_CLOSE` in this non-AMD environment.

## Remaining Rehearsal Step

The local environment did not have live vLLM/Qwen running. Runtime proof therefore correctly falls back to `fallback_without_live_vllm`, and Qwen critic is `skipped`.

On the AMD MI300X VM, the final rehearsal must verify:

- vLLM `/v1/models` is healthy.
- Runtime proof shows `live_vllm`.
- Qwen critic status becomes `ok`.
- HF Spaces can poll the Cloudflare Tunnel URL.
- `/api/readiness` has no formal blockers after external URLs are configured.

Run the AMD proof harness on the AMD VM:

```bash
python scripts/amd_runtime_rehearsal.py --public-api-base "$INFRAAGENT_API_BASE"
```
