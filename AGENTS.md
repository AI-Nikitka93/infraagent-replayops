# InfraAgent Hackathon Workspace

Goal: design and build InfraAgent for the AMD Developer Hackathon: a LangGraph incident-triage agent system running on AMD Developer Cloud beside local vLLM/Qwen2.5-72B, with a thin Hugging Face Spaces UI over a polling API.

Current stack decisions:
- Runtime: AMD Developer Cloud MI300X instance.
- Model server: local vLLM OpenAI-compatible API with Qwen2.5-72B-Instruct on ROCm.
- Agent service: FastAPI plus LangGraph on the same AMD VM.
- Public access: Cloudflare Tunnel to the FastAPI service.
- UI: Hugging Face Spaces calls the public HTTPS API and polls run status.

Project memory:
- Human state: `docs/STATE.md`
- Machine state: `docs/state.json`, generated from `docs/STATE.md` by `sync_state.py`
- Working plan: `docs/EXEC_PLAN.md`
- Root long plan: `EXECUTION_PLAN.md`
- Decisions: `docs/DECISIONS.md`
- History: `docs/PROJECT_HISTORY.md`
- Architecture artifacts: `docs/architecture.md`, `docs/state_graph.md`

Operating rules:
- Read this file, `docs/STATE.md`, `docs/state.json`, `docs/EXEC_PLAN.md`, recent `docs/PROJECT_HISTORY.md`, and `docs/DECISIONS.md` before changing the project.
- Keep the graph small for the hackathon demo: no more than five LangGraph nodes.
- Use polling for the external UI contract. Do not design WebSocket or SSE surfaces for the public path.
- Expose LangGraph/FastAPI through the tunnel, not raw vLLM.
- Mock production observability tools with deterministic JSON or JSONL fixtures for the demo.
