# Build in Public Technical Notes

## Update 1 - Evidence-First ReplayOps

InfraAgent ReplayOps focuses on incident response proof rather than generic chat. The system uses a five-node LangGraph workflow, deterministic observability fixtures, stable evidence IDs, and a War Room Packet so judges can replay the same case and verify the result.

Suggested tags: `#AMDDeveloperHackathon`, `#lablab`, `#LangGraph`, `#SRE`, `#AgenticAI`, `#ROCm`.

## Update 2 - Runtime Truth on AMD

The runtime contract separates target stack from observed behavior. The target is AMD Developer Cloud MI300X with ROCm, local vLLM, and Qwen2.5-72B-Instruct. If the AMD runtime is not reachable, the UI says `fallback_without_live_vllm` and skips Qwen critique instead of pretending that the model ran.

Suggested tags: `#AMD`, `#MI300X`, `#ROCm`, `#vLLM`, `#Qwen`, `#HuggingFace`.

## Technical Feedback To Include

- ROCm: strong fit for local large-model serving, but the demo must prove device access with `/dev/kfd`, `/dev/dri`, and `rocminfo`.
- AMD Developer Cloud: the submission should show a real public run, not only target architecture.
- vLLM/Qwen: expose `/v1/models` only to the agent service; never tunnel raw vLLM publicly.
- Cloudflare Tunnel: use a named tunnel for judging when available; Quick Tunnel is acceptable only with a last-minute refresh and smoke.
- Hugging Face Spaces: keep API keys in Space secrets, not repo variables.

## Do Not Post

- Private API keys, tunnel credentials, hostnames that reveal private infrastructure, local `.runtime` paths, or screenshots that hide fallback/live truth.
