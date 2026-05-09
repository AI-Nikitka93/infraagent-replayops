# InfraAgent ReplayOps

Evidence-verified incident triage for the AMD Developer Hackathon.

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
- `LICENSE` - MIT license.
- Public GitHub: https://github.com/AI-Nikitka93/infraagent-replayops
- Hugging Face Space: https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops
- Demo app: https://clendeningantonettie-infraagent-replayops.hf.space
- Video artifact: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-demo.mp4
- Slide deck artifact: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-slides.pdf

Readiness endpoint:

```bash
curl http://127.0.0.1:8010/api/readiness
```

The readiness gate is intentionally strict. Local files can pass while external submission remains `NO_GO_UNTIL_BLOCKERS_CLOSE` until public GitHub, HF Space, video, slides, and live AMD/Qwen proof are filled.

## Verification Run

Local verification completed on 2026-05-09:

```bash
python -m compileall agent.py tools.py server.py app.py
pytest -q
```

Observed:

- `10 passed`.
- Graph smoke reached `ready`.
- Eval score: `100/100`.
- Evidence records: `9`.
- Node traces: `5`.
- War Room Packet generated.
- Playwright opened the Gradio UI and completed a visible run.

## Remaining Rehearsal Step

The local environment did not have live vLLM/Qwen running. Runtime proof therefore correctly falls back to `fallback_without_live_vllm`, and Qwen critic is `skipped`.

On the AMD MI300X VM, the final rehearsal must verify:

- vLLM `/v1/models` is healthy.
- Runtime proof shows `live_vllm`.
- Qwen critic status becomes `ok`.
- HF Spaces can poll the Cloudflare Tunnel URL.
- `/api/readiness` has no formal blockers after external URLs are configured.
