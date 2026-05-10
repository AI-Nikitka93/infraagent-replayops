# Working Execution Plan

Status legend: `PLANNED`, `IN_PROGRESS`, `DONE`, `BLOCKED`, `CANCELLED`.

| Step | Status | Owner Role | Output |
|---|---|---|---|
| 1. Read local memory and P-18 topology | DONE | P-MAS | Existing `docs/research-report.md` used as topology source |
| 2. Verify official LangGraph patterns | DONE | P-MAS | Official docs checked for `StateGraph`, `MessagesState`, conditional edges, persistence, recursion limits |
| 3. Create missing project memory kit | DONE | P-MAS | `AGENTS.md`, `EXECUTION_PLAN.md`, `docs/STATE.md`, `docs/state.json`, supporting docs |
| 4. Design graph architecture | DONE | P-MAS | `docs/architecture.md`, `docs/state_graph.md` |
| 5. Create inference runtime scripts | DONE | P-95X | `.env.example`, `inference_config.yaml`, `start_vllm_rocm.sh`, `start_tunnel.sh` |
| 6. Implement FastAPI/LangGraph backend | DONE | P-AGENTX | `requirements.txt`, `tools.py`, `agent.py`, `server.py`, `tests/test_backend_contracts.py` |
| 7. Build thin Hugging Face Spaces UI | DONE | P-FRONTEND | `app.py`, `requirements-ui.txt`, `tests/test_ui_contracts.py` |
| 8. Competitive review and pivot decision | DONE | Strategy agent | `docs/COMPETITION_REVIEW.md` |
| 9. Upgrade InfraAgent into evidence-first ReplayOps demo | DONE | P-AGENTX + P-FRONTEND | Evidence graph, runtime proof, eval scorecard, War Room packet |
| 10. Local ReplayOps verification | DONE | QA | pytest, graph smoke, FastAPI TestClient, Playwright UI screenshot |
| 11. Submission hardening to maximum local package | DONE | Strategy + Full-stack | Runtime truth contract, readiness gate, market pain map, submission copy, demo script, slide outline, MIT license |
| 12. Public submission package publication | DONE | Deployment agent | Public GitHub, HF Space, app URL, video artifact, slide artifact, public tunnel smoke |
| 13. End-to-end AMD VM rehearsal | BLOCKED | Deployment agent | No AMD Developer Cloud SSH/host/runtime is present in the current environment; local fallback public demo is refreshed and verified |
| 14. Stable public demo refresh workflow | DONE | Deployment agent | `scripts/refresh_public_demo.py`, current tunnel, HF Space secrets, public API smoke, HF Space smoke |
| 15. Contest truth and AMD proof hardening | DONE | QA / Full-stack | `docs/contest_truth.json`, `/api/readiness` contest truth, `scripts/amd_runtime_rehearsal.py`, T001-T040 local closure without fake live proof |
| 16. ReplayOps product core and design hardening | DONE | QA / Full-stack | Six-scenario catalog, negative human-review path, stronger packet contract, operational UI, `DESIGN.md`, browser smoke |
| 17. Submission QA, public smoke, and recovery runbooks | DONE | QA / Full-stack | Curated visual assets, judge FAQ, Build in Public notes, claim/security audits, public smoke script, recovery and judging-day runbooks |
| 18. Strict final submission gate | DONE | QA / Full-stack | `live_vllm` requires AMD device proof, readiness requires `Qwen critic: ok`, and `scripts/final_submission_gate.py` returns `GO_SUBMIT` only when tests, audits, AMD proof, public smoke, and readiness all pass |

Current active step: local package and final submit gate are hardened. Winning-tier readiness remains blocked on real AMD Developer Cloud MI300X access, AMD device proof, live vLLM/Qwen, `Qwen critic: ok`, final AMD screenshot/status/readiness artifact, and `/api/readiness` returning `GO`.
